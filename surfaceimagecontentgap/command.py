# -*- coding: utf-8 -*-

"""Command module to the bot."""

import datetime


ALLOWED_TYPES = ["Category", "Template"]


class SicgCommand(object):

    """Command to sicg bot."""

    def __init__(self, user, command, argname):
        """Constructor.

        Args:
            user (str): user name that sends the Command
            command (str): command type. Should be in ALLOWED_TYPES
            name (str): argument of the command (e.g. category or template)
        """
        if command not in ALLOWED_TYPES:
            msg = "Command value should be in %s, was %s" % (ALLOWED_TYPES,
                                                             command)
            raise ValueError(msg)
        self.user = user
        self.command = command
        self.argname = argname
        self.datetime = datetime.datetime.now()

    def send(self, filename):
        """Send command to queue file."""
        pass

    def __repr__(self):
        """Representation."""
        repr_message = "<SicgCommand object %s cmd: %s by %s at %s>"
        return repr_message % (id(self),
                               self.command,
                               self.user,
                               self.datetime)
