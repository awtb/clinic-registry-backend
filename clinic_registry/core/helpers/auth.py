import datetime
from typing import Any
from typing import Literal

import bcrypt
import jwt

from clinic_registry.core.dto.auth import TokenPairDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.auth import ExpiredTokenError
from clinic_registry.core.errors.auth import InvalidAuthorizationScheme


class AuthHelper:
    def __init__(
        self,
        secret_key: str,
        hashing_algorithm: str,
        access_token_exp: int = 30,
        refresh_token_exp: int = 30,
    ) -> None:
        self._secret_key = secret_key
        self._hashing_algorithm = hashing_algorithm
        self._access_token_exp_minutes = access_token_exp
        self._refresh_token_exp_minutes = refresh_token_exp

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        return hashed_password.decode()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

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
            algorithm=self._hashing_algorithm,
        )

        return token

    def extract_token_payload(
        self,
        token: str,
    ) -> dict[str, str]:
        try:
            payload = jwt.decode(
                token, self._secret_key, algorithms=[self._hashing_algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError
        except jwt.InvalidTokenError:
            raise InvalidAuthorizationScheme("Token is invalid.")

        return payload

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
                minutes=self._access_token_exp_minutes
            )
        elif scope == "refresh":
            payload["exp"] = datetime.datetime.now() + datetime.timedelta(
                minutes=self._refresh_token_exp_minutes
            )
        else:
            raise ValueError(f"Invalid scope type {scope}")

        return payload
