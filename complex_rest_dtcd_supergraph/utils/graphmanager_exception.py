NO_ID = 0
NO_GRAPH = 1
NAME_EXISTS = 2
NO_TITLE = 3


class GraphManagerException(Exception):

    def __init__(self, problem, *args):
        msg = 'no message'
        if problem == NO_ID:
            msg = 'No id provided'
        elif problem == NO_GRAPH:
            msg = f"No graph found with id -> {args[0]}"
        elif problem == NAME_EXISTS:
            msg = f"Name -> {args[0]} already exists"
        elif problem == NO_TITLE:
            msg = f"No title found in request body"
        super().__init__(msg)