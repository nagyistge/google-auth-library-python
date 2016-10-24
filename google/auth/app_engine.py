# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google App Engine standard environment credentials.

This module provides authentication for application running on App Engine in
the standard environment using the `App Identity API`_.


.. _App Identity API:
    https://cloud.google.com/appengine/docs/python/appidentity/
"""

import datetime

from google.auth import _helpers
from google.auth import credentials

try:
    from google.appengine.api import app_identity
except ImportError:
    app_identity = None


class Credentials(credentials.Scoped, credentials.Signing,
                  credentials.Credentials):
    """App Engine standard environment credentials.

    These credentials use the App Engine App Identity API to obtain access
    tokens.
    """

    def __init__(self, scopes=None, service_account_id=None):
        """
        Args:
            scopes (Sequence[str]): Scopes to request from the App Identity
                API.
            service_account_id (str): The service account ID passed into
                :func:`google.appengine.api.app_identity.get_access_token`.
                If not specified, the default application service account
                ID will be used.

        Raises:
            EnvironmentError: If the App Engine APIs are unavailable.
        """
        if app_identity is None:
            raise EnvironmentError(
                'The App Engine APIs are not available.')

        super(Credentials, self).__init__()
        self._scopes = scopes
        self._service_account_id = service_account_id

    @_helpers.copy_docstring(credentials.Credentials)
    def refresh(self, request):
        # pylint: disable=unused-argument
        token, ttl = app_identity.get_access_token(
            self._scopes, self._service_account_id)
        expiry = _helpers.utcnow() + datetime.timedelta(seconds=ttl)

        self.token, self.expiry = token, expiry

    @property
    def requires_scopes(self):
        """Checks if the credentials requires scopes.

        Returns:
            bool: True if there are no scopes set otherwise False.
        """
        return not self._scopes

    @_helpers.copy_docstring(credentials.Scoped)
    def with_scopes(self, scopes):
        return Credentials(
            scopes=scopes, service_account_id=self._service_account_id)

    @_helpers.copy_docstring(credentials.Signing)
    def sign_bytes(self, message):
        return app_identity.sign_blob(message)