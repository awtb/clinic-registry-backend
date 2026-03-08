import datetime
from typing import Any
from typing import Literal

import jwt

from clinic_registry.core.dto.auth import TokenPairDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.auth import ExpiredTokenError
from clinic_registry.core.errors.auth import InvalidAuthorizationScheme
from clinic_registry.core.errors.auth import InvalidTokenScopeError


class TokenService:
    JWT_ALGORITHM = "HS256"

    def __init__(
        self,
        secret_key: str,
        access_token_exp: int = 30,
        refresh_token_exp: int = 30,
    ) -> None:
        self._secret_key = secret_key
        self._access_token_exp_minutes = access_token_exp
        self._refresh_token_exp_minutes = refresh_token_exp

    def create_token_pair(
        self,
        user_id: str,
        email: str,
        role: UserRole = UserRole.user,
    ) -> TokenPairDTO:
        access_token = self._create_jwt_token(
            scope="access",
            user_id=user_id,
            email=email,
            role=role,
        )
        refresh_token = self._create_jwt_token(
            scope="refresh",
            user_id=user_id,
            email=email,
            role=role,
        )

        return TokenPairDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def extract_token_payload(
        self,
        token: str,
        expected_scope: Literal["access", "refresh"] | None = None,
    ) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError
        except jwt.InvalidTokenError:
            raise InvalidAuthorizationScheme("Token is invalid.")

        token_scope = payload.get("scope")
        if expected_scope is not None and token_scope != expected_scope:
            raise InvalidTokenScopeError

        return payload

    def _create_jwt_token(
        self,
        scope: Literal["access", "refresh"],
        user_id: str,
        email: str,
        role: UserRole = UserRole.user,
    ) -> str:
        payload = self._build_token_payload(scope, user_id, email, role)
        token = jwt.encode(
            payload,
            self._secret_key,
            algorithm=self.JWT_ALGORITHM,
        )

        return token

    def _build_token_payload(
        self,
        scope: Literal["access", "refresh"],
        user_id: str,
        email: str,
        role: UserRole = UserRole.user,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "uid": user_id,
            "scope": scope,
            "email": email,
            "role": role.value,
        }

        if scope == "access":
            payload["exp"] = datetime.datetime.now() + datetime.timedelta(
                minutes=self._access_token_exp_minutes,
            )
        elif scope == "refresh":
            payload["exp"] = datetime.datetime.now() + datetime.timedelta(
                minutes=self._refresh_token_exp_minutes,
            )
        else:
            raise ValueError(f"Invalid scope type {scope}")

        return payload
