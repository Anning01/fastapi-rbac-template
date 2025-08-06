from datetime import datetime, timedelta
from enum import StrEnum

import jwt

from config import settings
from schemas.auth import JWTPayload, JWTDecoder


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"

def create_access_token(token_type: TokenType, data: JWTPayload) -> str:
    payload = data.model_dump().copy()
    if token_type == TokenType.ACCESS:
        expire = datetime.utcnow() + timedelta(
            days=settings.ACCESS_TOKEN_EXPIRE_DAYS
        )
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    payload["type"] = token_type.value
    payload["exp"] = expire
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: TokenType) -> JWTDecoder:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload["type"] != token_type.value:
        raise jwt.InvalidTokenError("Token类型不匹配")

    if payload["exp"] and datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
        raise jwt.ExpiredSignatureError("Token已过期")

    return JWTDecoder(**payload)
