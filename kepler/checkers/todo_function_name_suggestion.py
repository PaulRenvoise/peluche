from .ml_base import MLBaseChecker


# TODO: Integrate with the ML model
class FunctionNameSuggestion(MLBaseChecker):
    NAME = 'function_name_suggestion'
    DESCRIPTION = 'Suggests another name for a given function.'
    OPTIONS = {}
    MESSAGES = {
        'better-function-name': {
            'template': "Function %r could be renamed to %r.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

        self.model = load_model(PATH)

    def on_def(self, node):
        xp(node.fst())
        original_node_name = node.name
        node.name = 'f'
        xp(node.fst())

        code = node.dumps()

        predictions, confidences = self.model.predict(code)
        candidate_node_name = predictions[0]

        if original_node_name not in predictions and confidence[0] > 0.7:
            self.add_error('better-function-name', node=node, args=(original_node_name, candidate_node_name))
