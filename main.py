from asyncio import iscoroutine
from os import environ

from discord.ext import commands

bot = commands.Bot(command_prefix='hc!')

@bot.command()
@commands.is_owner()
async def load(ctx, *extensions):
    for name in extensions:
        name = f'hollow.cogs.{name}'
        
        if name in bot.extensions:
            bot.reload_extension(name)
        else:
            bot.load_extension(name)

    return

@bot.event
async def on_ready():
    return await load(None, 'special')

@bot.command()
async def ping(ctx):
    return await ctx.send('pong')

@bot.command(name='eval')
@commands.is_owner()
async def eval_(ctx, *, expression: str):
    try:
        async with ctx.typing():
            if iscoroutine(result := eval(expression)):
                result = await result

    except Exception as result:
        return await ctx.send(f"**__{type(result).__name__}__**: {str(result)}")

    return await ctx.send(f"> {repr(expression)} -> **{type(result).__name__}**\n{str(result)}")

bot.run(environ['HOLLOW_TOKEN'])