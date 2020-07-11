from itertools import count
from operator import itemgetter

from discord.ext import commands

def compare(first, second):
    for a, b, score in zip(first, second, count(1)):
        if a != b:
            return len(first)/score
    
    return 0

def find(items, string):
    return min(((item, compare(str(item), string)) for item in items), key=itemgetter(1))[0]

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(f'não há permissões o suficiente para executar o comando **{ctx.invoked_with}**', delete_after=5.0)
        elif isinstance(error, commands.CommandNotFound):
            return await ctx.send(f'você quis dizer **{str(find(self.bot.commands, ctx.invoked_with))}**?')

        raise error

def setup(bot):
    return bot.add_cog(Basic(bot))