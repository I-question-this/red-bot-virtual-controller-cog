import evdev
import discord
from discord.ext import tasks
import logging
import re
from requests.exceptions import RequestException

from redbot.core import checks, commands, Config
from redbot.core.data_manager import cog_data_path
from redbot.core.bot import Red

from .controller import GameCubeController, ACTIONS
from .version import __version__, Version


LOG = logging.getLogger("red.controller")
_DEFAULT_GLOBAL = {}
_DEFAULT_GUILD = {}

class ChannelController(GameCubeController):
    def __init__(self, channel:discord.TextChannel, clone_parent:str,
                       controller_name:str=None):
        super().__init__(clone_parent, controller_name)
        self.channel = channel
        self.members = set()


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

    def perform_action(self, button:str):
        selection = ACTIONS.get(button)
        if selection is not None:
            selection[0](self, selection[1])

class MainBot(commands.Cog):
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
        self._conf.register_guild(**_DEFAULT_GUILD)
        self.controllers = {}
        self.quiet = False

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
                ctr.perform_action(msg.content.lower())

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
            await ctx.send(f"No such controller. Existing controllers are: ")
            await self.list_controllers(ctx)
            return
       
        await controller.close()
        del self.controllers[controller_number]

    @commands.is_owner()
    @commands.command()
    async def close_all_controllers(self, ctx:commands.Context):
        for ctr in self.controllers.values():
            await ctr.close()
        # Delete entire list
        self.controllers = {}

    @commands.command()
    async def sign_up_for_controller(self, ctx:commands.Context, 
            controller_number:int):
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
        await self.sign_up_for_controller(ctx, controller_number)

    @commands.command()
    async def unsign_up_for_controller(self, ctx:commands.Context,
            controller_number:int):
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
        await self.unsign_up_for_controller(ctx, controller_number)

    @commands.command()
    async def list_controllers(self, ctx:commands.Context):
        formatted_controllers = "Controllers:\n"
        for ctr_id in self.controllers.keys():
            formatted_controllers += f"{ctr_id} -- "
            formatted_controllers += f"{self.controllers[ctr_id].ui.name}\n"
            for member in self.controllers[ctr_id].members:
                formatted_controllers += f"   - {member.mention}\n"

        await ctx.send(formatted_controllers)

    @commands.command()
    async def list_actions(self, ctx:commands.Context):
        actions = "Available Actions:\n"
        actions += ", ".join(ChannelController.ACTIONS.keys())
        await ctx.send(actions)

    @commands.is_owner()
    @commands.command()
    async def list_evdev_devices(self, ctx:commands.Context):
        await ctx.send(f"{evdev.util.list_devices()}")

    @commands.is_owner()
    @commands.command()
    async def toggle_controller_quiet(self, ctx:commands.Context):
        self.quiet = not self.quiet
        await ctx.send(f"Controllers Quiet set to: {self.quiet}")
