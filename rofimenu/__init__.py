"""A python library that can be used to create and launch menus using the rofi tool."""

import subprocess
import locale
import os

ENV = os.environ.copy()
ENV['LC_ALL'] = 'C'
ENC = locale.getpreferredencoding()


def evaluate_path(path):
    """Expands a path in a shell like fashion: $HOME/.config will become /home/userxxxx/.config"""
    arg = f"echo {path}"

    res = subprocess.run(
        arg, shell=True, capture_output=True, check=False, encoding=ENC)

    if res.returncode != 0:
        return path

    return res.stdout.strip()


class Action:
    """A helper class that represents a action that can be selected from the menu"""

    def __init__(self, name, action):
        self.name = name
        self.action = action

    def exec(self):
        if self.action != "":
            subprocess.run(self.action, shell=True, check=True, encoding=ENC)

    def __str__(self) -> str:
        return self.name


class RofiMenu:
    """A class to build and launch menus with the rofi tool"""

    def __init__(self, name, config=None, prompt=None):
        self.name = name
        self.actions = []
        self.config = evaluate_path(config)
        self.prompt = prompt

        if self.prompt is None:
            self.prompt = ""

    def add(self, name, cmd):
        """Adds a new entry to the menu"""
        self.actions.append(Action(name, cmd))

    def extend(self, dict):
        """Adds multiple entries to the menu, 
        where the key of the dictionary is the name and the value the command
        """
        for (key, val) in dict.items():
            self.add(key, val)

    def launch(self):
        """Launches the menu and executes the selected entry"""
        index = self._launch_rofi()
        if index is not None:
            self.actions[index].exec()

    def _launch_rofi(self):
        """Launches rofi and returns the index of the selected option"""

        args = [
            "rofi",
            "-dmenu",         # run in dmenu mode
            "-i",             # make rofi case insensitive
            "-format",  "i",  # this option makes rofi return the index of the selection
            "-window-title", self.name,
            "-p", self.prompt,
        ]

        if self.config is not None:
            args.extend(["-config", self.config])

        input = "\n".join([str(x) for x in self.actions])

        res = subprocess.run(args,
                             capture_output=True,
                             check=False,
                             input=input,
                             encoding=ENC,
                             env=ENV)

        # user cancled the selection
        if res.returncode != 0:
            return None

        index = int(res.stdout.rstrip())

        # user enterd a custom selection
        if index < 0:
            return None

        return index
