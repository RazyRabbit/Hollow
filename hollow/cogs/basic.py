from asyncio import iscoroutine
from os import environ

from discord.ext import commands

from .utils import pyanywhere
from .utils import find

pya = pyanywhere.Client(environ['HOLLOW_PYA_USER'], environ['HOLLOW_PYA_TOKEN'])

class Basic(commands.Cog):
    last_python_message = None

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(f'não há permissões o suficiente para executar o comando **{ctx.invoked_with}**', delete_after=5.0)

        elif isinstance(error, commands.CommandNotFound):
            return await ctx.send(f'você quis dizer **{str(list(find(self.bot.commands, ctx.invoked_with))[0])}**?')

        raise error

    @commands.command(name='return')
    @commands.is_owner()
    async def return_(self, ctx, *, expression: str):
        try:
            exec(f'async def handler(console, ctx): return {expression}')
            return await ctx.send('> {}\n{}'.format(expression, await locals()['handler'](pya.console, ctx)))
        except Exception as result:
            return await ctx.send(f'**{type(result).__name__}:** {str(result)}', delete_after=5.0)
        
        return
    
    @commands.command()
    async def python(self, ctx, *, expression: str):
        if expression.startswith('```python'):
            pya.console.send(expression[9:])
        else:
            pya.console.send(expression)

        try:
            return await self.last_python_message.edit(content=f'> {expression}\n```python\n{pya.console.output}```')

        except:
            self.last_python_message = await ctx.send(f'> {expression}\n```python\n{pya.console.output}```')
            
        return
        
        

def setup(bot):
    return bot.add_cog(Basic(bot))