def is_quarantined(self):
    pass


def related_subreddits(self):
    try:
        multi = LabeledMulti._byID(self._related_multipath)
    except tdb_cassandra.NotFound:
        multi = None
    return  [sr.name for sr in multi.srs] if multi else []


def related_subreddits(self, related_subreddits):
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
