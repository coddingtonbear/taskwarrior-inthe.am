import os
from setuptools import setup, find_packages
import uuid

from taskwarrior_inthe_am import __version__ as version_string


requirements_path = os.path.join(
    os.path.dirname(__file__),
    'requirements.txt',
)
try:
    from pip.req import parse_requirements
    requirements = [
        str(req.req) for req in parse_requirements(
            requirements_path,
            session=uuid.uuid1()
        )
    ]
except ImportError:
    requirements = []
    with open(requirements_path, 'r') as in_:
        requirements = [
            req for req in in_.readlines()
            if not req.startswith('-')
            and not req.startswith('#')
        ]


setup(
    name='taskwarrior-inthe.am',
    version=version_string,
    url='https://github.com/coddingtonbear/taskwarrior-inthe.am',
    description=(
        'Tools for making using Inthe.AM with Taskwarrior easier.'
    ),
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'intheam = taskwarrior_inthe_am.cmdline:main'
        ],
    },
)
