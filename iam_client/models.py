from pydantic import BaseModel
from typing import List, Optional


class TokenPayload(BaseModel):
    sub: str
    email: str
    roles: List[str] = []
    permissions: List[str] = []
    exp: Optional[int] = None


class UserContext(BaseModel):
    user_id: str
    email: str
    roles: List[str]
    permissions: List[str]
    valid: bool

    