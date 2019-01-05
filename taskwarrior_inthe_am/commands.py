import argparse
import codecs
from distutils.version import LooseVersion
import logging
import os

from taskw.warrior import TaskWarriorShellout
import keyring

from .api import get_api_connection
from .exceptions import ConfigurationError, IncompatibleVersionError
from .taskwarrior import get_taskwarrior_config


COMMANDS = {}

logger = logging.getLogger(__name__)


def get_command_list():
    command_lines = []
    for name, info in COMMANDS.items():
        if info['is_alias']:
            continue
        message = "{0}: {1}".format(name, info['description'])
        if info['aliases']:
            message = message + '; aliases: {0}'.format(
                ', '.join(info['aliases'])
            )
        command_lines.append(message)
    prolog = 'available commands:\n'
    return prolog + '\n'.join(['  ' + cmd for cmd in command_lines])


def command(desc, name=None, aliases=None):
    if aliases is None:
        aliases = []

    def decorator(fn):
        main_name = name if name else fn.__name__
        command_details = {
            'function': fn,
            'description': desc,
            'is_alias': False,
            'aliases': [],
        }

        COMMANDS[main_name] = command_details
        for alias in aliases:
            COMMANDS[alias] = command_details.copy()
            COMMANDS[alias]['is_alias'] = True
            COMMANDS[main_name]['aliases'].append(alias)
        return fn
    return decorator


@command("Set up Taskwarrior to sync issues with your Inthe.AM account.")
def setup(config, args, *extra, **kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data-dir',
        type=os.path.expanduser,
        default='~/.tasks'
    )
    extra_args = parser.parse_args(extra)

    twversion = TaskWarriorShellout.get_version()
    if twversion < LooseVersion('2.3'):
        raise IncompatibleVersionError(
            "Only Taskwarrior versions 2.3 and above support "
            "synchronization with a task server.  Please upgrade "
            "and try again."
        )

    api = get_api_connection(config)
    twconfig = get_taskwarrior_config(args.taskrc)

    # Make sure that none of these settings are already set.
    necessary_settings = ['certificate', 'key', 'ca', 'trust']
    if 'taskd' in twconfig:
        for setting in necessary_settings:
            if setting in twconfig['taskd'] and twconfig['taskd'][setting]:
                raise ConfigurationError(
                    "Cannot configure!  Setting taskd.%s is already "
                    "configured in your TaskRC file at %s." % (
                        setting,
                        args.taskrc
                    )
                )

    # Create the data directory if necessary
    data_location = os.path.expanduser(
        twconfig.get('data', {}).get('location', extra_args.data_dir)
    )
    try:
        os.mkdir(data_location)
        logger.info(
            "Data directory %s created.",
            data_location
        )
    except OSError:
        logger.warning(
            "Data directory %s already exists.",
            data_location
        )

    # Get user information
    status = api.get('https://inthe.am/api/v2/user/status/').json()

    # Write certificate files
    files = {
        'private.cert': '/api/v2/user/my-certificate/',
        'private.key': '/api/v2/user/my-key/',
        'ca.cert.pem': '/api/v2/user/ca-certificate/',
    }
    for filename, url in files.items():
        full_path = os.path.join(data_location, filename)
        with codecs.open(full_path, 'w', encoding='utf-8') as out:
            full_url = 'https://inthe.am%s' % url
            content = api.get(full_url).content
            out.write(content)
            logger.info(
                "File '%s' written to %s.",
                filename,
                full_path,
            )

    # Write configuration
    taskrc_path = os.path.expanduser(args.taskrc)
    with codecs.open(taskrc_path, 'a', encoding='utf-8') as out:
        lines = []
        if twconfig.get('data', {}).get('location') is None:
            lines.append(
                'data.location=%s' % data_location
            )
        lines.extend([
            'taskd.certificate=%s' % os.path.join(
                data_location,
                'private.cert',
            ),
            'taskd.key=%s' % os.path.join(
                data_location,
                'private.key',
            ),
            'taskd.ca=%s' % os.path.join(
                data_location,
                'ca.cert.pem',
            ),
            'taskd.server=%s' % status['taskd_server'],
            'taskd.credentials=%s' % status['taskd_credentials'],
        ])
        if twversion >= LooseVersion('2.4'):
            lines.append(
                'taskd.trust=ignore hostname'
            )
        for line in lines:
            out.write('%s\n' % line)

        logger.info(
            "Configuration written to %s.",
            taskrc_path,
        )

    # Synchronizing with Inthe.AM
    logger.info(
        "Performing initial sync..."
    )
    warrior = TaskWarriorShellout(
        config_filename=taskrc_path
    )
    warrior.sync()
    logger.info(
        "Taskwarrior has successfully been configured to synchronize with "
        "Inthe.AM; In the future, just run `task sync` to synchronize."
    )


@command("Clear saved passwords and API keys.")
def clear_passwords(config, args, *extra, **kwargs):
    keyring.delete_password(
        'taskwarrior_inthe.am',
        'api_key',
    )
    keyring.delete_password(
        'taskwarrior_inthe.am',
        'api_v2_key',
    )


@command('Sync tasks with bugwarrior.')
def sync_bugwarrior(config, args, *extra, **kwargs):
    api = get_api_connection(config)
    result = api.post('https://inthe.am/api/v2/tasks/bugwarrior/sync/')
    result.raise_for_status()

    logger.info("Synchronization with bugwarrior has been queued.")
