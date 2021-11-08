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
        if button == "a":
            self.push_a()
        elif button == "b":
            self.push_b()
        elif button == "x":
            self.push_x()
        elif button == "y":
            self.push_y()
        elif button == "z":
            self.push_z()
        elif button == "tl" or button == "trigger left":
            self.push_left_trigger()
        elif button == "tr" or button == "trigger right":
            self.push_right_trigger()
        elif button == "up":
            self.push_control_stick_up()
        elif button == "down":
            self.push_control_stick_down()
        elif button == "left":
            self.push_control_stick_left()
        elif button == "right":
            self.push_control_stick_right()
        if button == "start":
            self.push_start()
        elif button == "cup":
            self.push_c_stick_up()
        elif button == "cdown":
            self.push_c_stick_down()
        elif button == "cleft":
            self.push_c_stick_left()
        elif button == "cright":
            self.push_c_stick_right()
        elif button == "dup":
            self.push_dpad_up()
        elif button == "ddown":
            self.push_dpad_down()
        elif button == "dleft":
            self.push_dpad_left()
        elif button == "dright":
            self.push_dpad_left()


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
            await ctx.send(f"No such controller. Existing controllers are: "
                           f"{self.controllers.keys()}")
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
            await ctx.send(f"No such controller. Existing controllers are: "
                           f"{self.ctr.keys()}")
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
        def format_controller(ctr_id):
            return f"{ctr_id} -- {self.controllers[ctr_id].ui.name}"
        formatted_ctrs = [format_controller(ctr_id) for ctr_id in 
                          self.controllers.keys()]
        await ctx.send(f"{formatted_ctrs}")

    @commands.is_owner()
    @commands.command()
    async def list_evdev_devices(self, ctx:commands.Context):
        await ctx.send(f"{evdev.util.list_devices()}")
