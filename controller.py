#!/usr/bin/env python3
"""Virtual Gamecube controller"""

__author__="Tyler Westland"

import asyncio
from dataclasses import dataclass, replace
import evdev
from typing import List, Optional

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

# Create variations of the actions with shorter or longer time
adjectives = {
        "tiny_": 1/8,
        "t": 1/8,
        "short_": 1/8,
        "s": 1/4,
        "long_": 1.0,
        "l": 1.0
        }

variations = dict()
for adjective in adjectives:
    for action in ACTIONS:
        variations[f"{adjective}{action}"] = replace(
                ACTIONS[action], seconds=adjectives[adjective])

for variation in variations:
    ACTIONS[variation] = variations[variation]

def expand_adjectives(buttons: List[str]):
    def inner():
        for button in buttons:
            for adjective in adjectives:
                yield f"{adjective}{button}"
    return list(inner())

SUGGESTED_BANNED_INPUTS = expand_adjectives(["start", "z"])

class GameCubeController():
    def __init__(self, clone_parent:str, controller_name:str=None):
        if controller_name is None:
            controller_name = "python--GameCube"

        self.ui = evdev.uinput.UInput.from_device(
                clone_parent,
                name=controller_name)

    def close(self):
        self.ui.close()

    def is_open(self):
        return evdev.util.is_device(f"/dev/input/{self.ui.name}")

    async def perform_actions(self, actions:List[Action]) -> None:
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
        await asyncio.sleep(seconds)

        # Reset the actions
        for act in actions:
            self.ui.write(act.etype, act.code, act.reset_value)

        # Synchronize the lifts
        self.ui.syn()

        # Synchronize the resets
        self.ui.syn()
