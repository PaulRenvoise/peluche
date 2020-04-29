if 'a' in 'str':
    pass

if 1 in {1, 2, 3}:
    pass

if 1 not in {1, 3}:
    pass

lst = ['b', 'c', 'd']
if 'a' in lst:
    pass

if 1 in [1, 2, 3]:  # faster-membership-testing
    pass

if 1 not in [2, 3]:  # faster-membership-testing
    pass

if 'a' in ('a', 'b', 'c'):  # faster-membership-testing
    pass

if 'a' not in ('b', 'c'):  # faster-membership-testing
    pass
