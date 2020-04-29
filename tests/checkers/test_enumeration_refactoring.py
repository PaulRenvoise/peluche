for c in lst:
    print(c)

for c in 'abc':
    print(c)

for i, item in enumerate(lst):
    yield (i, item)

for i, _ in enumerate(lst):  # Why not?
    yield lst[i]

for i in range(custom_len(lst)):  # Cannot predict what custom_len will return
    yield lst[i]

for i in range(1, len(lst)):  # Cannot start iterating at the nth item using enumerate
    yield lst[i]

for i in range(0, len(lst), 2):  # Cannot introduce a step using enumerate
    yield lst[i]

for i in range(len(lst)):  # faster-enumeration
    yield other[i]

for i in range(len([1, 2, 3, 4])):  # faster-enumeration
    yield i

for i in range(len(lst)):  # faster-enumeration
    yield lst[i + 1]

for i in range(len(lst)):  # faster-enumeration
    yield lst[i]

for i in range(0, len(lst)):  # faster-enumeration
    yield lst[i]
