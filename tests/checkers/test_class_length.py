class SubredditExists(Exception):
    pass


class FakeSRMember:
    def __init__(self, permission_class):
        self.permission_class = permission_class

    def has_permission(self, perm):
        return True

    def get_permissions(self):
        return self.permission_class(all=True)

    def is_superuser(self):
        return True


class FakeSubreddit(BaseSite):
    _defaults = dict(Subreddit._defaults,
        link_flair_position='right',
        flair_enabled=False,
    )

    def __init__(self):
        BaseSite.__init__(self)

    def keep_for_rising(self, sr_id):
        return False

    def _should_wiki(self):
        return False

    def allow_gilding(self):
        return True

    def allow_ads(self):
        return True

    def is_moderator(self, user):
        if c.user_is_loggedin and c.user_is_admin:
            return FakeSRMember(ModeratorPermissionSet)

    def can_view(self, user):
        return True

    def can_comment(self, user):
        return False

    def can_submit(self, user, promotion=False):
        return False

    def can_change_stylesheet(self, user):
        return False

    def is_banned(self, user):
        return False

    def is_muted(self, user):
        return False

    def get_all_comments(self):
        from r2.lib.db import queries
        return queries.get_all_comments()

    def get_gilded(self):
        raise NotImplementedError()

    def spammy(self):
        return False


class AdminTools(object):

    def spam(self, things, auto=True, moderator_banned=False,
             banner=None, date=None, train_spam=True, **kw):
        from r2.lib.db import queries

        all_things = tup(things)
        new_things = [x for x in all_things if not x._spam]

        Report.accept(all_things, True)

        for t in all_things:
            if getattr(t, "promoted", None) is not None:
                g.log.debug("Refusing to mark promotion %r as spam" % t)
                continue

            if not t._spam and train_spam:
                note = 'spam'
            elif not t._spam and not train_spam:
                note = 'remove not spam'
            elif t._spam and not train_spam:
                note = 'confirm spam'
            elif t._spam and train_spam:
                note = 'reinforce spam'

            t._spam = True

            if moderator_banned:
                t.verdict = 'mod-removed'
            elif not auto:
                t.verdict = 'admin-removed'

            ban_info = copy(getattr(t, 'ban_info', {}))
            if isinstance(banner, dict):
                ban_info['banner'] = banner[t._fullname]
            else:
                ban_info['banner'] = banner

            ban_info.update(auto=auto,
                            moderator_banned=moderator_banned,
                            banned_at=date or datetime.now(g.tz),
                            **kw)

            ban_info['note'] = note

            t.ban_info = ban_info
            t._commit()

            if auto:
                amqp.add_item("auto_removed", t._fullname)

        if not auto:
            self.author_spammer(new_things, True)
            self.set_last_sr_ban(new_things)

        queries.ban(all_things, filtered=auto)

        for t in all_things:
            if auto:
                amqp.add_item("auto_removed", t._fullname)

            if isinstance(t, Comment):
                amqp.add_item("removed_comment", t._fullname)
            elif isinstance(t, Link):
                amqp.add_item("removed_link", t._fullname)

    def unspam(self, things, moderator_unbanned=True, unbanner=None,
               train_spam=True, insert=True):
        from r2.lib.db import queries

        things = tup(things)

        # We want to make unban-all moderately efficient, so when
        # mass-unbanning, we're going to skip the code below on links that
        # are already not banned.  However, when someone manually clicks
        # "approve" on an unbanned link, and there's just one, we want do
        # want to run the code below. That way, the little green checkmark
        # will have the right mouseover details, the reports will be
        # cleared, etc.

        if len(things) > 1:
            things = [x for x in things if x._spam]

        Report.accept(things, False)
        for t in things:
            ban_info = copy(getattr(t, 'ban_info', {}))
            ban_info['unbanned_at'] = datetime.now(g.tz)

            if unbanner:
                ban_info['unbanner'] = unbanner

            if ban_info.get('reset_used', None) == None:
                ban_info['reset_used'] = False
            else:
                ban_info['reset_used'] = True

            t.ban_info = ban_info
            t._spam = False

            if moderator_unbanned:
                t.verdict = 'mod-approved'
            else:
                t.verdict = 'admin-approved'
            t._commit()

            if isinstance(t, Comment):
                amqp.add_item("approved_comment", t._fullname)
            elif isinstance(t, Link):
                amqp.add_item("approved_link", t._fullname)

        self.author_spammer(things, False)

        self.set_last_sr_ban(things)

        queries.unban(things, insert)

    def report(self, thing):
        pass

    def author_spammer(self, things, spam):
        """incr/decr the 'spammer' field for the author of every
           passed thing"""
        by_aid = {}
        for thing in things:
            if (hasattr(thing, 'author_id')
                and not getattr(thing, 'ban_info', {}).get('auto',True)):
                # only decrement 'spammer' for items that were not
                # autobanned
                by_aid.setdefault(thing.author_id, []).append(thing)

        if by_aid:
            authors = Account._byID(by_aid.keys(), data=True, return_dict=True)

            for aid, author_things in by_aid.iteritems():
                author = authors[aid]
                author._incr('spammer', len(author_things) if spam else -len(author_things))

    def set_last_sr_ban(self, things):
        by_srid = {}
        for thing in things:
            if getattr(thing, 'sr_id', None) is not None:
                by_srid.setdefault(thing.sr_id, []).append(thing)

        if by_srid:
            srs = Subreddit._byID(by_srid.keys(), data=True, return_dict=True)

            for sr_id, sr_things in by_srid.iteritems():
                sr = srs[sr_id]

                sr.last_mod_action = datetime.now(g.tz)
                sr._commit()
                sr._incr('mod_actions', len(sr_things))

    def adjust_gold_expiration(self, account, days=0, months=0, years=0):
        now = datetime.now(g.display_tz)
        if months % 12 == 0:
            years += months / 12
        else:
            days += months * 31
        days += years * 366

        existing_expiration = getattr(account, "gold_expiration", None)
        if existing_expiration is None or existing_expiration < now:
            existing_expiration = now

        account.gold_expiration = existing_expiration + timedelta(days)

        if account.gold_expiration > now and not account.gold:
            self.engolden(account)
        elif account.gold_expiration <= now and account.gold:
            self.degolden(account)

        account._commit()

    def engolden(self, account):
        now = datetime.now(g.display_tz)
        account.gold = True
        description = "Since " + now.strftime("%B %Y")

        trophy = Award.give_if_needed("reddit_gold", account,
                                     description=description,
                                     url="/gold/about")

        if trophy and trophy.description.endswith("Member Emeritus"):
            trophy.description = description
            trophy._commit()

        account._commit()
        account.friend_rels_cache(_update=True)

    def degolden(self, account):
        Award.take_away("reddit_gold", account)

        account.gold = False
        account._commit()

    def admin_list(self):
        return list(g.admins)

    def create_award_claim_code(self, unique_award_id, award_codename,
                                description, url):
        '''Create a one-time-use claim URL for a user to claim a trophy.
        `unique_award_id` - A string that uniquely identifies the kind of
                            Trophy the user would be claiming.
                            See: token.py:AwardClaimToken.uid
        `award_codename` - The codename of the Award the user will claim
        `description` - The description the Trophy will receive
        `url` - The URL the Trophy will receive
        '''
        award = Award._by_codename(award_codename)
        token = AwardClaimToken._new(unique_award_id, award, description, url)

        return token.confirm_url()


class ThingBase(object):  # class-too-long
    # base class for Thing

    __metaclass__ = ThingMeta

    _cf_name = None # the name of the ColumnFamily; defaults to the
                    # name of the class

    # subclasses must replace these

    _type_prefix = None # this must be present for classes with _use_db==True

    _use_db = False

    # the Cassandra column-comparator (internally orders column
    # names). In real life you can't change this without some changes
    # to tdb_cassandra to support other attr types
    _compare_with = UTF8_TYPE

    _value_type = None # if set, overrides all of the _props types
                       # below. Used for Views. One of 'int', 'float',
                       # 'bool', 'pickle', 'json', 'date', 'bytes', 'str'

    _int_props = ()
    _float_props = () # note that we can lose resolution on these
    _bool_props = ()
    _pickle_props = ()
    _json_props = ()
    _date_props = () # note that we can lose resolution on these
    _bytes_props = ()
    _str_props = () # at present we never actually read out of here
                    # since it's the default if none of the previous
                    # matches

    # the value that we assume a property to have if it is not found
    # in the DB. Note that we don't do type-checking here, so if you
    # want a default to be a boolean and want it to be storable you'll
    # also have to set it in _bool_props
    _defaults = {}

    # The default TTL in seconds to add to all columns. Note: if an
    # entire object is expected to have a TTL, it should be considered
    # immutable! (You don't want to write out an object with an author
    # and date, then go update author or add a new column, then have
    # the original columns expire. Then when you go to look it up, the
    # inherent properties author and/or date will be gone and only the
    # updated columns will be present.) This is an expected convention
    # and is not enforced.
    _ttl = None
    _warn_on_partial_ttl = True

    # A per-class dictionary of default TTLs that new columns of this
    # class should have
    _default_ttls = {}

    # A per-instance property defining the TTL of individual columns
    # (that must also appear in self._dirties)
    _column_ttls = {}

    # a timestamp property that will automatically be added to newly
    # created Things (disable by setting to None)
    _timestamp_prop = None

    # a per-instance property indicating that this object was
    # partially loaded: i.e. only some properties were requested from
    # the DB
    _partial = None

    # a per-instance property that specifies that the columns backing
    # these attributes are to be removed on _commit()
    _deletes = set()

    # thrift will materialize the entire result set for a slice range
    # in memory, meaning that we need to limit the maximum number of columns
    # we receive in a single get to avoid hurting the server. if this
    # value is true, we will make sure to do extra gets to retrieve all of
    # the columns in a row when there are more than the per-call maximum.
    _fetch_all_columns = False

    # request-local cache to avoid duplicate lookups from hitting C*
    _local_cache = g.cassandra_local_cache

    def __init__(self, _id = None, _committed = False, _partial = None, **kw):
        # things that have changed
        self._dirties = kw.copy()

        # what the original properties were when we went to Cassandra to
        # get them
        self._orig = {}

        self._defaults = self._defaults.copy()

        # whether this item has ever been created
        self._committed = _committed

        self._partial = None if _partial is None else frozenset(_partial)

        self._deletes = set()
        self._column_ttls = {}

        # our row key
        self._id = _id

        if not self._use_db:
            raise TdbException("Cannot make instances of %r" % (self.__class__,))

    @classmethod
    def _byID(cls, ids, return_dict=True, properties=None):
        ids, is_single = tup(ids, True)

        if properties is not None:
            asked_properties = frozenset(properties)
            willask_properties = set(properties)

        if not len(ids):
            if is_single:
                raise InvariantException("whastis?")
            return {}

        # all keys must be strings or directly convertable to strings
        assert all(isinstance(_id, basestring) or str(_id) for _id in ids)

        def reject_bad_partials(cached, still_need):
            # tell sgm that the match it found in the cache isn't good
            # enough if it's a partial that doesn't include our
            # properties. we still need to look those items up to get
            # the properties that we're after
            stillfind = set()

            for k, v in cached.iteritems():
                if properties is None:
                    if v._partial is not None:
                        # there's a partial in the cache but we're not
                        # looking for partials
                        stillfind.add(k)
                elif v._partial is not None and not asked_properties.issubset(v._partial):
                    # we asked for a partial, and this is a partial,
                    # but it doesn't have all of the properties that
                    # we need
                    stillfind.add(k)

                    # other callers in our request are now expecting
                    # to find the properties that were on that
                    # partial, so we'll have to preserve them
                    for prop in v._partial:
                        willask_properties.add(prop)

            for k in stillfind:
                del cached[k]
                still_need.add(k)

        def lookup(l_ids):
            if properties is None:
                rows = cls._cf.multiget(l_ids, column_count=max_column_count)

                # if we got max_column_count columns back for a row, it was
                # probably clipped. in this case, we should fetch the remaining
                # columns for that row and add them to the result.
                if cls._fetch_all_columns:
                    for key, row in rows.iteritems():
                        if len(row) == max_column_count:
                            last_column_seen = next(reversed(row))
                            cols = cls._cf.xget(key,
                                                column_start=last_column_seen,
                                                buffer_size=max_column_count)
                            row.update(cols)
            else:
                rows = cls._cf.multiget(l_ids, columns = willask_properties)

            l_ret = {}
            for t_id, row in rows.iteritems():
                t = cls._from_serialized_columns(t_id, row)
                if properties is not None:
                    # make sure that the item is marked as a _partial
                    t._partial = willask_properties
                l_ret[t._id] = t

            return l_ret

        ret = sgm(
            cache=cls._local_cache,
            keys=ids,
            miss_fn=lookup,
            prefix=cls._cache_prefix(),
            found_fn=reject_bad_partials,
        )

        if is_single and not ret:
            raise NotFound("<%s %r>" % (cls.__name__,
                                        ids[0]))
        elif is_single:
            assert len(ret) == 1
            return ret.values()[0]
        elif return_dict:
            return ret
        else:
            return filter(None, (ret.get(i) for i in ids))

    @property
    def _fullname(self):
        if self._type_prefix is None:
            raise TdbException("%r has no _type_prefix, so fullnames cannot be generated"
                               % self.__class__)

        return '%s_%s' % (self._type_prefix, self._id)

    @classmethod
    def _by_fullname(cls, fnames, return_dict=True, ignore_missing=False):
        if ignore_missing:
            raise NotImplementedError
        ids, is_single = tup(fnames, True)

        by_cls = {}
        for i in ids:
            typ, underscore, _id = i.partition('_')
            assert underscore == '_'

            by_cls.setdefault(thing_types[typ], []).append(_id)

        items = []
        for typ, ids in by_cls.iteritems():
            items.extend(typ._byID(ids).values())

        if is_single:
            try:
                return items[0]
            except IndexError:
                raise NotFound("<%s %r>" % (cls.__name__, ids[0]))
        elif return_dict:
            return dict((x._fullname, x) for x in items)
        else:
            d = dict((x._fullname, x) for x in items)
            return [d[fullname] for fullname in fnames]

    @classmethod
    def _cache_prefix(cls):
        return 'tdbcassandra_' + cls._type_prefix + '_'

    def _cache_key(self):
        if not self._id:
            raise TdbException('no cache key for uncommitted %r' % (self,))

        return self._cache_key_id(self._id)

    @classmethod
    def _cache_key_id(cls, t_id):
        return cls._cache_prefix() + t_id

    @classmethod
    def _wcl(cls, wcl, default = None):
        if wcl is not None:
            return wcl
        elif default is not None:
            return default
        return cls._write_consistency_level

    def _rcl(cls, rcl, default = None):
        if rcl is not None:
            return rcl
        elif default is not None:
            return default
        return cls._read_consistency_level

    @classmethod
    def _get_column_validator(cls, colname):
        return cls._cf.column_validators.get(colname,
                                             cls._cf.default_validation_class)

    @classmethod
    def _deserialize_column(cls, attr, val):
        if attr in cls._int_props or (cls._value_type and cls._value_type == 'int'):
            try:
                return int(val)
            except ValueError:
                return long(val)
        elif attr in cls._float_props or (cls._value_type and cls._value_type == 'float'):
            return float(val)
        elif attr in cls._bool_props or (cls._value_type and cls._value_type == 'bool'):
            # note that only the string "1" is considered true!
            return val == '1'
        elif attr in cls._pickle_props or (cls._value_type and cls._value_type == 'pickle'):
            return pickle.loads(val)
        elif attr in cls._json_props or (cls._value_type and cls._value_type == 'json'):
            return json.loads(val)
        elif attr in cls._date_props or attr == cls._timestamp_prop or (cls._value_type and cls._value_type == 'date'):
            return cls._deserialize_date(val)
        elif attr in cls._bytes_props or (cls._value_type and cls._value_type == 'bytes'):
            return val

        # otherwise we'll assume that it's a utf-8 string
        return val if isinstance(val, unicode) else val.decode('utf-8')

    @classmethod
    def _serialize_column(cls, attr, val):
        if (attr in chain(cls._int_props, cls._float_props) or
            (cls._value_type and cls._value_type in ('float', 'int'))):
            return str(val)
        elif attr in cls._bool_props or (cls._value_type and cls._value_type == 'bool'):
            # n.b. we "truncate" this to a boolean, so truthy but
            # non-boolean values are discarded
            return '1' if val else '0'
        elif attr in cls._pickle_props or (cls._value_type and cls._value_type == 'pickle'):
            return pickle.dumps(val)
        elif attr in cls._json_props or (cls._value_type and cls._value_type == 'json'):
            return json.dumps(val)
        elif (attr in cls._date_props or attr == cls._timestamp_prop or
              (cls._value_type and cls._value_type == 'date')):
            # the _timestamp_prop is handled in _commit(), not here
            validator = cls._get_column_validator(attr)
            if validator in ("DateType", "TimeUUIDType"):
                # pycassa will take it from here
                return val
            else:
                return cls._serialize_date(val)
        elif attr in cls._bytes_props or (cls._value_type and cls._value_type == 'bytes'):
            return val

        return unicode(val).encode('utf-8')

    @classmethod
    def _serialize_date(cls, date):
        return date_serializer.pack(date)

    @classmethod
    def _deserialize_date(cls, val):
        if isinstance(val, datetime):
            date = val
        elif isinstance(val, UUID):
            return convert_uuid_to_time(val)
        elif len(val) == 8: # cassandra uses 8-byte integer format for this
            date = date_serializer.unpack(val)
        else: # it's probably the old-style stringified seconds since epoch
            as_float = float(val)
            date = datetime.utcfromtimestamp(as_float)

        return date.replace(tzinfo=pytz.utc)

    @classmethod
    def _from_serialized_columns(cls, t_id, columns):
        d_columns = dict((attr, cls._deserialize_column(attr, val))
                         for (attr, val)
                         in columns.iteritems())
        return cls._from_columns(t_id, d_columns)

    @classmethod
    def _from_columns(cls, t_id, columns):
        """Given a dictionary of freshly deserialized columns
           construct an instance of cls"""
        t = cls()
        t._orig = columns
        t._id = t_id
        t._committed = True
        return t

    @property
    def _dirty(self):
        return len(self._dirties) or len(self._deletes) or not self._committed

    @will_write
    def _commit(self, write_consistency_level = None):
        if not self._dirty:
            return

        if self._id is None:
            raise TdbException("Can't commit %r without an ID" % (self,))

        if self._committed and self._ttl and self._warn_on_partial_ttl:
            log.warning("Using a full-TTL object %r in a mutable fashion"
                        % (self,))

        if not self._committed:
            # if this has never been committed we should also consider
            # the _orig columns as dirty (but "less dirty" than the
            # _dirties)
            upd = self._orig.copy()
            self._orig.clear()
            upd.update(self._dirties)
            self._dirties = upd

        # Cassandra values are untyped byte arrays, so we need to
        # serialize everything while filtering out anything that's
        # been dirtied but doesn't actually differ from what's already
        # in the DB
        updates = dict((attr, self._serialize_column(attr, val))
                       for (attr, val)
                       in self._dirties.iteritems()
                       if (attr not in self._orig or
                           val != self._orig[attr]))

        # n.b. deleted columns are applied *after* the updates. our
        # __setattr__/__delitem__ tries to make sure that this always
        # works

        if not self._committed and self._timestamp_prop and self._timestamp_prop not in updates:
            # auto-create timestamps on classes that request them

            # this serialize/deserialize is a bit funny: the process
            # of storing and retrieving causes us to lose some
            # resolution because of the floating-point representation,
            # so this is just to make sure that we have the same value
            # that the DB does after writing it out. Note that this is
            # the only property munged this way: other timestamp and
            # floating point properties may lose resolution
            s_now = self._serialize_date(datetime.now(tz))
            now = self._deserialize_date(s_now)

            timestamp_is_typed = self._get_column_validator(self._timestamp_prop) == "DateType"
            updates[self._timestamp_prop] = now if timestamp_is_typed else s_now
            self._dirties[self._timestamp_prop] = now

        if not updates and not self._deletes:
            self._dirties.clear()
            return

        # actually write out the changes to the CF
        wcl = self._wcl(write_consistency_level)
        with self._cf.batch(write_consistency_level = wcl) as b:
            if updates:
                for k, v in updates.iteritems():
                    b.insert(self._id,
                             {k: v},
                             ttl=self._column_ttls.get(k, self._ttl))
            if self._deletes:
                b.remove(self._id, self._deletes)

        self._orig.update(self._dirties)
        self._column_ttls.clear()
        self._dirties.clear()
        for k in self._deletes:
            try:
                del self._orig[k]
            except KeyError:
                pass
        self._deletes.clear()

        if not self._committed:
            self._on_create()
        else:
            self._on_commit()

        self._committed = True

        self.__class__._local_cache.set(self._cache_key(), self)

    def _revert(self):
        if not self._committed:
            raise TdbException("Revert to what?")

        self._dirties.clear()
        self._deletes.clear()
        self._column_ttls.clear()

    def _destroy(self):
        self._cf.remove(self._id,
                        write_consistency_level=self._write_consistency_level)

    def __getattr__(self, attr):
        if isinstance(attr, basestring) and attr.startswith('_'):
            # TODO: I bet this interferes with Views whose column names can
            # start with a _
            try:
                return self.__dict__[attr]
            except KeyError:
                raise AttributeError(attr)

        if attr in self._deletes:
            raise AttributeError("%r has no %r because you deleted it", (self, attr))
        elif attr in self._dirties:
            return self._dirties[attr]
        elif attr in self._orig:
            return self._orig[attr]
        elif attr in self._defaults:
            return self._defaults[attr]
        elif self._partial is not None and attr not in self._partial:
            raise AttributeError("%r has no %r but you didn't request it" % (self, attr))
        else:
            raise AttributeError('%r has no %r' % (self, attr))

    def __setattr__(self, attr, val):
        if attr == '_id' and self._committed:
            raise ValueError('cannot change _id on a committed %r' % (self.__class__))

        if isinstance(attr, basestring) and attr.startswith('_'):
            # TODO: I bet this interferes with Views whose column names can
            # start with a _
            return object.__setattr__(self, attr, val)

        try:
            self._deletes.remove(attr)
        except KeyError:
            pass
        self._dirties[attr] = val
        if attr in self._default_ttls:
            self._column_ttls[attr] = self._default_ttls[attr]

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        if self._partial or other._partial and self._partial != other._partial:
            raise ValueError("Can't compare incompatible partials")

        return self._id == other._id and self._t == other._t

    def __ne__(self, other):
        return not (self == other)

    @property
    def _t(self):
        """Emulate the _t property from tdb_sql: a dictionary of all
           values that are or will be stored in the database, (not
           including _defaults or unrequested properties on
           partials)"""
        ret = self._orig.copy()
        ret.update(self._dirties)
        for k in self._deletes:
            try:
                del ret[k]
            except KeyError:
                pass
        return ret

    # allow the dictionary mutation syntax; it makes working some some
    # keys a bit easier. Go through our regular
    # __getattr__/__setattr__ functions where all of the appropriate
    # work is done
    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __delitem__(self, key):
        try:
            del self._dirties[key]
        except KeyError:
            pass
        try:
            del self._column_ttls[key]
        except KeyError:
            pass
        self._deletes.add(key)

    def _get(self, key, default = None):
        try:
            return self.__getattr__(key)
        except AttributeError:
            if self._partial is not None and key not in self._partial:
                raise AttributeError("_get on unrequested key from partial")
            return default

    def _set_ttl(self, key, ttl):
        assert key in self._dirties
        assert isinstance(ttl, (long, int))
        self._column_ttls[key] = ttl

    def _on_create(self):
        """A hook executed on creation, good for creation of static
           Views. Subclasses should call their parents' hook(s) as
           well"""
        pass

    def _on_commit(self):
        """Executed on _commit other than creation."""
        pass

    @classmethod
    def _all(cls):
        # returns a query object yielding every single item in a
        # column family. it probably shouldn't be used except in
        # debugging
        return Query(cls, limit=None)

    def __repr__(self):
        # it's safe for subclasses to override this to e.g. put a Link
        # title or Account name in the repr(), but they must be
        # careful to check hasattr for the properties that they read
        # out, as __getattr__ itself may call __repr__ in constructing
        # its error messages
        id_str = self._id
        comm_str = '' if self._committed else ' (uncommitted)'
        part_str = '' if self._partial is None else ' (partial)'
        return "<%s %r%s%s>" % (self.__class__.__name__,
                              id_str,
                              comm_str, part_str)

    if debug:
        # we only want this with g.debug because overriding __del__ can play
        # hell with memory leaks
        def __del__(self):
            if not self._committed:
                # normally we'd log this with g.log or something, but we can't
                # guarantee that the thread destructing us has access to g
                print("Warning: discarding uncomitted %r; this is usually a bug" % (self,))
            elif self._dirty:
                print ("Warning: discarding dirty %r; this is usually a bug (_dirties=%r, _deletes=%r)"
                       % (self,self._dirties,self._deletes))
