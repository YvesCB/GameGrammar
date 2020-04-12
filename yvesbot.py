from twitchio.ext import commands
from twitchio.ext.commands.core import Command

import unicodedata
import itertools

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

    def get_jisho_results_message(self, keywords, sense_index=None):
        result = bot_tools.jisho(keywords)

        if result is None:
            return f'Sorry, no results for {keywords}.'

        n_senses_to_show = 3
        sense_start_index = 0
        utils.log_kv('sense_index', sense_index)
        if sense_index is not None:
            sense_indices_to_get = [sense_index]
        else:
            sense_indices_to_get = range(
                sense_start_index,
                min(len(result['senses']), sense_start_index + n_senses_to_show)
            )

        senses_parts = []

        for idx, sense in enumerate(result['senses']):
            if idx not in sense_indices_to_get:
                continue
            digit = utils.get_unicode_digit(idx + 1)
            definitions = ', '.join(sense['english_definitions'])

            # This code adds parts of speech after every sense.
            # pos = '/'.join([
            #     bot_tools.shorten_part_of_speech(pos)
            #     for pos in sense['parts_of_speech']
            # ])
            # if len(pos) > 0:
            #     senses_parts.append(f'{digit} {definitions} [{pos}]')
            # else:
            #     senses_parts.append(f'{digit} {definitions}')

            senses_parts.append(f'{digit} {definitions}')

        senses_string = ' '.join(senses_parts)

        pos_all = list(itertools.chain.from_iterable([
            s['parts_of_speech'] for s in result['senses']
        ]))
        pos_unique = list(set(pos_all))
        pos_short = [bot_tools.shorten_part_of_speech(pos) for pos in pos_unique]
        pos_string = '/'.join(pos_short)

        message_prefix = 'gamegr2Hmmm'
        message = \
            f'{message_prefix} {result["japanese"][0]["word"]}・' + \
            f'{result["japanese"][0]["reading"]} ' + \
            f'{senses_string} ' + \
            f'[{pos_string}]'
        return message

    @commands.command(name='j')
    async def jisho_command(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            return await ctx.send('Usage: !j <keywords>')

        [_, keywords] = command
        [keywords, sense_number] = bot_tools.get_trailing_numbers(keywords)
        if sense_number is None:
            message = self.get_jisho_results_message(keywords)
        else:
            message = self.get_jisho_results_message(keywords, sense_number - 1)
        await ctx.send(message)


def main():
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
