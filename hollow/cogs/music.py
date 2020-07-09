from asyncio import Queue, Event

from discord.ext import commands

from discord import PCMVolumeTransformer
from discord import FFmpegPCMAudio

from discord import VoiceChannel
from discord import Guild
from discord import Embed

from youtube_dl import YoutubeDL

ydl = YoutubeDL({
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'nocheckcertificate': True,
    'restrictfilenames': True,
    'ignoreerrors': False,
    'no_warnings': True,
    'noplaylist': True,
    'quiet': True,
})


class YoutubeVideo(PCMVolumeTransformer):
    def __init__(self, source, thumbnail, title, url, uploader, description):
        super().__init__(FFmpegPCMAudio(source))

        self.description = description
        self.thumbnail = thumbnail
        self.uploader = uploader
        self.title = title
        self.url = url

    @classmethod
    def search(cls, string, download=False):
        result = ydl.extract_info(string, download)

        if "entries" in result:
            result = result["entries"][0]

        return cls(
            ydl.prepare_filename(result) if download else result['url'],
            result.get("thumbnail"), result.get("title"),
            result.get("url"), result.get("uploader"),
            result.get("description")
        )
    
    
    def __del__(self):
        return self.cleanup()

class Player:
    running = False
    paused = False

    incoming = Event()
    queue = Queue()

    def __init__(self, loop, guild: Guild, channel: VoiceChannel):
        self.channel = channel
        self.guild = guild
        self.loop = loop
    
    def sing(self, coro):
        async def player_loop(loop):
            self.running = True

            while not self.queue.empty():
                source = await self.queue.get()

                await coro(source)
                self.guild.voice_client.play(source, after=lambda _: loop.call_soon_threadsafe(self.incoming.set))
                await self.incoming.wait()

            self.running = False
            return
        
        return self.loop.create_task(player_loop(self.loop))
    
    async def add(self, title):
        return await self.queue.put(YoutubeVideo.search(title))
    
    async def pause(self):
        try:
            self.paused = True
            await self.guild.voice_client.pause()
        except:
            return
        
        return self
    
    async def resume(self):
        try:
            self.paused = False
            await self.guild.voice_client.resume()
        except:
            return

        return self
    
    async def skip(self):
        try:
            self.paused = False
            await self.guild.voice_client.stop()
        except:
            return
        
        return self

class Music(commands.Cog):
    players = {}

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['reproduzir'])
    async def tocar(self, ctx, *titulos):
        await self.connect(ctx)

        player = self.players.get(ctx.guild.id, Player(self.bot.loop, ctx.guild, ctx.channel))

        if player.paused:
            await self.resume(ctx)
        elif not titulos:
            await self.pause(ctx)
        
        running = player.running
        
        for titulo in titulos:
            await player.add(titulo)
        
        async def on_next_sound(top):
            embed = Embed(title=top.title, description=top.description, color=ctx.me.color)

            embed.set_thumbnail(url='https://i.pinimg.com/originals/93/07/51/930751de3d3f7a49b4a94e439c0014f4.gif')
            embed.set_footer(text=f'ouvida por {ctx.author.display_name}', icon_url=ctx.author.avatar_url)
            embed.set_author(name=top.uploader)
            embed.set_image(url=top.thumbnail)

            return await ctx.send(f':musical_note: tocando agora!! :musical_note:', embed=embed)
        
        player = self.players.setdefault(ctx.guild.id, player)

        if not running:
            return player.sing(on_next_sound)
        elif len(titulos) == 1:
            return await ctx.send(f"foi adicionado {titulos[0]} na queue", delete_after=5.0)
        elif len(titulos) > 1:
            return await ctx.send(f"foram adicionados {', '.join(titulos[:-1])} e {titulos[-1]} na queue", delete_after=5.0)
        
        return
    
    @commands.command()
    async def connect(self, ctx: commands.Context):
        vchannel = ctx.author.voice.channel
        vclient = ctx.voice_client

        if vclient and vclient.channel != vchannel:
            await ctx.send(f'movido para o canal **{vchannel.name}**', delete_after=5.0)
            await vclient.move_to(vchannel)
        else:
            await ctx.send(f'conectado ao canal **{vchannel.name}**', delete_after=5.0)
            await vchannel.connect()

        return await ctx.message.delete()
    
    @commands.command(aliases=['pular', 'proximo'])
    async def skip(self, ctx):
        if not (await self.players[ctx.guild.id].skip()):
            return await ctx.send('não há o que pular na queue', delete_after=5.0)

        return await ctx.send(f'{ctx.author.mention} pulou o som', delete_after=5.0)
    
    @commands.command(aliases=['pausar'])
    async def pause(self, ctx):
        player = self.players[ctx.guild.id]

        if player.paused:
            return await ctx.send('não há som para pausar', delete_after=5.0)
        else:
            await player.pause()
        
        return await ctx.send(f'{ctx.author.mention} pausou o som', delete_after=5.0)
    
    @commands.command(aliases=['continuar'])
    async def resume(self, ctx):
        player = self.players[ctx.guild.id]

        if player.paused:
            await player.resume()
        else:
            return await ctx.send('não há som para resumir.', delete_after=5.0)
        
        return await ctx.send(f'{ctx.author.mention} resumiu o som', delete_after=5.0)

def setup(bot):
    return bot.add_cog(Music(bot))