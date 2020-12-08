try:
    from ._rest_framework_jwt_impl import (JWTAuthentication,
                                           get_user_id_from_payload_handler,
                                           patch_jwt_settings)
except ImportError:
    pass

from django.utils.functional import cached_property
from jose import jwt

from .settings import api_token_auth_settings


class JWT:
    def __init__(self, encoded_jwt):
        self._encoded_jwt = encoded_jwt

    def validate(self, keys, audience):
        """Verifies the JWT's signature using the provided keys,
        and validates the claims, raising an exception if anything fails."""

        options = {
            "require_aud": True,
            "require_exp": True,
        }

        self._claims = jwt.decode(
            self._encoded_jwt, keys, options=options, audience=audience
        )

    @property
    def issuer(self):
        """Returns the "iss" claim value."""
        return self.claims["iss"]

    @property
    def claims(self):
        """Returns all the claims of the JWT as a dictionary."""
        if not hasattr(self, "_claims"):
            self._claims = jwt.get_unverified_claims(self._encoded_jwt)
        return self._claims

    def has_api_scope_with_prefix(self, prefix):
        """Checks if there is an API scope with the given prefix.
        The name of the claims field where API scopes are looked for is
        determined by the OIDC_API_TOKEN_AUTH['API_AUTHORIZATION_FIELD']
        setting."""
        return any(
            x == prefix or x.startswith(prefix + ".")
            for x in self._authorized_api_scopes
        )

    @cached_property
    def _authorized_api_scopes(self):
        def is_list_of_non_empty_strings(value):
            return isinstance(value, list) and all(
                isinstance(x, str) and x for x in value
            )

        api_scopes = self.claims.get(api_token_auth_settings.API_AUTHORIZATION_FIELD)
        return set(api_scopes) if is_list_of_non_empty_strings(api_scopes) else set()
