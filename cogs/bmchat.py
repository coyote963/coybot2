import discord
from discord.ext import commands
from cogs.bm_connection import initialize_sockets, initialize_threads, rawsay
from cogs.secret import game_servers


class BmChat(commands.Cog):
    def __init__(self, bot, mapping):
        self.bot = bot
        self._last_member = None
        self.mapping = mapping


    @commands.command()
    @commands.has_role('TDM-Chat')
    async def say(self, ctx, *args):
        """Sends a message to the boring man chat"""
        chan_id = str(ctx.channel.id)

        if channel_index(chan_id, game_servers) != -1:
            socket = self.mapping[chan_id]
            sent_message = "{}: {}".format(ctx.author.display_name, ' '.join(args))
            await ctx.send(sent_message)
            rawsay(socket, ctx.author.display_name, ' '.join(args))
        else:
            await ctx.send("This can only be used in the appropriate channel")
        
    @say.error
    async def say_error(ctx, error):
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send('You don\'t have the permission to do that')


def channel_index(channel_id, game_servers):
    """If channel_id is a valid channel return the index of the game_server,
        otherwise, return -1 
    """
    server_channel_ids = [g['discord_channel_id'] for g in game_servers]
    if channel_id in server_channel_ids:
        return server_channel_ids.index(channel_id)
    return -1


def setup(bot):
    socket_mapping = initialize_sockets(game_servers)
    threads = initialize_threads(socket_mapping.values())
    for thread in threads:
        thread.start()
    bot.add_cog(BmChat(bot, socket_mapping))