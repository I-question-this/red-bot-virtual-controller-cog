import asyncio
import itertools
import discord

from .controller import GameCubeController, ACTIONS


class ChannelController(GameCubeController):
    def __init__(self, channel:discord.TextChannel, clone_parent:str,
                 controller_name:str):
        super().__init__(clone_parent, controller_name)
        self.paused = False
        self.channel = channel
        self.members = set()
        self.members_who_pushed = set()

    async def ready_message(self):
        await self.channel.send(f"{self.ui.name}: READY")

    async def close(self):
        super().close()
        await self.channel.send(f"{self.ui.name}: CLOSED")

    def channel_and_member_check(self, channel:discord.TextChannel,
            member: discord.Member):
        if self.channel.id != channel.id:
            return False

        return member in self.members

    async def member_perform_action(self, member:discord.Member, actions:str,
            max_button_presses: int, min_participation: float,
            override_pause:bool=False):
        # If paused, do nothing!
        if self.paused and not override_pause:
            return

        # Prevent division by 0 when overriding a controller with no members.
        # Usually occurs with random input controllers
        if len(self.members) > 0:
            # Check if at least the required percentage of the team
            # participated
            if len(self.members_who_pushed)/len(self.members) >=\
                    min_participation:
                # All have pushed, reset list
                self.members_who_pushed = set()
            # Restrict max button presses down proportionally to the team size
            mbp = max(2, int(max_button_presses / len(self.members)))

            # Check if member has already pressed a button since reset
            if member in self.members_who_pushed:
                return
        else:
            mbp = max_button_presses

        # Collect valid actions
        validated_actions = []
        # Look at all button press, to a limit
        for action in itertools.islice(actions.split(" "), mbp):
            if ACTIONS.get(action) is not None:
                act = ACTIONS.get(action)
                placed = False
                for i in range(len(validated_actions)):
                    if not act in validated_actions[i]:
                        placed = True
                        validated_actions[i].append(act)
                        break
                if not placed:
                    validated_actions.append([act])

        # Push button
        if len(validated_actions) > 0:
            # Add member to pressed list
            self.members_who_pushed.add(member)
            for action_set in validated_actions:
                await self.perform_actions(action_set)
                await asyncio.sleep(1/8)

