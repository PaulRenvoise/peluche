from .store import Store as Storable

class Message(Storable):
    TYPES = {'info', 'convention', 'suggestion', 'refactor', 'warning', 'error', 'fatal'}
    TYPES_SHORT_TO_LONG = {t[0].upper(): t for t in TYPES}
    TYPES_LONG_TO_SHORT = {t: t[0].upper() for t in TYPES}

    def __init__(self, error_id, content, node=None):
        line = node.absolute_top_line
        column = node.absolute_left_column

        self.message = f"{line}:{column} - {error_id}: {content}"
        self.markup = 'MARKUP'

    def __repr__(self):
       return f"{self.message}\n{self.markup}"
