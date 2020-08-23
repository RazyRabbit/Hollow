from os import environ
from discord.ext import commands

from utils import get_nearest
from cogs import cog_names

bot = commands.Bot(environ.get("HOLLOW_PREFIX", 'h!'))

@bot.event
async def on_command_error(ctx, error):
    '''trata erros globalmente'''
    
    if isinstance(error, commands.CommandNotFound):
        return await ctx.send(f'você quis dizer **{get_nearest(ctx.invoked_with, *(c.name for c in bot.commands))[0]}**?', delete_after=5.0)

    return await ctx.send(f'erro: ``{str(error)}``', delete_after=5.0)

@commands.is_owner()
@bot.command(pass_context=False)
async def reload(module: str, prefix: str='cogs.{}'):
    '''recarrega um módulo'''

    module = prefix.format(module)

    if module in bot.extensions:
        bot.unload_extension(module)

    return bot.load_extension(module)


async def main():
    '''prepara o bot carregando todos os módulos'''

    for name in cog_names:
        await reload(name)

    return

if __name__ == "__main__":
    bot.loop.create_task(main())
    bot.run(environ["HOLLOW_TOKEN"])