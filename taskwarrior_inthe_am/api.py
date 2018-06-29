import getpass
import logging

import keyring
import requests
from six.moves import input

from .exceptions import ConfigurationError


logger = logging.getLogger(__name__)


def response_was_yes(response):
    if response.upper() and response.upper()[0] == 'Y':
        return True
    return False


def get_api_connection(config, interactive=True):
    old_api_key = keyring.get_password(
        'taskwarrior_inthe.am',
        'api_key',
    )
    api_key = keyring.get_password(
        'taskwarrior_inthe.am',
        'api_v2_key',
    )
    if old_api_key and not api_key:
        logger.warning(
            "You currently have an Api Key stored for an earlier version "
            "of Inthe.AM.  Please go to your control panel to find out "
            "what your new API key is.",
        )
    if not api_key:
        if interactive:
            api_key = getpass.getpass(
                "Please enter your API key: (Input hidden) "
            )
            if not api_key:
                raise ConfigurationError(
                    "No API key supplied at prompt.  Please enter one."
                )
            save_to_keyring = input("Save to keyring? (N/Y): ")
            if response_was_yes(save_to_keyring):
                keyring.set_password(
                    'taskwarrior_inthe.am',
                    'api_v2_key',
                    api_key
                )
        else:
            raise ConfigurationError(
                "API key not available.  Please save one to your keyring."
            )

    s = requests.Session()
    s.headers.update({
        'Authorization': 'Token {}'.format(api_key)
    })
    s.headers['User-Agent'] = ' '.join(
        [
            s.headers['User-Agent'],
            'Inthe.AM Client'
        ]
    )

    status = s.get('https://inthe.am/api/v2/user/status/').json()
    if not status.get('logged_in'):
        raise ConfigurationError(
            "The supplied API key is invalid."
        )

    return s
