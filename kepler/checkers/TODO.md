https://lintlyci.github.io/Flake8Rules/rules/E714.html
https://lintlyci.github.io/Flake8Rules/rules/E713.html
https://lintlyci.github.io/Flake8Rules/rules/E721.html
https://github.com/PyCQA/pydocstyle
https://github.com/terrencepreilly/darglint

'lstrip-rstrip': }
    'template': "Replace call to `.lstrip().rstrip()` by `.strip()` as it is 2x faster.",
    'description': '',
}
'redundant-strip': {
    'template': "Redudant usage of {!r} with `.strip()`.",
    'description': '',
}

'choice-sample': {
    'template': "Replace call to `{!r}` by `random.choice({!r})` to make it simpler.",
    'description': """
    """,
},
