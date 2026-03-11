from datetime import datetime, timedelta

import jwt
from jwt import PyJWTError

from abstractions.utility import IUtility
from start_utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)


class JWTUtility(IUtility):
    """
    Utility for creating and decoding JWT tokens for authentication.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
        self._urn: str = urn
        self._user_urn: str = user_urn
        self._api_name: str = api_name
        self._user_id: str = user_id
        self.logger.debug(
            f"JWTUtility initialized for "
            f"user_id={user_id}, urn={urn}, api_name={api_name}"
        )

    @property
    def urn(self):
        return self._urn

    @urn.setter
    def urn(self, value):
        self._urn = value

    @property
    def user_urn(self):
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value):
        self._user_urn = value

    @property
    def api_name(self):
        return self._api_name

    @api_name.setter
    def api_name(self, value):
        self._api_name = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    def create_access_token(self, data: dict) -> str:
        """
        Create a JWT access token with an expiration time.
        Args:
            data (dict): Data to encode in the token payload.
        Returns:
            str: Encoded JWT token as a string.
        """
        self.logger.info("Creating access token")

        to_encode = data.copy()
        if ACCESS_TOKEN_EXPIRE_MINUTES:
            expire = datetime.now() + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        else:
            expire = datetime.now() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    def decode_token(self, token: str) -> dict[str, str]:
        """
        Decode a JWT token and return its payload.
        Args:
            token (str): The JWT token to decode.
        Returns:
            dict: Decoded payload from the token.
        Raises:
            PyJWTError: If decoding fails or the token is invalid.
        """
        self.logger.info("Decoding JWT token")
        try:

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload

        except PyJWTError as err:
            raise err
