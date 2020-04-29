# The contents of this file are subject to the Common Public Attribution
# License Version 1.0. (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://code.reddit.com/LICENSE. The License is based on the Mozilla Public
# License Version 1.1, but Sections 14 and 15 have been added to cover use of
# software over a computer network and provide for limited attribution for the
# Original Developer. In addition, Exhibit A has been modified to be consistent
# with Exhibit B.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
#
# The Original Code is reddit.
#
# The Original Developer is the Initial Developer.  The Initial Developer of
# the Original Code is reddit Inc.
#
# All portions of the code written by reddit are Copyright (c) 2006-2015 reddit
# Inc. All Rights Reserved.
###############################################################################

from ConfigParser import SafeConfigParser
from datetime import datetime, timedelta
from r2.lib.db import tdb_cassandra
from r2.lib.db.thing import NotFound
from r2.lib.merge import *
from r2.models.last_modified import LastModified
from pycassa.system_manager import TIME_UUID_TYPE
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.controllers.util import abort
from r2.lib.db.tdb_cassandra import NotFound
from r2.models.printable import Printable
from r2.models.account import Account
from collections import OrderedDict
from StringIO import StringIO

import pycassa.types


class WikiPage(tdb_cassandra.Thing):
    """ Contains permissions, current content (markdown), subreddit, and current revision (ID)
        Key is subreddit-pagename """

    _use_db = True
    _connection_pool = 'main'

    _read_consistency_level = tdb_cassandra.CL.QUORUM
    _write_consistency_level = tdb_cassandra.CL.QUORUM

    _date_props = ('last_edit_date')
    _str_props = ('revision', 'name', 'last_edit_by', 'content', 'sr')
    _int_props = ('permlevel')
    _bool_props = ('listed')
    _defaults = {'listed': True}

    def get_author(self):
        if self._get('last_edit_by'):
            return Account._byID36(self.last_edit_by, data=True)
        return None

    @classmethod
    def id_for(cls, sr, name):
        id = getattr(sr, '_id36', None)
        if not id:
            raise tdb_cassandra.NotFound
        return wiki_id(id, name)

    @classmethod
    def get_multiple(cls, pages):
        """Get multiple wiki pages.

        Arguments:
        pages -- list of tuples in the form of [(sr, names),..]
        """
        return cls._byID([cls.id_for(sr, name) for sr, name in pages])

    @classmethod
    def get(cls, sr, name):
        return cls._byID(cls.id_for(sr, name))

    @classmethod
    def create(cls, sr, name):
        if not name or not sr:
            raise ValueError

        name = name.lower()
        _id = wiki_id(sr._id36, name)
        lock_key = "wiki_create_%s:%s" % (sr._id36, name)
        with g.make_lock("wiki", lock_key):
            try:
                cls._byID(_id)
            except tdb_cassandra.NotFound:
                pass
            else:
                raise WikiPageExists

            page = cls(_id=_id, sr=sr._id36, name=name, permlevel=0, content='')
            page._commit()
            return page

    @property
    def restricted(self):
        return WikiPage.is_restricted(self.name)

    @classmethod
    def is_impossible(cls, page):
        return ("%s/" % page) in impossible_namespaces or page.startswith(impossible_namespaces)

    @classmethod
    def is_restricted(cls, page):
        return ("%s/" % page) in restricted_namespaces or page.startswith(restricted_namespaces)

    @classmethod
    def is_special(cls, page):
        return page in special_pages

    @classmethod
    def get_special_view_permlevel(cls, page):
        return special_page_view_permlevels.get(page, 0)

    @classmethod
    def is_automatically_created(cls, page):
        return page in automatically_created_pages

    @property
    def special(self):
        return WikiPage.is_special(self.name)

    def add_to_listing(self):
        WikiPagesBySR.add_object(self)

    def _on_create(self):
        self.add_to_listing()

    def _on_commit(self):
         self.add_to_listing()

    def remove_editor(self, user):
        WikiPageEditors._remove(self._id, [user])

    def add_editor(self, user):
        WikiPageEditors._set_values(self._id, {user: ''})

    @classmethod
    def get_pages(cls, sr, after=None, filter_check=None):
        NUM_AT_A_TIME = num = 1000
        pages = []
        while num >= NUM_AT_A_TIME:
            wikipages = WikiPagesBySR.query([sr._id36],
                                            after=after,
                                            count=NUM_AT_A_TIME)
            wikipages = list(wikipages)
            num = len(wikipages)
            pages += wikipages
            after = wikipages[-1] if num else None
        return filter(filter_check, pages)

    @classmethod
    def get_listing(cls, sr, filter_check=None):
        """
            Create a tree of pages from their path.
        """
        page_tree = OrderedDict()
        pages = cls.get_pages(sr, filter_check=filter_check)
        pages = sorted(pages, key=lambda page: page.name)
        for page in pages:
            p = page.name.split('/')
            cur_node = page_tree
            # Loop through all elements of the path except the page name portion
            for name in p[:-1]:
                next_node = cur_node.get(name)
                # If the element did not already exist in the tree, create it
                if not next_node:
                    new_node = OrderedDict()
                    cur_node[name] = [None, new_node]
                else:
                    # Otherwise, continue through
                    new_node = next_node[1]
                cur_node = new_node
            # Get the actual page name portion of the path
            pagename = p[-1]
            node = cur_node.get(pagename)
            # The node may already exist as a path name in the tree
            if node:
                node[0] = page
            else:
                cur_node[pagename] = [page, OrderedDict()]

        return page_tree, pages

    def get_editor_accounts(self):
        editors = self.get_editors()
        accounts = [Account._byID36(editor, data=True)
                    for editor in self.get_editors()]
        accounts = [account for account in accounts
                    if not account._deleted]
        return accounts

    def get_editors(self, properties=None):
        try:
            return WikiPageEditors._byID(self._id, properties=properties)._values().keys() or []
        except tdb_cassandra.NotFoundException:
            return []

    def has_editor(self, editor):
        return bool(self.get_editors(properties=[editor]))

    def revise(self, content, previous = None, author=None, force=False, reason=None):
        if content is None:
            content = ""
        if self.content == content:
            return
        force = True if previous is None else force
        max_length = special_length_restrictions_bytes.get(self.name, MAX_PAGE_LENGTH_BYTES)
        if len(content) > max_length:
            raise ContentLengthError(max_length)

        revision = getattr(self, 'revision', None)

        if not force and (revision and previous != revision):
            if previous:
                origcontent = WikiRevision.get(previous, pageid=self._id).content
            else:
                origcontent = ''
            try:
                content = threewaymerge(origcontent, content, self.content)
            except ConflictException as e:
                e.new_id = revision
                raise e

        wr = WikiRevision.create(self._id, content, author, reason)
        self.content = content
        self.last_edit_by = author
        self.last_edit_date = wr.date
        self.revision = str(wr._id)
        self._commit()

        LastModified.touch(self._fullname, "Edit")

        return wr

    def change_permlevel(self, permlevel, force=False):
        NUM_PERMLEVELS = 3
        if permlevel == self.permlevel:
            return
        if not force and int(permlevel) not in range(NUM_PERMLEVELS):
            raise ValueError('Permlevel not valid')
        self.permlevel = permlevel
        self._commit()

    def get_revisions(self, after=None, count=100):
        return WikiRevisionHistoryByPage.query(
            rowkeys=[self._id], after=after, count=count)
