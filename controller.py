#!/usr/bin/env python3
"""Virtual Gamecube controller"""

__author__="Tyler Westland"

import argparse
# https://python-evdev.readthedocs.io/en/latest/index.html
import evdev
import os
import sys
import time
from typing import List


class GameCubeController():
    def __init__(self, controller_name:str=None):
        if controller_name is None:
            controller_name = "python--GameCube"

        self.ui = evdev.uinput.UInput(name=controller_name)

    def close(self):
        self.ui.close()

    def push_buttons(self, buttons:List[int], seconds:float=0.5) -> None:
        """Push button for specified time
        Parameters
        ----------
        button: List[int] (evdev.ecodes)
            Buttons to push down, and then lift up
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        # Push the buttons down
        for btn in buttons:
            self.ui.write(evdev.events.EV_KEY, btn, 1)
        # Synchronize the pushes
        self.ui.syn()
        # Wait
        time.sleep(seconds)
        # Lift the buttons up
        for btn in buttons:
            self.ui.write(evdev.events.EV_KEY, btn, 0)
        # Synchronize the lifts
        self.ui.syn()

    # Right thumb buttons
    def push_a(self):
        self.push_buttons([evdev.ecodes.BTN_A])

    def push_b(self):
        self.push_buttons([evdev.ecodes.BTN_B])

    def push_x(self):
        self.push_buttons([evdev.ecodes.BTN_X])

    def push_y(self):
        self.push_buttons([evdev.ecodes.BTN_Y])

    # Trigger buttons
    def push_z(self):
        self.push_buttons([evdev.ecodes.BTN_Z])

    def push_left_trigger(self):
        self.push_buttons([evdev.ecodes.BTN_TL])

    def push_right_trigger(self):
        self.push_buttons([evdev.ecodes.BTN_TR])

    # DPAD
    def push_dpad_up(self):
        self.push_buttons([evdev.ecodes.BTN_DPAD_UP])

    def push_dpad_down(self):
        self.push_buttons([evdev.ecodes.BTN_DPAD_DOWN])

    def push_dpad_left(self):
        self.push_buttons([evdev.ecodes.BTN_DPAD_LEFT])

    def push_dpad_right(self):
        self.push_buttons([evdev.ecodes.BTN_DPAD_RIGHT])

    # Control Stick
    def push_control_stick_up(self):
        self.push_buttons([evdev.ecodes.BTN_FORWARD])

    def push_control_stick_back(self):
        self.push_buttons([evdev.ecodes.BTN_BACK])

    def push_control_stick_left(self):
        self.push_buttons([evdev.ecodes.BTN_LEFT])

    def push_control_stick_right(self):
        self.push_buttons([evdev.ecodes.BTN_RIGHT])

    # C Stick
    def push_control_stick_up(self):
        self.push_buttons([evdev.ecodes.BTN_NORTH])

    def push_control_stick_down(self):
        self.push_buttons([evdev.ecodes.BTN_SOUTH])

    def push_control_stick_left(self):
        self.push_buttons([evdev.ecodes.BTN_WEST])

    def push_control_stick_right(self):
        self.push_buttons([evdev.ecodes.BTN_EAST])


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
    parser.add_argument("-cn", "--controller_name", help="Controller name.")
    args = parser.parse_args(args=args)
    return args


def main(controller_name:str=None) -> None:
    """Main function.

    Parameters
    ----------
    controller_name: str
        Controller name
    Raises
    ------
    FileNotFoundError
        Means that the input file was not found.
    """

    GC = GameCubeController(controller_name)

    option = None
    while(option != "q"):
        option = input("Push a button: ")
        buttons = []
        for b in option.split():
            try:
                buttons.append(evdev.ecodes.ecodes[b])
            except:
                print(f"{b} is not a button")
        if len(buttons) > 0:
            GC.push_buttons(buttons, 0.5)

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
