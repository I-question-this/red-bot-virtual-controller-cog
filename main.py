import evdev
import discord
from discord.ext import tasks
import logging
import re
from requests.exceptions import RequestException

from redbot.core import checks, commands, Config
from redbot.core.data_manager import cog_data_path
from redbot.core.bot import Red

from .controller import GameCubeController
from .version import __version__, Version


LOG = logging.getLogger("red.controller")
_DEFAULT_GLOBAL = {}
_DEFAULT_GUILD = {}

class ChannelController(GameCubeController):
    def __init__(self, channel:discord.TextChannel, clone_parent:str,
                       controller_name:str=None):
        super().__init__(clone_parent, controller_name)
        self.channel = channel

    async def ready_message(self):
        await self.channel.send(f"{self.ui.name}: READY")

    async def close(self):
        super().close()
        await self.channel.send(f"{self.ui.name}: CLOSED")


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


    @commands.is_owner()
    @commands.command()
    async def create_controller(self, ctx:commands.Context, clone_parent:str):
        controller_name = f"DiscordController{len(self.controllers)}"
        self.controllers[controller_name] = ChannelController(
                ctx.channel, clone_parent, controller_name)
        await self.controllers[controller_name].ready_message()

    @commands.is_owner()
    @commands.command()
    async def close_controller(self, ctx:commands.Context, controller_name:str):
        controller = self.controllers.get(controller_name)
        if controller is None:
            await ctx.send(f"No such controller. Existing controllers are: "
                           f"{self.controllers.keys()}")
            return
       
        await controller.close()

    @commands.is_owner()
    @commands.command()
    async def list_evdev_devices(self, ctx:commands.Context):
        await ctx.send(f"{evdev.util.list_devices()}")
