class IAMError(Exception):
    pass


class AuthenticationError(IAMError):
    pass


class AuthorizationError(IAMError):
    pass