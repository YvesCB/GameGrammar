from twitchio.ext import commands
from twitchio.ext.commands.core import Command

import unicodedata

import config
import bot_tools
import utils


TAGS = [
    {'command': 'yes', 'response': 'Yes!'},
    {'command': 'no', 'response': 'No!'},
]

tag_commands = [c['command'] for c in TAGS]


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            irc_token=config.bot_irc_token,
            nick=config.bot_nick,
            prefix=config.bot_prefix,
            initial_channels=config.bot_initial_channels
        )

    async def event_ready(self):
        utils.log_kv('[Bot#event_ready] Ready with username', self.nick)
        await self.add_tag('hello', 'OK DUDE')

    async def event_message(self, message):
        utils.log_kv('[Bot#event_message] New message', message.content)
        await self.handle_commands(message)

    async def add_tag(self, name, response):
        self.add_command(Command(name=name, func=self.get_tag, aliases=[], instance=None))
        # TODO: Add tag to database

    async def remove_tag(self, name):
        self.remove_command(name)
        # TODO: Remove tag from database

    async def get_tag(self, ctx):
        # TODO: Get response from database
        # NOTE: This may not be the best way to do this. We're not getting the actual command from
        # the `ctx`, so we have to parse it from the message. This means we need to remove the
        # prefix ourselves, and do not at the moment support arguments. This can be fixed.
        tag_command = ctx.message.content.replace(ctx.prefix, '')
        tag = [tag for tag in TAGS if tag['command'] == tag_command]
        if len(tag) == 0:
            utils.log_kv('[Bot#get_tag] Could not find tag, though we have a command', tag_command)
            return
        response = tag[0]['response']
        await ctx.send(response)

    @commands.command(name='get_tag', aliases=tag_commands)
    async def get_tag_command(self, ctx):
        """
        We run this in `get_tag()` because we want to be able to use that function when adding
        tags as well.
        """
        await self.get_tag(ctx)

    @commands.command(name='test')
    async def test_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command(name='j')
    async def jisho_command(self, ctx):
        message = ctx.message.content[3:]
        index = 0
        if len(message) > 1:
            if len([int(s) for s in message.split() if s.isdigit()]) > 0:
                index = [int(s) for s in message.split() if s.isdigit()][0] - 1
                index_digit_count = len(str(index))
                message = message[:-(index_digit_count)]

        searchres = bot_tools.jisho(message)

        if searchres is None:
            await ctx.send('No results...')
        else:
            if index >= len(searchres):
                index = 0
            else:
                english_info = str(searchres[index]["english"]) \
                    .replace('[', '').replace(']', '') .replace('\'', "\"")
                index_info = str(index + 1) + "/" + str(len(searchres))
                message = "gamegr2Hmmm " + \
                    searchres[index]["word_jp"] + " " + \
                    searchres[index]["reading"] + " " + \
                    english_info + " " + \
                    str(searchres[index]["parts_of_speech"]).replace('\'', '') + " " + \
                    index_info
                await ctx.send(message)


def main():
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
