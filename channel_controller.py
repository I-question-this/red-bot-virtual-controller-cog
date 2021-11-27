import asyncio
import discord

from .controller import GameCubeController, ACTIONS


class ChannelController(GameCubeController):
    def __init__(self, channel:discord.TextChannel, clone_parent:str,
                 controller_name:str):
        super().__init__(clone_parent, controller_name)
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
            max_button_presses: int, min_participation: float):
        # Check if at least half the team pushed a button
        if len(self.members_who_pushed)/len(self.members) >=\
                min_participation:
            # All have pushed, reset list
            self.members_who_pushed = set()

        # Check if member has already pressed a button since reset
        if member in self.members_who_pushed:
            return

        # Collect valid actions
        validated_actions = []
        # Look at all button press, to a limit
        mbp = max(1, int(max_button_presses / len(self.members)))
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

