class TaskNotFoundError(Exception):
    pass


class InvalidTaskStatusTransitionError(Exception):
    pass


class TaskAccessDeniedError(Exception):
    pass


class InvalidProgressError(Exception):
    pass


class DeadlineValidationError(Exception):
    pass


class CommentNotFoundError(Exception):
    pass


class ParentTaskNotFoundError(Exception):
    pass


class ProjectServiceUnavailableError(Exception):
    pass
