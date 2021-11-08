#!/usr/bin/env python3
"""Virtual Gamecube controller"""

__author__="Tyler Westland"

import argparse
# https://python-evdev.readthedocs.io/en/latest/index.html
import evdev
import json
import os
import random
random.seed()
import sys
import time
from typing import List


class GameCubeController():
    def __init__(self, clone_parent:str, controller_name:str=None):
        if controller_name is None:
            controller_name = "python--GameCube"

        self.ui = evdev.uinput.UInput.from_device(
                clone_parent,
                name=controller_name)

    def close(self):
        self.ui.close()

    def push_buttons(self, buttons:List[int], seconds:float=0.25) -> None:
        """Push button for specified time
        Parameters
        ----------
        button: List[int] (evdev.ecodes)
            Buttons to push down, and then lift up
        seconds: float = 0.25
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

    def push_sticks(self, sticks:List[int], values:List[int], seconds:float=0.25)\
            -> None:
        """Push button for specified time
        Parameters
        ----------
        sticks: List[int] (evdev.ecodes)
            Sticks to manipulate, and then reset.
        values: List[int] 
            Values to set the sticks to. Should be the same size as sticks
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        # Push the sticks down
        for i in range(len(sticks)):
            self.ui.write(evdev.events.EV_ABS, sticks[i], values[i])

        # Synchronize the pushes
        self.ui.syn()

        # Wait
        time.sleep(seconds)

        # Move sticks back to center
        # Since this is intended to clone a PS3 controller that's 127
        for i in range(len(sticks)):
            self.ui.write(evdev.events.EV_ABS, sticks[i], 127)

        # Synchronize the lifts
        self.ui.syn()

    # Start button
    def push_start(self, seconds:float=0.25):
        """Push Start button for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_START], seconds)

    # Right thumb buttons
    def push_a(self, seconds:float=0.25):
        """Push A button for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_SOUTH], seconds)

    def push_b(self, seconds:float=0.25):
        """Push B button for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_EAST], seconds)

    def push_x(self, seconds:float=0.25):
        """Push X button for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_NORTH], seconds)

    def push_y(self, seconds:float=0.25):
        """Push Y button for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_WEST], seconds)

    # Trigger buttons
    def push_z(self, seconds:float=0.25):
        """Push Z button for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_TR], seconds)

    def push_left_trigger(self, seconds:float=0.25):
        """Push left trigger for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_TL2], seconds)

    def push_right_trigger(self, seconds:float=0.25):
        """Push right trigger for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_TR2], seconds)

    # DPAD
    def push_dpad_up(self, seconds:float=0.25):
        """Push DPad up for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_DPAD_UP], seconds)

    def push_dpad_down(self, seconds:float=0.25):
        """Push DPad down for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_DPAD_DOWN], seconds)

    def push_dpad_left(self, seconds:float=0.25):
        """Push DPad left for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_DPAD_LEFT], seconds)

    def push_dpad_right(self, seconds:float=0.25):
        """Push DPad right for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_DPAD_RIGHT], seconds)

    # Control Stick
    def push_control_stick_up(self, seconds:float=0.25):
        """Push Control Stick up for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_sticks([evdev.ecodes.ABS_Y], [0], seconds)

    def push_control_stick_down(self, seconds:float=0.25):
        """Push Control Stick back for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_sticks([evdev.ecodes.ABS_Y], [255], seconds)

    def push_control_stick_left(self, seconds:float=0.25):
        """Push Control Stick left for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_sticks([evdev.ecodes.ABS_X], [0], seconds)

    def push_control_stick_right(self, seconds:float=0.25):
        """Push Control Stick right for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_sticks([evdev.ecodes.ABS_X], [255], seconds)

    # C Stick
    def push_c_stick_up(self, seconds:float=0.25):
        """Push C Stick up for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_sticks([evdev.ecodes.ABS_RY], [0], seconds)

    def push_c_stick_down(self, seconds:float=0.25):
        """Push C Stick down for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_sticks([evdev.ecodes.ABS_RY], [255], seconds)

    def push_c_stick_left(self, seconds:float=0.25):
        """Push C Stick left for specified time
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_sticks([evdev.ecodes.ABS_RX], [0], seconds)

    def push_c_stick_right(self, seconds:float=0.25):
        """Push C Stick right for specified time
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_sticks([evdev.ecodes.ABS_RX], [255], seconds)

    # Macros
    def macro_ground_pound(self, seconds:float=0.25):
        """Perform a ground pound via pushing a twice quickly.
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_a(seconds)
        time.sleep(seconds)
        self.push_a(seconds)

    def macro_ab(self, seconds:float=0.25):
        """Push a and b at the same time.
        Parameters
        ----------
        seconds: float = 0.25
            Seconds to hold the button down for
        """
        self.push_buttons(
                [evdev.ecodes.BTN_SOUTH, evdev.ecodes.BTN_EAST], seconds)


ACTIONS = {
        "a": (GameCubeController.push_a, 0.25),
        "hold a": (GameCubeController.push_a, 1.0),
        "ab": (GameCubeController.macro_ab, 0.25),
        "b": (GameCubeController.push_b, 0.25),
        "x": (GameCubeController.push_x, 0.25),
        "y": (GameCubeController.push_y, 0.25),
        "z": (GameCubeController.push_z, 0.25),
        "l": (GameCubeController.push_left_trigger, 0.25),
        "r": (GameCubeController.push_right_trigger, 0.25),
        "start": (GameCubeController.push_start, 0.25),
        "up": (GameCubeController.push_control_stick_up, 0.25),
        "down": (GameCubeController.push_control_stick_down, 0.25),
        "left": (GameCubeController.push_control_stick_left, 0.25),
        "right": (GameCubeController.push_control_stick_right, 0.25),
        "hold up": (GameCubeController.push_control_stick_up, 1.0),
        "hold down": (GameCubeController.push_control_stick_down, 1.0),
        "hold left": (GameCubeController.push_control_stick_left, 1.0),
        "hold right": (GameCubeController.push_control_stick_right, 1.0),
        "ground pound": (GameCubeController.macro_ground_pound, 0.25),
        "cup": (GameCubeController.push_c_stick_up, 0.25),
        "cdown": (GameCubeController.push_c_stick_down, 0.25),
        "cleft": (GameCubeController.push_c_stick_left, 0.25),
        "cright": (GameCubeController.push_c_stick_right, 0.25),
        "hold cup": (GameCubeController.push_c_stick_up, 1.0),
        "hold cdown": (GameCubeController.push_c_stick_down, 1.0),
        "hold cleft": (GameCubeController.push_c_stick_left, 1.0),
        "hold cright": (GameCubeController.push_c_stick_right, 1.0),
        "dup": (GameCubeController.push_dpad_up, 0.25),
        "ddown": (GameCubeController.push_dpad_down, 0.25),
        "dright": (GameCubeController.push_dpad_right, 0.25),
        "dleft": (GameCubeController.push_dpad_left, 0.25),
    }


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
            GC.push_a()
        else:
            button = "start"
            while(button == "start"):
                button = random.choice(list(ACTIONS.keys()))
            selection = ACTIONS[button]
            if selection is not None:
                selection[0](GC, selection[1])
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
