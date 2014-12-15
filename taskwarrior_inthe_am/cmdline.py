import argparse
import logging
import os

from configobj import ConfigObj

from .commands import COMMANDS, get_command_list
from .exceptions import IntheAmError


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        epilog=get_command_list(),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'command',
        type=str,
        nargs=1,
        choices=COMMANDS.keys()
    )
    parser.add_argument(
        '--config',
        type=os.path.expanduser,
        default='~/.inthe.am'
    )
    parser.add_argument(
        '--taskrc',
        type=os.path.expanduser,
        default='~/.taskrc'
    )
    parser.add_argument(
        '--loglevel',
        type=str,
        default='INFO'
    )
    args, extra = parser.parse_known_args()

    # Set up a simple console logger
    logging.basicConfig(level=args.loglevel)
    logging.addLevelName(
        logging.WARNING,
        "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING)
    )
    logging.addLevelName(
        logging.ERROR,
        "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR)
    )

    config = ConfigObj(args.config)

    try:
        if args.command[0] in COMMANDS:
            COMMANDS[args.command[0]]['function'](config, args, *extra)
    except IntheAmError as e:
        logger.error(e)

    config.write()
