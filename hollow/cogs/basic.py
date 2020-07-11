from asyncio import iscoroutine
from discord.ext import commands

from .utils import find

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

    @commands.command(name='return')
    @commands.is_owner()
    async def return_(self, ctx, *, expression: str):
        try:
            exec(f'async def handler(ctx): return {expression}')
            return await ctx.send('> {}\n{}'.format(expression, await locals()['handler'](ctx)))
        except Exception as result:
            return await ctx.send(f'**{type(result).__name__}:** {str(result)}', delete_after=5.0)
        
        return

def setup(bot):
    return bot.add_cog(Basic(bot))