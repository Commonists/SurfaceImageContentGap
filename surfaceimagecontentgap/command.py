# -*- coding: utf-8 -*-

"""Command module to the bot."""

import datetime
from ConfigParser import RawConfigParser
import os


ALLOWED_TYPES = ["Category", "Template"]


class SicgCommand(object):

    """Command to sicg bot."""

    def __init__(self, user, command, argname, date_time=None):
        """Constructor.

        Args:
            user (str): user name that sends the Command
            command (str): command type. Should be in ALLOWED_TYPES
            name (str): argument of the command (e.g. category or template)
            date_time (optional:datetime.datetime): creation date of the
                command
        """
        if command not in ALLOWED_TYPES:
            msg = "Command value should be in %s, was %s" % (ALLOWED_TYPES,
                                                             command)
            raise ValueError(msg)
        self.user = user
        self.command = command
        self.argname = argname
        if date_time is None:
            self.datetime = datetime.datetime.now()
        else:
            self.datetime = date_time

    def send(self, filename):
        """Send command to queue file."""
        with open(filename, "a") as commandfile:
            msg = ";;;".join([str(self.datetime),
                              self.user,
                              self.command,
                              self.argname])
            commandfile.write(msg + "\n")

    def check(self, authorized_users):
        """Return whether the command is authorized given a list of users."""
        return self.user in authorized_users

    @classmethod
    def fromtext(cls, text):
        """Command from file format used in command_file."""
        fields = [textfield.strip() for textfield in text.split(";;;")]
        return cls(fields[1], fields[2], fields[3], date_time=fields[0])

    def __repr__(self):
        """Representation."""
        repr_message = "<SicgCommand object %s cmd: %s by %s at %s>"
        return repr_message % (id(self),
                               self.command,
                               self.user,
                               self.datetime)


class SicgExecutableObject(object):

    """Object containing information to run the bot."""

    def __init__(self, configfile):
        """Constructor."""
        configparser = RawConfigParser()
        configparser.read(configfile)
        self.path = configparser.get("command", "path")
        self.user_file = os.path.join(self.path, "users.txt")
        self.command_file = os.path.join(self.path, "commands.txt")
        self.log_file = os.path.join(self.path, "log.txt")
        self.userlist = None

    def users(self):
        """List of users that are authorized to use the bot.

        As the user list should not change so much we are caching it."""
        if self.userlist is None:
            with open(self.user_file) as userfile:
                self.userlist = [line.strip()
                                 for line in userfile.readlines()]
        return self.userlist

    def commands(self):
        """List of commands on the command file."""
        with open(self.command_file) as commandfile:
            return [SicgCommand.fromtext(line.strip())
                    for line in commandfile.readlines()]


class SicgScheduler(SicgExecutableObject):

    """Scheduler class."""

    def __init__(self, configfile):
        """Constructor."""
        SicgExecutableObject.__init__(self, configfile)

    def addcommand(self, command):
        """Add a command to the command file."""
        if command.check(self.users()):
            command.send(self.command_file)

    def runnext(self):
        """Run the first command from the file and removes it from the file."""
        pass
