from typing import List


def has_role(user_roles: List[str], required: str) -> bool:
    return required in user_roles


def has_any_role(user_roles: List[str], required: List[str]) -> bool:
    return any(r in user_roles for r in required)


def has_permission(user_permissions: List[str], required: str) -> bool:
    return required in user_permissions


def require_role(user_roles: List[str], role: str):
    if role not in user_roles:
        raise PermissionError(f"Missing role: {role}")