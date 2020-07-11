from os import environ
from discord.ext import commands

bot = commands.Bot(command_prefix=environ.get("HOLLOW_PREFIX", 'h!'))

@bot.command(pass_context=False)
@commands.is_owner()
async def load(*extensions):
    for name in extensions:
        name = f'hollow.cogs.{name}'
        
        if name in bot.extensions:
            bot.reload_extension(name)
        else:
            bot.load_extension(name)

    return

@bot.event
async def on_ready():
    return await load('basic', 'special', 'music')

bot.run(environ['HOLLOW_TOKEN'])