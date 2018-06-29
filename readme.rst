Taskwarrior Inthe.AM Utility
============================

Utilities to make using Inthe.AM with Taskwarrior just a little easier.

Installation
------------

Using pip::

    pip install taskwarrior-inthe.am

If you do not have ``pip`` installed, follow
`these instructions <https://pip.pypa.io/en/latest/installing.html#install-pip>`_.

Commands
--------

To run any of the below commands from the command-line, run::

    intheam <COMMAND>

``setup``
~~~~~~~~~

Run this command if you'd like to configure your local installation of Taskwarrior to synchronize with Inthe.AM.

``clear_passwords``
~~~~~~~~~~~~~~~~~~~

Clear your saved API key from your keychain.

``sync_bugwarrior``
~~~~~~~~~~~~~~~~~~~

Ask Inthe.AM to synchronize your task list with Bugwarrior.

Getting your API Key
--------------------

To perform any interactions with Inthe.AM you will need to provide an API key.
To find your API key:

1. Log-in to Inthe.AM using a web browser.
2. Go to the 'Configuration' page.
3. Open the 'API Access' section.
