class WorkspaceError(Exception):
    pass


class DiffError(WorkspaceError):
    pass


class GraphError(WorkspaceError):
    pass


class VCSError(WorkspaceError):
    pass
