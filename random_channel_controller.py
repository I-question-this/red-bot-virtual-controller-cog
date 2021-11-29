import asyncio
import discord
import random
random.seed()

from .controller import ACTIONS, SUGGESTED_BANNED_INPUTS
from .channel_controller import ChannelController

class RandomChannelController(ChannelController):
    def __init__(self, channel:discord.TextChannel, clone_parent:str,
                 controller_name:str):
        super().__init__(channel, clone_parent, controller_name)
        self.__keep_going = True

    async def close(self):
        await super().close()
        # Ensures that the infinite while loop ends
        self.__keep_going = False

    async def start_random_controller(self, banned_inputs=None):
        if banned_inputs is None:
            banned_inputs = SUGGESTED_BANNED_INPUTS

        # Run until the controller is close 
        try:
            while(self.__keep_going):
                # Wait 0.25 seconds between button presses
                await asyncio.sleep(0.25)

                # Check if paused
                if self.paused:
                    await asyncio.sleep(0.25)
                    continue

                # Press "a" lot of the time
                if random.randint(1,100)  <= 40:
                    await self.perform_actions([ACTIONS["a"]])
                else:
                    def pick_a_action():
                        if len(banned_inputs) == 0:
                            action = random.choice(list(ACTIONS.keys()))
                        else:
                            action = banned_inputs[0]
                            while(action in banned_inputs):
                                action = random.choice(list(ACTIONS.keys()))
                        return ACTIONS[action]

                    # Pick an action
                    actions = [pick_a_action()]

                    # Pick a second action, maybe?
                    if random.choice([True, False]):
                        actions.append(pick_a_action())

                    await self.perform_actions(actions)
        except KeyboardInterrupt as e:
            controller.close()
        except ValueError as e:
            # Usually means the controller was closed
            pass


