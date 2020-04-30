class Message:
    """
    TODO
    """
    TYPES = {'info', 'convention', 'suggestion', 'refactor', 'warning', 'error', 'fatal'}
    TYPES_SHORT_TO_LONG = {t[0].upper(): t for t in TYPES}
    TYPES_LONG_TO_SHORT = {t: t[0].upper() for t in TYPES}

    def __init__(self, error_id, content, position):
        """
        TODO
        """
        self.message = f"{position.line}:{position.column} - {error_id}: {content}"

    def __repr__(self):
       return f"{self.message}"
