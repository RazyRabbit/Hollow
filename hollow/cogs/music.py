from asyncio import Queue, Event

from discord.ext import commands

from discord import PCMVolumeTransformer
from discord import FFmpegPCMAudio

from discord import VoiceChannel
from discord import Guild

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
    def __init__(self, source, title, url):
        super().__init__(FFmpegPCMAudio(source))

        self.title = title
        self.url = url

    @classmethod
    def search(cls, string, download=True):
        result = ydl.extract_info(string, download)

        if "entries" in result:
            result = result["entries"][0]
        
        return cls(ydl.prepare_filename(result), result.get("title"), result.get("url"))
    
    def __del__(self):
        return self.cleanup()

class Player:
    paused = False

    incoming = Event()
    queue = Queue()

    def __init__(self, loop, guild: Guild, channel: VoiceChannel):
        self.channel = channel
        self.guild = guild
        self.loop = loop
    
    def sing(self, coro):
        async def player_loop(loop):
            while not self.queue.empty():
                source = await self.queue.get()

                await coro(source)
                self.guild.voice_client.play(source, after=lambda _: loop.call_soon_threadsafe(self.incoming.set))
                await self.incoming.wait()
            
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
    
    async def next(self):
        try:
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

        for titulo in titulos:
            await player.add(titulo)
        
        async def on_next_sound(top):
            return await ctx.send(f'tocando agora **"{top.title}"**"', delete_after=5.0)

        return self.players.setdefault(ctx.guild.id, player).sing(on_next_sound)
    
    @commands.command()
    async def connect(self, ctx: commands.Context):
        vchannel = ctx.author.voice.channel
        vclient = ctx.voice_client

        if vclient and vclient != vchannel:
            await vclient.move_to(vchannel)
        else:
            await vchannel.connect()

        await ctx.send(f'conectado ao canal **{vchannel.name}**', delete_after=5.0)
        return await ctx.message.delete()
    
    @commands.command(aliases=['pular', 'proximo'])
    async def skip(self, ctx):
        if not (await self.players[ctx.guild.id].next()):
            return await ctx.send('não há o que pular na queue', delete_after=5.0)

        return await ctx.send(f'{ctx.author.mention} pulou o som', delete_after=5.0)
    
    @commands.command(aliases=['pausar'])
    async def pause(self, ctx):
        if not (await self.players[ctx.guild.id].pause()):
            return await ctx.send('não há som para pausar', delete_after=5.0)
        
        return await ctx.send(f'{ctx.author.mention} pausou o som', delete_after=5.0)
    
    @commands.command(aliases=['continuar'])
    async def resume(self, ctx):
        if not (await self.players[ctx.guild.id].resume()):
            return await ctx.send('não há som para resumir.', delete_after=5.0)
        
        return await ctx.send(f'{ctx.author.mention} resumiu o som', delete_after=5.0)




def setup(bot):
    return bot.add_cog(Music(bot))