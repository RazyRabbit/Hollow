from functools import partial
from typing import List

from discord.ext.commands import Bot, Cog, Context
from discord.ext.commands import command

from discord import TextChannel
from discord import Message
from discord import Member


class Private:
    def can_delete_of(self, member: Member, message: Message):
        return not message.pinned and message.author == member
    
    def can_delete(self, message: Message):
        return not message.pinned

class Moderation(Private, Cog):
    @command(aliases=["limpar", "cls"])
    async def clear(self, ctx: Context, limit: int=10, member: Member=None):
        channel: TextChannel = ctx.channel

        if member:
            return await channel.purge(limit=limit, check=partial(self.can_delete_of, member))

        return await channel.purge(limit=limit, check=partial(self.can_delete))
    
    @command(aliased=["desfixar", "unp"])
    async def unpin(self, ctx: Context, limit: int=10, reason=None):
        channel: TextChannel = ctx.channel
        pinneds: List[Message] = await channel.pins()

        for _, message in zip(range(limit), pinneds):
            await message.unpin(reason=reason)

        return


def setup(bot: Bot):
    return bot.add_cog(Moderation())