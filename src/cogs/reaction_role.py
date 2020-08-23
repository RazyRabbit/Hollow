from typing import Union, List, Set

from discord.ext.commands import Cog, Bot, Context
from discord.ext.commands import command

from discord import Reaction
from discord import Embed
from discord import Emoji

from discord import Message
from discord import Member
from discord import Role

import json


class Private:
    async def give_to(self, reaction: Reaction, author: Member, roles: Set[Role]):
        to_add = roles.difference(roles)
        to_rem = roles.intersection(roles)

        await author.remove_roles(*to_rem, reason='reaction-role: os usuario já possui o role')
        await author.add_roles(*to_add, reason='reaction-role: o usuario não possui o role')

class ReactionRole(Private, Cog):
    messages = {}

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, author: Member):
        message: Message = reaction.message
        emoji: Emoji = reaction.emoji

        if emoji in (emojis := self.messages.get(message.id, {})):
            await self.give_to(reaction, author, emojis[emoji])

        return
    
    @Cog.listener()
    async def on_reaction_remove(self, reaction: Reaction, author: Member):
        return await self.on_reaction_add(reaction, author)
    
    @command()
    async def rr_new(self, ctx: Context, *, codeblock: str):
        '''cria um embed como tabela de reaction-role'''

        if codeblock.startswith('```json\n') and codeblock.endswith('```'):
            raise SyntaxError("codeblock deve ter um sinalizador do tipo json")
        
        codeblock = json.loads(codeblock[8:-3])
        message = codeblock.pop("message", 'react to get your role')

        embed = Embed(
            description=codeblock.pop("description", None),
            title=codeblock.pop("title", None),
            type=codeblock.pop("type", None),
        )

        for name, value in codeblock.items():
            embed.add_field(name=name, value='\n'.join(map(str, value)))
        
        self.messages.setdefault((await ctx.send(message, embed=embed)).id, {})

        return await ctx.message.delete()
    
    @command()
    async def rr_enable(self, ctx: Context, message: Message):
        '''habilita uma tabela de reaction-role'''

        if message.id not in self.messages:
            self.bot._connection._messages.append(message)
            self.messages.setdefault(message.id, {})

        return await ctx.message.delete()
    
    @command()
    async def rr_add(self, ctx: Context, message: Message, emoji: Emoji, role: Role):
        '''associa um emoji a um cargo em uma tabela'''

        self.messages.setdefault(message.id, {}).setdefault(emoji, set()).add(role)
        await message.add_reaction(emoji)
        await ctx.message.delete()
    
    @command()
    async def as_json(self, ctx: Context, message: Message):
        '''transforma uma mensagem em uma estrutura json'''

        for embed in message.embeds:
            await ctx.send(f'```json\n{json.dumps(embed.to_dict(), ensure_ascii=False, indent=1)}```')

        return

def setup(bot: Bot):
    return bot.add_cog(ReactionRole(bot))