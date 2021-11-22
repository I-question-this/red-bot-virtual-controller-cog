# Set up Dad bot
from .main import Controllers
def setup(bot):
    bot.add_cog(Controllers(bot))
