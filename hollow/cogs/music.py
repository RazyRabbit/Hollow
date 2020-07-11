from asyncio import Queue, Event

from discord.ext import commands
from youtube_dl import YoutubeDL

from discord import PCMVolumeTransformer, FFmpegPCMAudio
from discord import VoiceChannel, VoiceClient
from discord import Guild, Embed

ydl = YoutubeDL({
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'cookies': '__pycache__/cookies.txt',
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
    incoming = Event()
    queue = Queue()

    def __init__(self, loop, voice: VoiceClient, channel: VoiceChannel):
        self.channel = channel
        self.voice = voice
        self.loop = loop
    
    async def sing(self, coro_iteration, coro_end):
        while not self.queue.empty():
            current = YoutubeVideo.search(await self.queue.get())

            self.voice.play(current, after=lambda _: self.loop.call_soon_threadsafe(self.incoming.set))
            self.incoming.clear()

            await coro_iteration(current)
            await self.incoming.wait()

        return await coro_end()

    async def pause(self):
        try:
            await self.voice.pause()
        except:
            return
        
        return self
    
    async def resume(self):
        try:
            await self.voice.resume()
        except:
            return

        return self
    
    async def skip(self):
        try:
            self.voice.stop()
            return not self.queue.empty()
        except:
            return

        return self
    
    @property
    def paused(self):
        return self.voice.is_paused
    
    @property
    def playing(self):
        return self.voice.is_playing
    
class Music(commands.Cog):
    players = {}

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['reproduzir'])
    async def tocar(self, ctx, *, titulo: str):
        await self.connect(ctx)

        player = self.players.setdefault(ctx.guild.id, Player(self.bot.loop, ctx.guild.voice_client, ctx.channel))

        await player.queue.put(titulo)
        
        async def on_next(top):
            embed = Embed(title=top.title, description=top.description, color=ctx.me.color)

            embed.set_thumbnail(url='https://i.pinimg.com/originals/93/07/51/930751de3d3f7a49b4a94e439c0014f4.gif')
            embed.set_footer(text=f'ouvida por {ctx.author.display_name}', icon_url=ctx.author.avatar_url)
            embed.set_author(name=top.uploader)
            embed.set_image(url=top.thumbnail)

            return await ctx.send(f':musical_note: tocando agora!! :musical_note:', embed=embed)
        
        async def on_end():
            del self.players[ctx.guild.id]
            return await ctx.send(f'acabaram as músicas!!', delete_after=5.0)

        if player.playing():
            return await ctx.send(f"foi adicionado **{titulo.title()}** na queue", delete_after=5.0)

        return await player.sing(on_next, on_end)
    
    @commands.command(aliases=['conectar'])
    async def connect(self, ctx: commands.Context):
        vclient = ctx.voice_client
        avoice = ctx.author.voice

        if avoice is None:
            await ctx.send(f'você precisa estar em um canal de voz', delete_after=5.0)

        elif vclient is None:
            await ctx.send(f'estou conectado do no canal {avoice.channel.name}', delete_after=5.0)
            await avoice.channel.connect()
        
        elif vclient.channel != avoice.channel:
            if len(avoice.channel.members) > len(vclient.channel.members):
                vclient.move_to(avoice.channel)

        return
    
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