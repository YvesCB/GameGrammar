from twitchio.ext import commands
from twitchio.ext.commands.core import Command

import unicodedata

import config
import bot_tools
import bot_db
import utils


tag_names = [t['name'] for t in bot_db.get_all_tags()]


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
        utils.log_kv('Tags', bot_db.get_all_tags())
        utils.log_kv('Mods', bot_db.get_all_mods())
        utils.log_kv('Superadmins', config.superadmins)

    async def event_message(self, message):
        utils.log_kv('[Bot#event_message] New message', message.content)
        await self.handle_commands(message)

    async def get_tag(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 0)
        except ValueError:
            return
        [tag_name] = command
        tag = bot_db.get_tag(tag_name)
        if tag is None:
            utils.log_kv('[Bot#get_tag] Could not find tag, though we have a command', tag_name)
            return
        response = tag['response']
        await ctx.send(response)

    @commands.command(name='get_tag', aliases=tag_names)
    async def get_tag_command(self, ctx):
        """
        We run this in `get_tag()` because we want to be able to use that function when adding
        tags as well.
        """
        await self.get_tag(ctx)

    @commands.command(name='add_tag')
    async def add_tag_command(self, ctx):
        if not bot_db.is_mod(ctx.author.name):
            utils.log_body('[Bot#add_tag_command] Access denied to ' + ctx.author.name)
            return
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except ValueError:
            return await ctx.send('Usage: add_tag <tag_name> <tag_response>')

        [_, tag_name, tag_response] = command
        utils.log_kv('Adding tag', [tag_name, tag_response])

        if bot_db.exists_tag(tag_name):
            await ctx.send(f'Tag {tag_name} already exists.')
        else:
            bot_db.add_tag(tag_name, tag_response)
            self.add_command(Command(name=tag_name, func=self.get_tag, aliases=[], instance=None))
            await ctx.send(f'Added tag {tag_name}.')

    @commands.command(name='remove_tag')
    async def remove_tag_command(self, ctx):
        if not bot_db.is_mod(ctx.author.name):
            utils.log_body('[Bot#remove_tag_command] Access denied to ' + ctx.author.name)
            return
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            return await ctx.send('Usage: remove_tag <tag_name>')

        [_, tag_name] = command
        utils.log_kv('Removing tag', tag_name)

        if bot_db.exists_tag(tag_name):
            bot_db.remove_tag(tag_name)

            async def dummy_func():
                pass

            self.remove_command(Command(name=tag_name, func=dummy_func))

            await ctx.send(f'Removed tag {tag_name}.')
        else:
            await ctx.send(f'Tag {tag_name} does not exist.')

    @commands.command(name='mods')
    async def mods_command(self, ctx):
        mods = [mod['name'] for mod in bot_db.get_all_mods()]
        await ctx.send('Mods: {}'.format(', '.join(mods)))

    @commands.command(name='mod')
    async def mod_command(self, ctx):
        if not bot_tools.is_superadmin(ctx.author.name):
            utils.log_body('[Bot#mod_command] Access denied to ' + ctx.author.name)
            return
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            return await ctx.send('Usage: mod <name>')

        [_, mod_name] = command
        utils.log_kv('Modding', mod_name)

        if bot_db.is_mod(mod_name):
            await ctx.send(f'{mod_name} is already a mod.')
        else:
            bot_db.add_mod(mod_name)
            await ctx.send(f'Modded {mod_name}.')

    @commands.command(name='demod')
    async def demod_command(self, ctx):
        if not bot_tools.is_superadmin(ctx.author.name):
            utils.log_body('[Bot#demod_command] Access denied to ' + ctx.author.name)
            return
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            return await ctx.send('Usage: demod <name>')

        [_, user_name] = command
        utils.log_kv('Demodding', user_name)

        if bot_db.is_mod(user_name):
            bot_db.remove_mod(user_name)
            await ctx.send(f'Demodded {user_name}.')
        else:
            await ctx.send(f'{user_name} is not a mod.')

    @commands.command(name='test')
    async def test_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')

    def get_jisho_results_message(self, keywords, start_index=0):
        n_to_show = 3

        results = bot_tools.jisho(keywords)

        if results is None:
            return f'Sorry, no results for {keywords}.'

        message_parts = []

        for idx, result in enumerate(results):
            if idx < start_index:
                continue
            if idx > start_index + (n_to_show - 1):
                break

            part_prefix = f'{utils.get_unicode_digit(idx + 1)}'
            jp_info = result['word_jp']
            reading_info = result['reading']
            english_info = ', '.join(result['english'])
            pos_info = '/'.join([
                bot_tools.shorten_part_of_speech(pos)
                for pos in result['parts_of_speech']
            ])

            message_part = \
                f'{part_prefix} {jp_info}・{reading_info} {english_info} [{pos_info}]'

            message_parts.append(message_part)

        message_prefix = 'gamegr2Hmmm'
        if len(results) == 1:
            message_suffix = '[1 meaning]'
        else:
            message_suffix = f'[{len(results)} meanings]'
        joined_message_parts = ' '.join(message_parts)
        message = f'{message_prefix} {joined_message_parts} {message_suffix}'
        return message

    @commands.command(name='jfrom')
    async def jisho_from_command(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except ValueError:
            return await ctx.send('Usage: !jfrom <result_number> <keywords>')

        [_, start_from, keywords] = command
        if (not start_from.isdigit()) or int(start_from) < 1:
            return await ctx.send('Usage: !jfrom <result_number> <keywords>')

        message = self.get_jisho_results_message(keywords, int(start_from) - 1)
        await ctx.send(message)

    @commands.command(name='j')
    async def jisho_command(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            return await ctx.send('Usage: !j <keywords>')

        [_, keywords] = command
        message = self.get_jisho_results_message(keywords)
        await ctx.send(message)


def main():
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
