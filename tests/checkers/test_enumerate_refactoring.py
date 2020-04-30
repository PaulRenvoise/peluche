for i in range(custom_len(lst)):  # Cannot predict what custom_len will return
    yield lst[i]

for i in range(1, len(lst)):  # Cannot start iterating at the nth item using enumerate
    yield lst[i]

for i in range(0, len(lst), 2):  # Cannot introduce a step using enumerate
    yield lst[i]

for i in range(len(lst)):  # range-enumerate
    yield other[i]

for i in range(len([1, 2, 3, 4])):  # range-enumerate
    yield i

for i in range(len(lst)):  # range-enumerate
    yield lst[i + 1]

for i in range(len(lst)):  # range-enumerate
    yield lst[i]

for i in range(0, len(lst)):  # range-enumerate
    yield lst[i]
