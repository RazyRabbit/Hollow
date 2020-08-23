from os import environ
from discord.ext import commands

from cogs import cog_names

bot = commands.Bot(environ.get("HOLLOW_PREFIX", 'h!'))

@commands.is_owner()
@commands.command(pass_context=False)
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