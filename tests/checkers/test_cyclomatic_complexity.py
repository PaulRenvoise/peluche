def is_quarantined(self):
    pass


def is_limited_moderator(self, user):
    rel = self.is_moderator(user)
    return bool(rel and not rel.is_superuser())


def get_related_subreddits(self):
    try:
        multi = LabeledMulti._byID(self._related_multipath)
    except tdb_cassandra.NotFound:
        multi = None
    return  [sr.name for sr in multi.srs] if multi else []


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


def can_edit(self, user):
    if isinstance(user, FakeAccount):
        return False

    # subreddit multireddit (admin can edit)
    if isinstance(self.owner, Subreddit):
        return (c.user_is_admin or
                self.owner.is_moderator_with_perms(user, 'config'))

    if c.user_is_admin and self.owner == Account.system_user():
        return True

    return user == self.owner


@classmethod
def lookup(cls, keys, update=False):
    def _lookup(keys):
        rows = cls._cf.multiget(keys)
        ret = {}
        for key in keys:
            columns = rows[key] if key in rows else {}
            id36s = columns.keys()
            ret[key] = id36s
        return ret

    id36s_by_location = sgm(
        cache=g.gencache,
        keys=keys,
        miss_fn=_lookup,
        prefix=cls.CACHE_PREFIX,
        stale=True,
        _update=update,
        ignore_set_errors=True,
    )
    ids_by_location = {location: [int(id36, 36) for id36 in id36s]
                       for location, id36s in id36s_by_location.iteritems()}
    return ids_by_location


def set_related_subreddits(self, related_subreddits):
    try:
        multi = LabeledMulti._byID(self._related_multipath)
    except tdb_cassandra.NotFound:
        if not related_subreddits:
            return
        multi = LabeledMulti.create(self._related_multipath, self)

    if related_subreddits:
        srs = Subreddit.find_by_name(related_subreddits)
        try:
            sr_props = {srs[sr_name]: {} for sr_name in related_subreddits}
        except KeyError as e:
            raise NotFound('Subreddit %s' % e.args[0])

        multi.clear_srs()
        multi.add_srs(sr_props)
        multi._commit()
    else:
        multi.delete()

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


def find_by_name(cls, names, stale=False, _update = False):
    '''
    Usages:
    1. Subreddit.find_by_name('funny') # single sr name
    Searches for a single subreddit. Returns a single Subreddit object or
    raises NotFound if the subreddit doesn't exist.
    2. Subreddit.find_by_name(['aww','iama']) # list of sr names
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
                g.log.debug("Subreddit.find_by_name() ignoring invalid srname: %s", lname)

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
