#
#  GoogleFindMyTools - A set of tools to interact with the Google Find My API
#  Copyright © 2024 Leon Böttger. All rights reserved.
#

import ssl
import sys
import gpsoauth

from Auth.auth_flow import request_oauth_account_token_flow
from Auth.fcm_receiver import FcmReceiver
from Auth.token_cache import get_cached_value_or_set, set_cached_value
from Auth.username_provider import get_username, username_string

# Python 3.14 SSL compatibility fix
if sys.version_info >= (3, 10):
    import urllib3
    from urllib3.util.ssl_ import create_urllib3_context

    # Monkey-patch urllib3 to use a more lenient SSL context
    class CustomSSLContextHTTPAdapter(urllib3.util.ssl_.SSLContext):
        pass

    original_create_urllib3_context = create_urllib3_context

    def patched_create_urllib3_context(*args, **kwargs):
        context = original_create_urllib3_context(*args, **kwargs)
        # Allow TLS 1.2+ to work with older servers
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        return context

    urllib3.util.ssl_.create_urllib3_context = patched_create_urllib3_context
    urllib3.util.create_urllib3_context = patched_create_urllib3_context


def _generate_aas_token():
    username = get_username()
    android_id = FcmReceiver().get_android_id()
    token = request_oauth_account_token_flow()

    aas_token_response = gpsoauth.exchange_token(username, token, android_id)
    aas_token = aas_token_response['Token']

    if 'Email' in aas_token_response:
        email = aas_token_response['Email']
        set_cached_value(username_string, email)

    return aas_token


def get_aas_token():
    return get_cached_value_or_set('aas_token', _generate_aas_token)


if __name__ == '__main__':
    print(get_aas_token())