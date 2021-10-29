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
    def push_a(self, seconds:float=0.5):
        """Push A button for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_A], seconds)

    def push_b(self, seconds:float=0.5):
        """Push B button for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_B], seconds)

    def push_x(self, seconds:float=0.5):
        """Push X button for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_X], seconds)

    def push_y(self, seconds:float=0.5):
        """Push Y button for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_Y], seconds)

    # Trigger buttons
    def push_z(self, seconds:float=0.5):
        """Push Z button for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_Z], seconds)

    def push_left_trigger(self, seconds:float=0.5):
        """Push left trigger for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_TL], seconds)

    def push_right_trigger(self, seconds:float=0.5):
        """Push right trigger for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_TR], seconds)

    # DPAD
    def push_dpad_up(self, seconds:float=0.5):
        """Push DPad up for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_DPAD_UP], seconds)

    def push_dpad_down(self, seconds:float=0.5):
        """Push DPad down for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_DPAD_DOWN], seconds)

    def push_dpad_left(self, seconds:float=0.5):
        """Push DPad left for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_DPAD_LEFT], seconds)

    def push_dpad_right(self, seconds:float=0.5):
        """Push DPad right for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_DPAD_RIGHT], seconds)

    # Control Stick
    def push_control_stick_up(self, seconds:float=0.5):
        """Push Control Stick up for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_FORWARD], seconds)

    def push_control_stick_back(self, seconds:float=0.5):
        """Push Control Stick back for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_BACK], seconds)

    def push_control_stick_left(self, seconds:float=0.5):
        """Push Control Stick left for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_LEFT], seconds)

    def push_control_stick_right(self, seconds:float=0.5):
        """Push Control Stick right for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_RIGHT], seconds)

    # C Stick
    def push_c_stick_up(self, seconds:float=0.5):
        """Push C Stick up for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_NORTH], seconds)

    def push_c_stick_down(self, seconds:float=0.5):
        """Push C Stick down for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_SOUTH], seconds)

    def push_c_stick_left(self, seconds:float=0.5):
        """Push C Stick left for specified time
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_WEST], seconds)

    def push_c_stick_right(self, seconds:float=0.5):
        """Push C Stick right for specified time
        Parameters
        ----------
        seconds: float = 0.5
            Seconds to hold the button down for
        """
        self.push_buttons([evdev.ecodes.BTN_EAST], seconds)


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
            wait_time = 3
            print(f"Waiting {wait_time} seconds")
            time.sleep(wait_time)
            GC.push_buttons(buttons, 0.5)
            print(f"Pressed {buttons}")

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
