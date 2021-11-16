#!/usr/bin/env python3
"""Virtual Gamecube controller"""

__author__="Tyler Westland"

import argparse
from dataclasses import dataclass, replace
# https://python-evdev.readthedocs.io/en/latest/index.html
import evdev
import json
import os
import random
random.seed()
import sys
import time
from typing import List


@dataclass(frozen=True)
class Action:
    etype: int
    code: int
    set_value: int
    reset_value: int
    seconds: float

# 0 is base, 127 is middle, and 255 max for absolutes axises
ACTIONS = {
        "a": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_SOUTH, 1, 0, 0.25),
        "b": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_EAST, 1, 0, 0.25),
        "x": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_NORTH, 1, 0, 0.25),
        "y": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_WEST, 1, 0, 0.25),
        "z": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_TR, 1, 0, 0.25),
        "l": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_TL2, 1, 0, 0.25),
        "r": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_TR2, 1, 0, 0.25),
        "start": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_START, 1, 0, 0.25),
        "up": Action(evdev.events.EV_ABS, evdev.ecodes.ABS_Y, 0, 127, 0.25),
        "down": Action(evdev.events.EV_ABS, evdev.ecodes.ABS_Y, 255, 127, 0.25),
        "left": Action(evdev.events.EV_ABS, evdev.ecodes.ABS_X, 0, 127, 0.25),
        "right": Action(evdev.events.EV_ABS, evdev.ecodes.ABS_X, 255, 127, 0.25),
        "cup": Action(evdev.events.EV_ABS, evdev.ecodes.ABS_RY, 0, 127, 0.25),
        "cdown": Action(evdev.events.EV_ABS, evdev.ecodes.ABS_RY, 255, 127, 0.25),
        "cleft": Action(evdev.events.EV_ABS, evdev.ecodes.ABS_RX, 0, 127, 0.25),
        "cright": Action(evdev.events.EV_ABS, evdev.ecodes.ABS_RX, 255, 127, 0.25),
        "dup": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_DPAD_UP, 1, 0, 0.25),
        "ddown": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_DPAD_DOWN, 1, 0, 0.25),
        "dleft": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_DPAD_LEFT, 1, 0, 0.25),
        "dright": Action(evdev.events.EV_KEY, evdev.ecodes.BTN_DPAD_RIGHT, 1, 0, 0.25),
    }

# Create short and long versions
extensions = {"t": 1/8, "s": 1/4, "l": 1.0}
additions = dict()
for adjective in extensions:
    for action in ACTIONS:
        additions[f"{adjective}{action}"] = replace(
                ACTIONS[action], seconds=extensions[adjective])
for new_action in additions:
    ACTIONS[new_action] = additions[new_action]


class GameCubeController():
    def __init__(self, clone_parent:str, controller_name:str=None):
        if controller_name is None:
            controller_name = "python--GameCube"

        self.ui = evdev.uinput.UInput.from_device(
                clone_parent,
                name=controller_name)

    def close(self):
        self.ui.close()

    def perform_actions(self, actions:List[Action]) -> None:
        """Push button for specified time
        Parameters
        ----------
        button: List[int] (evdev.ecodes)
            Buttons to push down, and then lift up
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        # FIND MAX SECONDS
        seconds = max(act.seconds for act in actions)
        # Activate the actions
        for act in actions:
            self.ui.write(act.etype, act.code, act.set_value)

        # Synchronize the activations
        self.ui.syn()

        # Wait
        time.sleep(seconds)

        # Reset the actions
        for act in actions:
            self.ui.write(act.etype, act.code, act.reset_value)

        # Synchronize the lifts
        self.ui.syn()

        # Synchronize the resets
        self.ui.syn()

def parse_arguments(args=None) -> None:
    """Returns the parsed arguments.
    Parameters
    ----------
    args: List of strings to be parsed by argparse.
        The default None results in argparse using the values passed into
        sys.args.
    """
    parser = argparse.ArgumentParser(
            description="Create and control a virtual gamecube controller.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("clone_parent", help="Controller to clone from.")
    parser.add_argument("-cn", "--controller_name", help="Controller name.")
    args = parser.parse_args(args=args)
    return args


def main(clone_parent:str, controller_name:str=None) -> None:
    """Main function.

    Parameters
    ----------
    clone_parent: str
        Controller to clone from.
    controller_name: str
        Controller name.
    Raises
    ------
    FileNotFoundError
        Means that the input file was not found.
    """
    if controller_name is None:
        controller_name = "RANDOM"

    GC = GameCubeController(clone_parent, controller_name)

    while(True):
        # Wait 0.25 seconds between button presses
        time.sleep(0.25)
        # Press a lot of the time
        if random.randint(1,100)  <= 40:
            GC.perform_actions([ACTIONS["a"]])
        else:
            def pick_a_action_besides_start():
                action = "start"
                while("start" in action):
                    action = random.choice(list(ACTIONS.keys()))
                return action

            actions = [ACTIONS[pick_a_action_besides_start()]]
            # Pick a second action, maybe?
            if random.choice([True, False]):
                actions.append(ACTIONS[pick_a_action_besides_start()])

            GC.perform_actions(actions)
    GC.close()

    return None


def cli_interface() -> None:
    """Get program arguments from command line and run main"""
    args = parse_arguments()
    try:
        main(**vars(args))
        sys.exit(0)
    except FileNotFoundError as exp:
        print(exp, file=sys.stderr)
        sys.exit(-1)


# Execute only if this file is being run as the entry file.
if __name__ == "__main__":
    cli_interface()
