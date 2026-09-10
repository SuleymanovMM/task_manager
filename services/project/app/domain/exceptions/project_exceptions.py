class ProjectNotFoundError(Exception): pass


class ProjectAccessDeniedError(Exception): pass


class ProjectAlreadyArchivedError(Exception): pass


class TeamNotFoundError(Exception): pass


class TeamAccessDeniedError(Exception): pass


class MemberAlreadyExistsError(Exception): pass


class InvitationNotFoundError(Exception): pass


class InvitationExpiredError(Exception): pass


class InvalidInvitationStatusError(Exception): pass


class CannotInviteSelfError(Exception): pass
