from discord.ext import commands
import discord
import logging
import config
from cogs import secret

def setup_logger():
    logging.basicConfig(filename='bot.log', level=logging.INFO)

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('!'), **kwargs)
        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                logging.error('Could not load extension {0} due to {1.__class__.__name__}: {1}'.format(cog, exc))

    async def on_ready(self):
        logging.info('Logged on as {0} (ID: {0.id})'.format(self.user))
        print('Logged on as {0} (ID: {0.id})'.format(self.user))


if __name__ == "__main__":
    setup_logger()
    bot = Bot()
    bot.run(secret.token)
