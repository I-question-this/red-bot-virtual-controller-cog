# Set up Dad bot
from .main import MainBot
def setup(bot):
    bot.add_cog(MainBot(bot))
