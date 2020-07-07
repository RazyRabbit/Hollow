from discord.ext import commands

from discord import Reaction
from discord import Message
from discord import Member
from discord import Embed

import json

class Special(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, author: Member):
        message = reaction.message
        content = message.content
        emoji = reaction.emoji
        guild = message.guild
        me = guild.me

        if me == author or me not in (await reaction.users().flatten()):
            return

        for embed in message.embeds:
            for field in embed.fields:
                content += f'\n{field.name}{field.value}'
        
        roles = tuple(filter(lambda r: f"{emoji}: {r.mention}" in content, guild.roles))
        roles = tuple(filter(lambda r: r.permissions <= author.top_role.permissions, roles))

        if not roles:
            return await reaction.remove()
        elif me.guild_permissions.manage_roles:
            await author.add_roles(*roles)
        else:
            raise commands.MissingPermissions(['manage_permissions'])

        return
    
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: Reaction, author: Member):
        message = reaction.message
        content = message.content
        emoji = reaction.emoji
        guild = message.guild
        me = guild.me

        if me == author or me not in (await reaction.users().flatten()):
            return

        roles = tuple(filter(lambda r: f"{emoji}: {r.mention}" in content, guild.roles))
        roles = tuple(filter(lambda r: r.permissions <= author.top_role.permissions, roles))

        if me.guild_permissions.manage_roles:
            await author.remove_roles(*roles)
        else:
            raise commands.MissingPermissions(['manage_permissions'])

        return
    
    @commands.command(aliases=['rr', 'reaction_role'])
    @commands.has_permissions(add_reactions=True)
    async def react(self, ctx, emoji, message: Message):
        return await message.add_reaction(emoji)
    
    @commands.command()
    async def embed(self, ctx, message: str, *, embed: str):
        embed = Embed.from_dict(json.loads(embed))
        return await ctx.send(message, embed=embed)


def setup(bot: commands.Bot):
    return bot.add_cog(Special(bot))