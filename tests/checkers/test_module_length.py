import base64
import collections
import datetime
import itertools
import json
import re
import struct

from pycassa import types
from pycassa.util import convert_uuid_to_time
from pycassa.system_manager import ASCII_TYPE, DATE_TYPE, FLOAT_TYPE, UTF8_TYPE
from pylons import request
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.i18n import _, N_
from thrift.protocol.TProtocol import TProtocolException
from thrift.Thrift import TApplicationException
from thrift.transport.TTransport import TTransportException

from r2.config import feature
from r2.lib.db.thing import Thing, Relation, NotFound
from account import (
    Account,
    FakeAccount,
    QuarantinedSubredditOptInsByAccount,
)
from printable import Printable
from r2.lib.db.userrel import UserRel, MigratingUserRel
from r2.lib.db.operators import lower, or_, and_, not_, desc
from r2.lib.errors import RedditError
from r2.lib.geoip import get_request_location
from r2.lib.memoize import memoize
from r2.lib.permissions import ModeratorPermissionSet
from r2.lib.utils import (
    UrlParser,
    in_chunks,
    summarize_markdown,
    timeago,
    to36,
    tup,
    unicode_title_to_ascii,
)
from r2.lib.cache import MemcachedError
from r2.lib.sgm import sgm
from r2.lib.strings import strings, Score
from r2.lib.filters import _force_unicode
from r2.lib.db import tdb_cassandra
from r2.lib.db.tdb_sql import CreationError
from r2.models.wiki import WikiPage, ImagesByWikiPage
from r2.models.trylater import TryLater, TryLaterBySubject
from r2.lib.merge import ConflictException
from r2.lib.cache import CL_ONE
from r2.lib import hooks
from r2.models.query_cache import MergedCachedQuery
from r2.models.rules import SubredditRules
import pycassa

from r2.models.keyvalue import NamedGlobals
from r2.models.wiki import WikiPage
import os.path
import random


class Subreddit(Thing, Printable, BaseSite):
    _cache = g.thingcache

    # Note: As of 2010/03/18, nothing actually overrides the static_path
    # attribute, even on a cname. So c.site.static_path should always be
    # the same as g.static_path.
    _defaults = dict(BaseSite._defaults,
        stylesheet_url="",
        stylesheet_url_http="",
        stylesheet_url_https="",
        header_size=None,
        allow_top=False, # overridden in "_new"
        reported=0,
        valid_votes=0,
        show_media=False,
        show_media_preview=True,
        domain=None,
        suggested_comment_sort=None,
        wikimode="disabled",
        wiki_edit_karma=100,
        wiki_edit_age=0,
        over_18=False,
        exclude_banned_modqueue=False,
        mod_actions=0,
        # do we allow self-posts, links only, or any?
        link_type='any', # one of ('link', 'self', 'any')
        sticky_fullnames=None,
        submit_link_label='',
        submit_text_label='',
        comment_score_hide_mins=0,
        flair_enabled=True,
        flair_position='right', # one of ('left', 'right')
        link_flair_position='', # one of ('', 'left', 'right')
        flair_self_assign_enabled=False,
        link_flair_self_assign_enabled=False,
        use_quotas=True,
        description="",
        public_description="",
        submit_text="",
        public_traffic=False,
        spam_links='high',
        spam_selfposts='high',
        spam_comments='low',
        archive_age=g.ARCHIVE_AGE,
        gilding_server_seconds=0,
        contest_mode_upvotes_only=False,
        collapse_deleted_comments=False,
        icon_img='',
        icon_size=None,
        banner_img='',
        banner_size=None,
        key_color='',
        hide_ads=False,
        ban_count=0,
        quarantine=False,
    )

    # special attributes that shouldn't set Thing data attributes because they
    # have special setters that set other data attributes
    _derived_attrs = (
        'related_subreddits',
    )

    _essentials = ('type', 'name', 'lang')
    _data_int_props = Thing._data_int_props + ('mod_actions', 'reported',
                                               'wiki_edit_karma', 'wiki_edit_age',
                                               'gilding_server_seconds',
                                               'ban_count')

    sr_limit = 50
    gold_limit = 100
    DEFAULT_LIMIT = object()

    ICON_EXACT_SIZE = (256, 256)
    BANNER_MIN_SIZE = (640, 192)
    BANNER_MAX_SIZE = (1280, 384)
    BANNER_ASPECT_RATIO = 10.0 / 3

    valid_types = {
        'archived',
        'employees_only',
        'gold_only',
        'gold_restricted',
        'private',
        'public',
        'restricted',
    }

    # this holds the subreddit types where content is not accessible
    # unless you are a contributor or mod
    private_types = {
        'employees_only',
        'gold_only',
        'private',
    }

    KEY_COLORS = collections.OrderedDict([
        ('#ea0027', N_('red')),
        ('#ff4500', N_('orangered')),
        ('#ff8717', N_('orange')),
        ('#ffb000', N_('mango')),
        ('#94e044', N_('lime')),
        ('#46d160', N_('green')),
        ('#0dd3bb', N_('mint')),
        ('#25b79f', N_('teal')),
        ('#24a0ed', N_('blue')),
        ('#0079d3', N_('alien blue')),
        ('#ff66ac', N_('pink')),
        ('#7e53c1', N_('purple')),
        ('#ddbd37', N_('gold')),
        ('#a06a42', N_('brown')),
        ('#efefed', N_('pale grey')),
        ('#a5a4a4', N_('grey')),
        ('#545452', N_('dark grey')),
        ('#222222', N_('semi black')),
    ])
    ACCENT_COLORS = (
        '#f44336', # red
        '#9c27b0', # purple
        '#3f51b5', # indigo
        '#03a9f4', # light blue
        '#009688', # teal
        '#8bc34a', # light green
        '#ffeb3b', # yellow
        '#ff9800', # orange
        '#795548', # brown
        '#607d8b', # blue grey
        '#e91e63', # pink
        '#673ab7', # deep purple
        '#2196f3', # blue
        '#00bcd4', # cyan
        '#4caf50', # green
        '#cddc39', # lime
        '#ffc107', # amber
        '#ff5722', # deep orange
        '#9e9e9e', # grey
    )

    MAX_STICKIES = 2

    @classmethod
    def _cache_prefix(cls):
        return "sr:"

    def __setattr__(self, attr, val, make_dirty=True):
        if attr in self._derived_attrs:
            object.__setattr__(self, attr, val)
        else:
            Thing.__setattr__(self, attr, val, make_dirty=make_dirty)

    # note: for purposely unrenderable reddits (like promos) set author_id = -1
    @classmethod
    def _new(cls, name, title, author_id, ip, lang = g.lang, type = 'public',
             over_18 = False, **kw):
        if not cls.is_valid_name(name):
            raise ValueError("bad subreddit name")
        with g.make_lock("create_sr", 'create_sr_' + name.lower()):
            try:
                sr = Subreddit._by_name(name)
                raise SubredditExists
            except NotFound:
                if "allow_top" not in kw:
                    kw['allow_top'] = True
                sr = Subreddit(name = name,
                               title = title,
                               lang = lang,
                               type = type,
                               over_18 = over_18,
                               author_id = author_id,
                               ip = ip,
                               **kw)
                sr._commit()

                #clear cache
                Subreddit._by_name(name, _update = True)
                return sr

    @classmethod
    def is_valid_name(cls, name, allow_language_srs=False, allow_time_srs=False,
                      allow_reddit_dot_com=False):
        if not name:
            return False

        if allow_reddit_dot_com and name.lower() == "reddit.com":
            return True

        valid = bool(subreddit_rx.match(name))

        if not valid and allow_language_srs:
            valid = bool(language_subreddit_rx.match(name))

        if not valid and allow_time_srs:
            valid = bool(time_subreddit_rx.match(name))

        return valid

    _specials = {}

    SRNAME_NOTFOUND = "n"
    SRNAME_TTL = int(datetime.timedelta(hours=12).total_seconds())

    @classmethod
    def _by_name(cls, names, stale=False, _update = False):
        '''
        Usages:
        1. Subreddit._by_name('funny') # single sr name
        Searches for a single subreddit. Returns a single Subreddit object or
        raises NotFound if the subreddit doesn't exist.
        2. Subreddit._by_name(['aww','iama']) # list of sr names
        Searches for a list of subreddits. Returns a dict mapping srnames to
        Subreddit objects. Items that were not found are ommitted from the dict.
        If no items are found, an empty dict is returned.
        '''
        names, single = tup(names, True)

        to_fetch = {}
        ret = {}

        for name in names:
            try:
                ascii_only = str(name.decode("ascii", errors="ignore"))
            except UnicodeEncodeError:
                continue

            lname = ascii_only.lower()

            if lname in cls._specials:
                ret[name] = cls._specials[lname]
            else:
                valid_name = cls.is_valid_name(lname, allow_language_srs=True,
                                               allow_time_srs=True,
                                               allow_reddit_dot_com=True)
                if valid_name:
                    to_fetch[lname] = name
                else:
                    g.log.debug("Subreddit._by_name() ignoring invalid srname: %s", lname)

        if to_fetch:
            if not _update:
                srids_by_name = g.gencache.get_multi(
                    to_fetch.keys(), prefix='srid:', stale=True)
            else:
                srids_by_name = {}

            missing_srnames = set(to_fetch.keys()) - set(srids_by_name.keys())
            if missing_srnames:
                for srnames in in_chunks(missing_srnames, size=10):
                    q = cls._query(
                        lower(cls.c.name) == srnames,
                        cls.c._spam == (True, False),
                        # subreddits can't actually be deleted, but the combo
                        # of allowing for deletion and turning on optimize_rules
                        # gets rid of an unnecessary join on the thing table
                        cls.c._deleted == (True, False),
                        limit=len(srnames),
                        optimize_rules=True,
                        data=True,
                    )
                    with g.stats.get_timer('subreddit_by_name'):
                        fetched = {sr.name.lower(): sr._id for sr in q}
                    srids_by_name.update(fetched)

                    still_missing = set(srnames) - set(fetched)
                    fetched.update((name, cls.SRNAME_NOTFOUND) for name in still_missing)
                    try:
                        g.gencache.set_multi(
                            keys=fetched,
                            prefix='srid:',
                            time=cls.SRNAME_TTL,
                        )
                    except MemcachedError:
                        pass

            srs = {}
            srids = [v for v in srids_by_name.itervalues() if v != cls.SRNAME_NOTFOUND]
            if srids:
                srs = cls._byID(srids, data=True, return_dict=False, stale=stale)

            for sr in srs:
                ret[to_fetch[sr.name.lower()]] = sr

        if ret and single:
            return ret.values()[0]
        elif not ret and single:
            raise NotFound('Subreddit %s' % name)
        else:
            return ret

    @classmethod
    @memoize('subreddit._by_domain')
    def _by_domain_cache(cls, name):
        q = cls._query(cls.c.domain == name,
                       limit = 1)
        l = list(q)
        if l:
            return l[0]._id

    @classmethod
    def _by_domain(cls, domain, _update = False):
        sr_id = cls._by_domain_cache(_force_unicode(domain).lower(),
                                     _update = _update)
        if sr_id:
            return cls._byID(sr_id, True)
        else:
            return None

    @property
    def allowed_types(self):
        if self.link_type == "any":
            return set(("link", "self"))
        return set((self.link_type,))

    @property
    def allows_referrers(self):
        return self.type in {'public', 'restricted',
                             'gold_restricted', 'archived'}

    @property
    def author_slow(self):
        if self.author_id:
            return Account._byID(self.author_id, data=True)
        else:
            return None

    def add_moderator(self, user, **kwargs):
        if not user.modmsgtime:
            user.modmsgtime = False
            user._commit()

        hook = hooks.get_hook("subreddit.add_moderator")
        hook.call(subreddit=self, user=user)

        return super(Subreddit, self).add_moderator(user, **kwargs)

    def remove_moderator(self, user, **kwargs):
        hook = hooks.get_hook("subreddit.remove_moderator")
        hook.call(subreddit=self, user=user)

        ret = super(Subreddit, self).remove_moderator(user, **kwargs)

        is_mod_somewhere = bool(Subreddit.reverse_moderator_ids(user))
        if not is_mod_somewhere:
            user.modmsgtime = None
            user._commit()

        return ret

    @property
    def moderators(self):
        return self.moderator_ids()

    def moderators_with_perms(self):
        return collections.OrderedDict(
            (r._thing2_id, r.get_permissions())
            for r in self.each_moderator())

    def moderator_invites_with_perms(self):
        return collections.OrderedDict(
            (r._thing2_id, r.get_permissions())
            for r in self.each_moderator_invite())

    def fetch_stylesheet_source(self):
        try:
            return WikiPage.get(self, 'config/stylesheet')._get('content','')
        except tdb_cassandra.NotFound:
            return ""

    @property
    def prev_stylesheet(self):
        try:
            return WikiPage.get(self, 'config/stylesheet')._get('revision','')
        except tdb_cassandra.NotFound:
            return ''

    @property
    def wikibanned(self):
        return self.wikibanned_ids()

    @property
    def wikicontributor(self):
        return self.wikicontributor_ids()

    @property
    def _should_wiki(self):
        return True

    @property
    def subscribers(self):
        return self.subscriber_ids()

    @property
    def wiki_use_subreddit_karma(self):
        return True

    @property
    def hide_subscribers(self):
        return self.name.lower() in g.hide_subscribers_srs

    @property
    def hide_contributors(self):
        return self.type in {'employees_only', 'gold_only'}

    @property
    def hide_num_users_info(self):
        return self.quarantine

    @property
    def _related_multipath(self):
        return '/r/%s/m/related' % self.name.lower()

    @property
    def related_subreddits(self):
        try:
            multi = LabeledMulti._byID(self._related_multipath)
        except tdb_cassandra.NotFound:
            multi = None
        return  [sr.name for sr in multi.srs] if multi else []

    @property
    def allow_ads(self):
        return not (self.hide_ads or self.quarantine)

    @property
    def discoverable(self):
        return self.allow_top and not self.quarantine

    @property
    def community_rules(self):
        return SubredditRules.get_rules(self)

    @related_subreddits.setter
    def related_subreddits(self, related_subreddits):
        try:
            multi = LabeledMulti._byID(self._related_multipath)
        except tdb_cassandra.NotFound:
            if not related_subreddits:
                return
            multi = LabeledMulti.create(self._related_multipath, self)

        if related_subreddits:
            srs = Subreddit._by_name(related_subreddits)
            try:
                sr_props = {srs[sr_name]: {} for sr_name in related_subreddits}
            except KeyError as e:
                raise NotFound('Subreddit %s' % e.args[0])

            multi.clear_srs()
            multi.add_srs(sr_props)
            multi._commit()
        else:
            multi.delete()

    activity_contexts = (
        "logged_in",
    )
    SubredditActivity = collections.namedtuple(
        "SubredditActivity", activity_contexts)

    def record_visitor_activity(self, context, visitor_id):
        """Record a visit to this subreddit in the activity service.
        This is used to show "here now" numbers. Multiple contexts allow us
        to bucket different kinds of visitors (logged-in vs. logged-out etc.)
        :param str context: The category of visitor. Must be one of
            Subreddit.activity_contexts.
        :param str visitor_id: A unique identifier for this visitor within the
            given context.
        """
        assert context in self.activity_contexts

        # we don't actually support other contexts yet
        assert self.activity_contexts == ("logged_in",)

        if not c.activity_service:
            return

        try:
            c.activity_service.record_activity(self._fullname, visitor_id)
        except (TApplicationException, TProtocolException, TTransportException):
            pass

    def count_activity(self):
        """Count activity in this subreddit in all known contexts.
        :returns: a named tuple of activity information for each context.
        """
        # we don't actually support other contexts yet
        assert self.activity_contexts == ("logged_in",)

        if not c.activity_service:
            return None

        try:
            # TODO: support batch lookup of multiple contexts (requires changes
            # to activity service)
            with c.activity_service.retrying(attempts=4, budget=0.1) as svc:
                activity = svc.count_activity(self._fullname)
            return self.SubredditActivity(activity)
        except (TApplicationException, TProtocolException, TTransportException):
            return None

    def spammy(self):
        return self._spam

    def is_contributor(self, user):
        if self.type == 'employees_only':
            return user.employee
        else:
            return super(Subreddit, self).is_contributor(user)

    def can_comment(self, user):
        if c.user_is_admin:
            return True

        override = hooks.get_hook("subreddit.can_comment").call_until_return(
                                                            sr=self, user=user)

        if override is not None:
            return override
        elif self.is_banned(user):
            return False
        elif self.type == 'gold_restricted' and user.gold:
            return True
        elif self.type in ('public','restricted'):
            return True
        elif self.is_moderator(user) or self.is_contributor(user):
            #private requires contributorship
            return True
        elif self.type == 'gold_only':
            return user.gold or user.gold_charter
        else:
            return False

    def wiki_can_submit(self, user):
        return self.can_submit(user)

    def can_submit(self, user, promotion=False):
        if c.user_is_admin:
            return True
        elif self.is_banned(user) and not promotion:
            return False
        elif self.spammy():
            return False
        elif self.type == 'public':
            return True
        elif self.is_moderator(user) or self.is_contributor(user):
            #restricted/private require contributorship
            return True
        elif self.type == 'gold_only':
            return user.gold or user.gold_charter
        elif self.type == 'gold_restricted' and user.gold:
            return True
        elif self.type == 'restricted' and promotion:
            return True
        else:
            return False

    def can_submit_link(self, user):
        if c.user_is_admin or self.is_moderator_with_perms(user, "posts"):
            return True
        return "link" in self.allowed_types

    def can_submit_text(self, user):
        if c.user_is_admin or self.is_moderator_with_perms(user, "posts"):
            return True
        return "self" in self.allowed_types

    def can_ban(self, user):
        return (user
                and (c.user_is_admin
                     or self.is_moderator_with_perms(user, 'posts')))

    def can_mute(self, muter, user):
        return (user.is_mutable(self) and
            (c.user_is_admin or
                self.is_moderator_with_perms(muter, 'access', 'mail'))
        )

    def can_distinguish(self,user):
        return (user
                and (c.user_is_admin
                     or self.is_moderator_with_perms(user, 'posts')))

    def can_change_stylesheet(self, user):
        if c.user_is_loggedin:
            return (
                c.user_is_admin or self.is_moderator_with_perms(user, 'config'))
        else:
            return False

    def parse_css(self, content, verify=True):
        from r2.lib import cssfilter
        from r2.lib.template_helpers import (
            make_url_protocol_relative,
            static,
        )

        if g.css_killswitch or (verify and not self.can_change_stylesheet(c.user)):
            return (None, None)

        if not content:
            return ([], "")

        # parse in regular old http mode
        images = ImagesByWikiPage.get_images(self, "config/stylesheet")

        if self.quarantine:
            images = {name: static('blank.png') for name, url in images.iteritems()}

        protocol_relative_images = {
            name: make_url_protocol_relative(url)
            for name, url in images.iteritems()}
        parsed, errors = cssfilter.validate_css(
            content,
            protocol_relative_images,
        )

        return (errors, parsed)

    def change_css(self, content, parsed, prev=None, reason=None, author=None, force=False):
        from r2.models import ModAction
        from r2.lib.media import upload_stylesheet

        if not author:
            author = c.user

        if content is None:
            content = ''
        try:
            wiki = WikiPage.get(self, 'config/stylesheet')
        except tdb_cassandra.NotFound:
            wiki = WikiPage.create(self, 'config/stylesheet')
        wr = wiki.revise(content, previous=prev, author=author._id36, reason=reason, force=force)

        if parsed:
            self.stylesheet_url = upload_stylesheet(parsed)
            self.stylesheet_url_http = ""
            self.stylesheet_url_https = ""
        else:
            self.stylesheet_url = ""
            self.stylesheet_url_http = ""
            self.stylesheet_url_https = ""
        self._commit()

        if wr:
            ModAction.create(self, author, action='wikirevise', details='Updated subreddit stylesheet')

        return wr

    def is_special(self, user):
        return (user
                and (c.user_is_admin
                     or self.is_moderator(user)
                     or self.is_contributor(user)))

    def should_ratelimit(self, user, kind):
        if self.is_special(user):
            return False

        hook = hooks.get_hook("account.is_ratelimit_exempt")
        ratelimit_exempt = hook.call_until_return(account=c.user)
        if ratelimit_exempt:
            return False

        if kind == 'comment':
            rl_karma = g.MIN_RATE_LIMIT_COMMENT_KARMA
        else:
            rl_karma = g.MIN_RATE_LIMIT_KARMA

        return user.karma(kind, self) < rl_karma

    def can_view(self, user):
        if c.user_is_admin:
            return True

        if self.spammy() or not self.is_exposed(user):
            return False
        else:
            return self.is_allowed_to_view(user)

    def can_view_in_modlist(self, user):
        if c.user_is_admin:
            return True
        elif self.spammy():
            return False
        else:
            return self.is_allowed_to_view(user)

    def is_allowed_to_view(self, user):
        """Returns whether user can view based on permissions and settings"""
        if self.type in ('public', 'restricted',
                         'gold_restricted', 'archived'):
            return True
        elif c.user_is_loggedin:
            if self.type == 'gold_only':
                return (user.gold or
                    user.gold_charter or
                    self.is_moderator(user) or
                    self.is_moderator_invite(user))

            return (self.is_contributor(user) or
                    self.is_moderator(user) or
                    self.is_moderator_invite(user))

    def is_exposed(self, user):
        """Return whether user is opted in to the subreddit's content.
        If a subreddit is quarantined, users must opt-in before viewing its
        content. Logged out users cannot opt-in, and all users are considered
        opted-in to non-quarantined subreddits.
        """
        if not self.quarantine:
            return True
        elif not user:
            return False
        elif (user.email_verified and
              QuarantinedSubredditOptInsByAccount.is_opted_in(user, self)):
            return True

        return False

    @property
    def is_embeddable(self):
        return (self.type not in Subreddit.private_types and
                not self.over_18 and not self._spam and not self.quarantine)

    def can_demod(self, bully, victim):
        bully_rel = self.get_moderator(bully)
        if bully_rel is not None and bully == victim:
            # mods can always demod themselves
            return True
        victim_rel = self.get_moderator(victim)
        return (
            bully_rel is not None
            and victim_rel is not None
            and bully_rel.is_superuser()  # limited mods can't demod
            and bully_rel._date <= victim_rel._date)

    @classmethod
    def load_subreddits(cls, links, return_dict = True, stale=False):
        """returns the subreddits for a list of links. it also preloads the
        permissions for the current user."""
        srids = set(l.sr_id for l in links
                    if getattr(l, "sr_id", None) is not None)
        subreddits = {}
        if srids:
            subreddits = cls._byID(srids, data=True, stale=stale)

        if subreddits and c.user_is_loggedin:
            # dict( {Subreddit,Account,name} -> Relationship )
            SRMember._fast_query(subreddits.values(), (c.user,), ('moderator',),
                                 data=True)

        return subreddits if return_dict else subreddits.values()

    def keep_for_rising(self, sr_id):
        """Return whether or not to keep a thing in rising for this SR."""
        return sr_id == self._id

    @classmethod
    def get_sr_user_relations(cls, user, srs):
        """Return SubredditUserRelations for the user and subreddits.
        The SubredditUserRelation objects indicate whether the user is a
        moderator, contributor, subscriber, banned, or muted. This method
        batches the lookups of all the relations for all the subreddits.
        """

        moderator_srids = set()
        contributor_srids = set()
        banned_srids = set()
        muted_srids = set()
        subscriber_srids = cls.user_subreddits(user, limit=None)

        if user and c.user_is_loggedin:
            res = SRMember._fast_query(
                thing1s=srs,
                thing2s=user,
                name=["moderator", "contributor", "banned", "muted"],
            )
            # _fast_query returns a dict of {(t1, t2, name): rel}, with rel of
            # None if the relation doesn't exist
            rels = [rel for rel in res.itervalues() if rel]
            for rel in rels:
                rel_name = rel._name
                sr_id = rel._thing1_id

                if rel_name == "moderator":
                    moderator_srids.add(sr_id)
                elif rel_name == "contributor":
                    contributor_srids.add(sr_id)
                elif rel_name == "banned":
                    banned_srids.add(sr_id)
                elif rel_name == "muted":
                    muted_srids.add(sr_id)

        ret = {}
        for sr in srs:
            sr_id = sr._id
            ret[sr_id] = SubredditUserRelations(
                subscriber=sr_id in subscriber_srids,
                moderator=sr_id in moderator_srids,
                contributor=sr_id in contributor_srids,
                banned=sr_id in banned_srids,
                muted=sr_id in muted_srids,
            )
        return ret

    @classmethod
    def add_props(cls, user, wrapped):
        srs = {item.lookups[0] for item in wrapped}
        sr_user_relations = cls.get_sr_user_relations(user, srs)

        for item in wrapped:
            relations = sr_user_relations[item._id]
            item.subscriber = relations.subscriber
            item.moderator = relations.moderator
            item.contributor = relations.contributor
            item.banned = relations.banned
            item.muted = relations.muted

            if item.hide_subscribers and not c.user_is_admin:
                item._ups = 0

            item.score_hidden = (
                not item.can_view(user) or
                item.hide_num_users_info
            )

            item.score = item._ups

            # override "voting" score behavior (it will override the use of
            # item.score in builder.py to be ups-downs)
            item.likes = item.subscriber or None
            base_score = item.score - (1 if item.likes else 0)
            item.voting_score = [(base_score + x - 1) for x in range(3)]
            item.score_fmt = Score.subscribers

            #will seem less horrible when add_props is in pages.py
            from r2.lib.pages import UserText
            if item.public_description or item.description:
                text = (item.public_description or
                        summarize_markdown(item.description))
                item.public_description_usertext = UserText(item, text)
            else:
                item.public_description_usertext = None


        Printable.add_props(user, wrapped)

    cache_ignore = {
        "description",
        "public_description",
        "subscribers",
    }.union(Printable.cache_ignore)

    @staticmethod
    def wrapped_cache_key(wrapped, style):
        s = Printable.wrapped_cache_key(wrapped, style)
        return s

    @classmethod
    def default_subreddits(cls, ids=True):
        """Return the subreddits a user with no subscriptions would see."""
        location = get_user_location()
        srids = LocalizedDefaultSubreddits.get_defaults(location)

        srs = Subreddit._byID(srids, data=True, return_dict=False, stale=True)
        srs = filter(lambda sr: sr.allow_top, srs)

        if ids:
            return [sr._id for sr in srs]
        else:
            return srs

    @classmethod
    def featured_subreddits(cls):
        """Return the curated list of subreddits shown during onboarding."""
        location = get_user_location()
        srids = LocalizedFeaturedSubreddits.get_featured(location)

        srs = Subreddit._byID(srids, data=True, return_dict=False, stale=True)
        srs = filter(lambda sr: sr.discoverable, srs)

        return srs

    @classmethod
    @memoize('random_reddits', time = 1800)
    def random_reddits_cached(cls, user_name, sr_ids, limit):
        # First filter out any subreddits that don't have a new enough post
        # to be included in the front page (just doing this may remove enough
        # to get below the limit anyway)
        sr_ids = SubredditsActiveForFrontPage.filter_inactive_ids(sr_ids)
        if len(sr_ids) <= limit:
            return sr_ids

        return random.sample(sr_ids, limit)

    @classmethod
    def random_reddits(cls, user_name, sr_ids, limit):
        """Select a random subset from sr_ids.
        Used for limiting the number of subscribed subreddits shown on a user's
        front page. Selection is cached for a while so the front page doesn't
        jump around.
        """

        if not limit:
            return sr_ids

        # if the user is subscribed to them, the automatic subreddits should
        # always be in the front page set and not count towards the limit
        if g.automatic_reddits:
            automatics = Subreddit._by_name(
                g.automatic_reddits, stale=True).values()
            automatic_ids = [sr._id for sr in automatics if sr._id in sr_ids]
            sr_ids = [sr_id for sr_id in sr_ids if sr_id not in automatic_ids]
        else:
            automatic_ids = []

        if len(sr_ids) > limit:
            sr_ids = sorted(sr_ids)
            sr_ids = cls.random_reddits_cached(user_name, sr_ids, limit)

        return sr_ids + automatic_ids

    @classmethod
    def random_reddit(cls, over18=False, user=None):
        if over18:
            sr_ids = NamedGlobals.get("popular_over_18_sr_ids")
        else:
            sr_ids = NamedGlobals.get("popular_sr_ids")

        if user:
            excludes = set(cls.user_subreddits(user, limit=None))
            sr_ids = list(set(sr_ids) - excludes)

        if not sr_ids:
            return Subreddit._by_name(g.default_sr)

        sr_id = random.choice(sr_ids)
        sr = Subreddit._byID(sr_id, data=True)
        return sr

    @classmethod
    def update_popular_subreddits(cls, limit=5000):
        q = cls._query(cls.c.type == "public", sort=desc('_downs'), limit=limit,
                       data=True)
        srs = list(q)

        # split the list into two based on whether the subreddit is 18+ or not
        sr_ids = []
        over_18_sr_ids = []

        # /r/promos is public but has special handling to make it unviewable
        promo_sr_id = cls.get_promote_srid()

        for sr in srs:
            if not sr.discoverable:
                continue

            if sr._id == promo_sr_id:
                continue

            if not sr.over_18:
                sr_ids.append(sr._id)
            else:
                over_18_sr_ids.append(sr._id)

        NamedGlobals.set("popular_sr_ids", sr_ids)
        NamedGlobals.set("popular_over_18_sr_ids", over_18_sr_ids)

    @classmethod
    def random_subscription(cls, user):
        if user.has_subscribed:
            sr_ids = Subreddit.subscribed_ids_by_user(user)
        else:
            sr_ids = Subreddit.default_subreddits(ids=True)

        return (Subreddit._byID(random.choice(sr_ids), data=True)
                if sr_ids else Subreddit._by_name(g.default_sr))

    @classmethod
    def user_subreddits(cls, user, ids=True, limit=DEFAULT_LIMIT):
        """
        subreddits that appear in a user's listings. If the user has
        subscribed, returns the stored set of subscriptions.
        limit - if it's Subreddit.DEFAULT_LIMIT, limits to 50 subs
                (100 for gold users)
                if it's None, no limit is used
                if it's an integer, then that many subs will be returned
        Otherwise, return the default set.
        """
        # Limit the number of subs returned based on user status,
        # if no explicit limit was passed
        if limit is Subreddit.DEFAULT_LIMIT:
            if user and user.gold:
                # Goldies get extra subreddits
                limit = Subreddit.gold_limit
            else:
                limit = Subreddit.sr_limit

        # note: for user not logged in, the fake user account has
        # has_subscribed == False by default.
        if user and user.has_subscribed:
            sr_ids = Subreddit.subscribed_ids_by_user(user)
            sr_ids = cls.random_reddits(user.name, sr_ids, limit)

            return sr_ids if ids else Subreddit._byID(sr_ids,
                                                      data=True,
                                                      return_dict=False,
                                                      stale=True)
        else:
            return cls.default_subreddits(ids=ids)


    # Used to pull all of the SRs a given user moderates or is a contributor
    # to (which one is controlled by query_param)
    @classmethod
    def special_reddits(cls, user, query_param):
        lookup = getattr(cls, 'reverse_%s_ids' % query_param)
        return lookup(user)

    @classmethod
    def subscribe_defaults(cls, user):
        if not user.has_subscribed:
            user.has_subscribed = True
            user._commit()
            srs = cls.user_subreddits(user=None, ids=False, limit=None)
            cls.subscribe_multiple(user, srs)

    def keep_item(self, wrapped):
        if c.user_is_admin:
            return True

        user = c.user if c.user_is_loggedin else None
        return self.can_view(user)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        if isinstance(self, FakeSubreddit):
            return self is other

        return self._id == other._id

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def get_all_mod_ids(srs):
        from r2.lib.db.thing import Merge
        srs = tup(srs)
        queries = [
            SRMember._simple_query(
                ["_thing2_id"],
                SRMember.c._thing1_id == sr._id,
                SRMember.c._name == 'moderator',
            ) for sr in srs
        ]

        merged = Merge(queries)
        return [rel._thing2_id for rel in list(merged)]

    def update_moderator_permissions(self, user, **kwargs):
        """Grants or denies permissions to this moderator.
        Does nothing if the given user is not a moderator. Args are named
        parameters with bool or None values (use None to all back to the default
        for a permission).
        """
        rel = self.get_moderator(user)
        if rel:
            rel.update_permissions(**kwargs)
            rel._commit()

    def add_rel_note(self, type, user, note):
        rel = getattr(self, "get_%s" % type)(user)
        if not rel:
            raise ValueError("User is not %s." % type)
        rel.note = note
        rel._commit()

    def get_live_promos(self):
        from r2.lib import promote
        return promote.get_live_promotions([self.name])

    def schedule_unban(self, kind, victim, banner, duration):
        return SubredditTempBan.schedule(
            self,
            kind,
            victim,
            banner,
            datetime.timedelta(days=duration),
        )

    def unschedule_unban(self, victim, type):
        SubredditTempBan.unschedule(self.name, victim.name, type)

    def get_tempbans(self, type=None, names=None):
        return SubredditTempBan.search(self.name, type, names)

    def get_muted_items(self, names=None):
        return MutedAccountsBySubreddit.search(self, names)

    def add_gilding_seconds(self):
        from r2.models.gold import get_current_value_of_month
        seconds = get_current_value_of_month()
        self._incr("gilding_server_seconds", int(seconds))

    @property
    def allow_gilding(self):
        return not self.quarantine

    @classmethod
    def get_promote_srid(cls):
        try:
            return cls._by_name(g.promo_sr_name, stale=True)._id
        except NotFound:
            return None

    def is_subscriber(self, user):
        try:
            return bool(SubscribedSubredditsByAccount.fast_query(user, self))
        except tdb_cassandra.NotFound:
            return False

    def add_subscriber(self, user):
        SubscribedSubredditsByAccount.create(user, self)
        SubscriptionsByDay.create(self, user)
        add_legacy_subscriber(self, user)
        self._incr('_ups', 1)

    @classmethod
    def subscribe_multiple(cls, user, srs):
        SubscribedSubredditsByAccount.create(user, srs)
        SubscriptionsByDay.create(srs, user)
        add_legacy_subscriber(srs, user)
        for sr in srs:
            sr._incr('_ups', 1)

    def remove_subscriber(self, user):
        SubscribedSubredditsByAccount.destroy(user, self)
        remove_legacy_subscriber(self, user)
        self._incr('_ups', -1)

    @classmethod
    def subscribed_ids_by_user(cls, user):
        return SubscribedSubredditsByAccount.get_all_sr_ids(user)

    @classmethod
    def reverse_subscriber_ids(cls, user):
        # This is just for consistency with all the other UserRel types
        return cls.subscribed_ids_by_user(user)

    def get_rgb(self, fade=0.8):
        r = int(256 - (hash(str(self._id)) % 256)*(1-fade))
        g = int(256 - (hash(str(self._id) + ' ') % 256)*(1-fade))
        b = int(256 - (hash(str(self._id) + '  ') % 256)*(1-fade))
        return (r, g, b)

    def set_sticky(self, link, log_user=None, num=None):
        unstickied_fullnames = []

        if not self.sticky_fullnames:
            self.sticky_fullnames = [link._fullname]
        else:
            # don't re-sticky something that's already stickied
            if link._fullname in self.sticky_fullnames:
                return

            # XXX: have to work with a copy of the list instead of modifying
            #   it directly, because it doesn't get marked as "dirty" and
            #   saved properly unless we assign a new list to the attr
            sticky_fullnames = self.sticky_fullnames[:]

            # if a particular slot was specified and is in use, replace it
            if num and num <= len(sticky_fullnames):
                unstickied_fullnames.append(sticky_fullnames[num-1])
                sticky_fullnames[num-1] = link._fullname
            else:
                # either didn't specify a slot or it's empty, just append

                # if we're already at the max number of stickies, remove
                # the bottom-most to make room for this new one
                if self.has_max_stickies:
                    unstickied_fullnames.extend(
                        sticky_fullnames[self.MAX_STICKIES-1:])
                    sticky_fullnames = sticky_fullnames[:self.MAX_STICKIES-1]

                sticky_fullnames.append(link._fullname)

            self.sticky_fullnames = sticky_fullnames

        self._commit()

        if log_user:
            from r2.models import Link, ModAction
            for fullname in unstickied_fullnames:
                unstickied = Link._by_fullname(fullname)
                ModAction.create(self, log_user, "unsticky",
                    target=unstickied, details="replaced")
            ModAction.create(self, log_user, "sticky", target=link)

    def remove_sticky(self, link, log_user=None):
        # XXX: have to work with a copy of the list instead of modifying
        #   it directly, because it doesn't get marked as "dirty" and
        #   saved properly unless we assign a new list to the attr
        sticky_fullnames = self.sticky_fullnames[:]
        try:
            sticky_fullnames.remove(link._fullname)
        except ValueError:
            return

        self.sticky_fullnames = sticky_fullnames
        self._commit()

        if log_user:
            from r2.models import ModAction
            ModAction.create(self, log_user, "unsticky", target=link)

    @property
    def has_max_stickies(self):
        if not self.sticky_fullnames:
            return False
        return len(self.sticky_fullnames) >= self.MAX_STICKIES
