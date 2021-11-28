import evdev
import discord
from discord.ext import tasks
import itertools
import logging
import re
from requests.exceptions import RequestException
import time

from redbot.core import checks, commands, Config
from redbot.core.data_manager import cog_data_path
from redbot.core.bot import Red

from .controller import ACTIONS
from .channel_controller import ChannelController
from .random_channel_controller import RandomChannelController
from .version import __version__, Version


LOG = logging.getLogger("red.controller")
_DEFAULT_GLOBAL = {
        "max_button_presses": 20,
        "min_participation": 0.5
        }

class Controllers(commands.Cog):
    def __init__(self, bot:Red):
        """Init for the controller cog

        Parameters
        ----------
        bot: Red
            The Redbot instance instantiating this cog.
        """
        # Setup
        super().__init__()
        self.bot = bot

        self._conf = Config.get_conf(
                None, 93949998, 
                cog_name=f"{self.__class__.__name__}", force_registration=True
                )
        self._conf.register_global(**_DEFAULT_GLOBAL)
        self.controllers = {}
        self.random_controllers = {}
        self.quiet = False
        self.locked = False

    async def report_no_such_controller(self, ctx:commands.Context):
        await ctx.send(f"No such controller. Existing controllers are: ")
        await self.list_controllers(ctx)

    @commands.Cog.listener()
    async def on_shutdown(self):
        for ctr in self.controllers:
            await ctr.close()

    @commands.Cog.listener()
    async def on_message(self, msg:discord.Message):
        """Perform actions when a message is received

        Parameters
        ---------
        msg: discord.Message
            The message to perform actions upon.
        """
        # Check this message is within a guild
        if isinstance(msg.channel, discord.abc.PrivateChannel):
            return

        # Check this is a message from a valid user
        if not isinstance(msg.author, discord.Member) or msg.author.bot:
            return
        if await self.bot.is_automod_immune(msg):
            return

        # Check if controllers are set to quiet
        if self.quiet:
            return

        # Interpret message
        for ctr in self.controllers.values():
            if ctr.channel_and_member_check(msg.channel, msg.author):
                ctr.member_perform_action(msg.author, msg.content.lower(),
                        await self._conf.max_button_presses(),
                        await self._conf.min_participation())

    @commands.is_owner()
    @commands.command()
    async def max_button_presses(self, ctx:commands.Context, new_max: int=None):
        """Displays or sets the max button press for people.
        Remember that the actual number is `max_button_presses/len(team_size)`
        """
        if new_max is not None:
            await self._conf.max_button_presses.set(new_max)

        await ctx.send(
            f"max_button_press: {await self._conf.max_button_presses()}")

    @commands.is_owner()
    @commands.command()
    async def minimum_participation(self, ctx:commands.Context, 
            new_min: float=None):
        """Displays or sets the minimum percentage of participation from a team.
        Value will be cast to range of [0,1].
        """
        if new_min is not None:
            await self._conf.min_participation.set(
                    min(1, max(0, new_min)))

        await ctx.send(
            f"minimum_participation: {await self._conf.min_participation()}")

    @commands.is_owner()
    @commands.command()
    async def create_controller(self, ctx:commands.Context, clone_parent:str):
        if len(self.controllers) == 0:
            controller_number = 0
        else:
            controller_number = max(self.controllers.keys()) + 1

        controller_name = f"DiscordController{controller_number}"
        self.controllers[controller_number] = ChannelController(
                ctx.channel, clone_parent, controller_name)
        await self.controllers[controller_number].ready_message()

    @commands.is_owner()
    @commands.command()
    async def close_controller(self, ctx:commands.Context, 
            controller_number:int):
        controller = self.controllers.get(controller_number)
        if controller is None:
            await self.report_no_such_controller()
            return
       
        await controller.close()
        del self.controllers[controller_number]

    @commands.is_owner()
    @commands.command()
    async def create_random_controller(self, ctx:commands.Context, 
            clone_parent:str):
        if len(self.random_controllers) == 0:
            controller_number = 0
        else:
            controller_number = max(self.random_controllers.keys()) + 1

        controller_name = f"RandomController{controller_number}"
        self.random_controllers[controller_number] = RandomChannelController(
                ctx.channel, clone_parent, controller_name)
        await self.random_controllers[controller_number].ready_message()
        await self.random_controllers[controller_number].\
                start_random_controller()

    @commands.is_owner()
    @commands.command()
    async def close_random_controller(self, ctx:commands.Context, 
            controller_number:int):
        controller = self.random_controllers.get(controller_number)
        if controller is None:
            await ctx.send(f"No such controller. Existing controllers are: ")
            await self.list_controllers(ctx)
            return
      
        await controller.close()
        del self.random_controllers[controller_number]

    @commands.is_owner()
    @commands.command()
    async def close_all_controllers(self, ctx:commands.Context):
        for ctr in self.controllers.values():
            await ctr.close()
        for ctr in self.random_controllers.values():
            await ctr.close()
        # Delete entire list
        self.controllers = {}
        self.random_controllers = {}

    @commands.command()
    async def sign_up_for_controller(self, ctx:commands.Context, 
            controller_number:int):
        if self.locked:
            await ctx.send(f"Controller sign up is currently locked.")
            return

        for ctr_id in self.controllers.keys():
            if ctx.author in self.controllers[ctr_id].members:
                await self.unsign_up_for_controller(ctx, ctr_id)

        ctr = self.controllers.get(controller_number)
        if ctr is None:
            await ctx.send(f"No such controller. Existing controllers are: ")
            await self.list_controllers(ctx)
            return
      
        ctr.members.add(ctx.author)
        await ctx.send(f"{ctx.author.mention} is signed up for "
                       f"{controller_number}")
        
    @commands.is_owner()
    @commands.command()
    async def sign_up_member_for_controller(self, ctx:commands.Context, 
            controller_number:int, member:discord.Member):
        ctx.author = member
        # Hack for getting around lock as owner
        # Would be dangerous if this were important for things other than
        # anti-griefing
        locked_status = self.locked
        self.locked = False
        await self.sign_up_for_controller(ctx, controller_number)
        self.locked = locked_status

    @commands.command()
    async def unsign_up_for_controller(self, ctx:commands.Context,
            controller_number:int):
        if self.locked:
            await ctx.send(f"Controller sign up is currently locked.")
            return

        for ctr in self.controllers.values():
            if ctx.author in ctr.members:
                ctr.members.remove(ctx.author)
                await ctx.send(f"Unsigned up {ctx.author.mention} from "
                               f"{controller_number}")
                return

        await ctx.send(f"{ctx.author.mention} was not signed up for any "
                        "controller")

    @commands.is_owner()
    @commands.command()
    async def unsign_up_member_for_controller(self, ctx:commands.Context, 
            controller_number:int, member:discord.Member):
        ctx.author = member
        # Hack for getting around lock as owner
        # Would be dangerous if this were important for things other than
        # anti-griefing
        locked_status = self.locked
        self.locked = False
        await self.unsign_up_for_controller(ctx, controller_number)
        self.locked = locked_status

    @commands.command()
    async def list_controllers(self, ctx:commands.Context):
        formatted_controllers = "Controllers:\n"
        for ctr_id in self.controllers.keys():
            formatted_controllers += f"{ctr_id} -- "
            formatted_controllers += f"{self.controllers[ctr_id].ui.name}\n"
            for member in self.controllers[ctr_id].members:
                formatted_controllers += f"   - {member.mention}\n"

        formatted_controllers += "\nRandom Controllers:\n"
        for ctr_id in self.random_controllers.keys():
            formatted_controllers += f"{ctr_id} -- "
            formatted_controllers += \
                f"{self.random_controllers[ctr_id].ui.name}\n"

        await ctx.send(formatted_controllers)

    @commands.command()
    async def list_actions(self, ctx:commands.Context):
        actions = "Available Actions:\n"
        actions += ", ".join(ACTIONS.keys())
        await ctx.send(actions)

    @commands.is_owner()
    @commands.command()
    async def list_evdev_devices(self, ctx:commands.Context):
        await ctx.send(f"{evdev.util.list_devices()}")

    @commands.is_owner()
    @commands.command()
    async def pause_controller(self, ctx:commands.Context, 
                               controller_number:int):
        if self.controllers.get(controller_number) is not None:
            self.controllers[controller_number].paused = True
            await ctx.send(f"Paused controller: {controller_number}.")
        else:
            await self.report_no_such_controller(ctx)

    @commands.is_owner()
    @commands.command()
    async def unpause_controller(self, ctx:commands.Context, 
                               controller_number:int):
        if self.controllers.get(controller_number) is not None:
            self.controllers[controller_number].paused = False
            await ctx.send(f"Unpaused controller: {controller_number}.")
        else:
            await self.report_no_such_controller(ctx)

    @commands.is_owner()
    @commands.command()
    async def pause_all_controllers(self, ctx:commands.Context):
        for ctr_id in self.controllers.keys():
            self.controllers[ctr_id].paused = True
        await ctx.send(f"Paused all controllers.")

    @commands.is_owner()
    @commands.command()
    async def unpause_all_controllers(self, ctx:commands.Context):
        for ctr_id in self.controllers.keys():
            self.controllers[ctr_id].paused = False
        await ctx.send(f"Unpaused all controllers.")

    @commands.is_owner()
    @commands.command()
    async def pause_random_controller(self, ctx:commands.Context, 
                               controller_number:int):
        if self.random_controllers.get(controller_number) is not None:
            self.random_controllers[controller_number].paused = True
            await ctx.send(f"Paused random controller: {controller_number}.")
        else:
            await self.report_no_such_controller(ctx)

    @commands.is_owner()
    @commands.command()
    async def unpause_random_controller(self, ctx:commands.Context, 
                               controller_number:int):
        if self.random_controllers.get(controller_number) is not None:
            self.random_controllers[controller_number].paused = False
            await ctx.send(f"Unpaused random controller: {controller_number}.")
        else:
            await self.report_no_such_controller(ctx)

    @commands.is_owner()
    @commands.command()
    async def pause_all_random_controllers(self, ctx:commands.Context):
        for ctr_id in self.random_controllers.keys():
            self.random_controllers[ctr_id].paused = True
        await ctx.send(f"Paused all random controllers.")

    @commands.is_owner()
    @commands.command()
    async def unpause_all_random_controllers(self, ctx:commands.Context):
        for ctr_id in self.random_controllers.keys():
            self.random_controllers[ctr_id].paused = False
        await ctx.send(f"Unpaused all random controllers.")

    @commands.is_owner()
    @commands.command()
    async def toggle_sign_up_lock(self, ctx:commands.Context):
        self.locked = not self.locked
        await ctx.send(f"Controller Sign Up Lock set to: {self.locked}")
