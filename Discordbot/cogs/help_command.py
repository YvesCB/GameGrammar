import discord
import asyncio
from discord.ext import commands

import bot_tools


"""
async def create_help_embed(ctx, cogs):
    help_embed = discord.Embed(
        title = 'Commands', 
        description = 'Here are all the commands supported by GrammarBot',
        color = discord.Color.blue()
    )
    help_embed.set_footer(
        text=f'Requested by {ctx.author.name}'
    )
    for cog_name, cog in cogs.items():
        if len(cog.get_commands()) == 0:
            continue
        value = []
        commands = cog.get_commands()
        for command in commands:
            try:
                await command.can_run(ctx)
                al = ', !'.join(command.aliases)
                value.append(f'**!{command.name}, !{al}**\n{command.help}\n\n')
            except:
                pass
        if len(value) > 0:
            value = ''.join(value)
            help_embed.add_field(
                name = cog_name,
                value = f'{value}',
                inline = False
                )
    return help_embed
"""

async def create_help_embeds(ctx, cogs, other_commands):
    embeds = []
    grouped_cogs = list(bot_tools.grouped(cogs, 2))
    for cog_group in grouped_cogs:
        embed = discord.Embed(
            title = f'Help Page {grouped_cogs.index(cog_group) + 1}/{len(grouped_cogs)}',
            description = 'Use `!help CommandName` to get more detailed info.',
            color = discord.Color.blue()
        )
        embed.set_footer(
            text=f'Requested by {ctx.author.name}. You can switch the page by reacting.'
        )
        for cog in cog_group:
            commands = cog.get_commands()
            command_string = ''
            for command in commands:
                try:
                    await command.can_run(ctx)
                    al = ', !'.join(command.aliases)
                    command_string += f'**!{command.name}' + f'/!{al}**' + f'\n{command.brief}\n{command.usage}\n\n'
                except:
                    pass
            
            text = cog.description
            text += f'\n\n{"".join(command_string)}'

            embed.add_field(
                name = f'**__{cog.qualified_name}__**',
                value = f'{text}',
                inline = False
            )
        embeds.append(embed)
    
    other_commands_text = '' 
    for command in other_commands:
        try:
            await command.can_run(ctx)
            al = ', !'.join(command.aliases)
            other_commands_text += f'**!{command.name}' + f'/!{al}**' + f'\n{command.brief}\n{command.usage}\n\n'
        except:
            pass
    
    if len(other_commands_text) != 0:
        embeds[-1].add_field(
            name = '**__Other__**',
            value = f'{other_commands_text}'
        )
    return embeds


def create_commmand_help_embed(ctx, command):
    embed = discord.Embed(
        title = f'Help for the `!{command.name}` command',
        description = f'{command.help}\n\n{command.usage}',
        color = discord.Color.blue()
    )
    embed.set_footer(
        text=f'Requested by {ctx.author.name}.'
    )
    return embed


class HelpCommmand(commands.Cog, name='Help'):
    """The help command will show you how to use the bot and what functionality there is."""
    def __init__(self, bot):
        self.bot = bot
        self.current = 0


    async def reaction_add(self, check, help_message, right_arrow, left_arrow, embeds):
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=600.0, check=check)
        except:
            return
        if str(reaction.emoji) == right_arrow:
            if self.current < len(embeds) - 1:
                self.current += 1
                await help_message.edit(embed=embeds[self.current])
        elif str(reaction.emoji) == left_arrow:
            if self.current > 0:
                self.current -= 1
                await help_message.edit(embed=embeds[self.current])

    async def reaction_remove(self, check, help_message, right_arrow, left_arrow, embeds):
        try:
            reaction, user = await self.bot.wait_for('reaction_remove', timeout=600.0, check=check)
        except:
            return
        if str(reaction.emoji) == right_arrow:
            if self.current < len(embeds) - 1:
                self.current += 1
                await help_message.edit(embed=embeds[self.current])
        elif str(reaction.emoji) == left_arrow:
            if self.current > 0:
                self.current -= 1
                await help_message.edit(embed=embeds[self.current])

    @commands.command(
        name='help', 
        aliases=['?', 'h'], 
        brief='Display the help message.',
        help='This command will display the overview help message or the specific help message when a command is specified.',
        usage='Usage: `!help/!h/!?` or `!help/!h/!? CommandName`')
    async def help_message(self, ctx):
        cogs = [cog for cog in self.bot.cogs.values() if cog.description[0] != '0']
        cogs = sorted(cogs, key=lambda x: x.qualified_name)
        other_commands = [command for command in self.bot.commands if command.cog is None]
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            try:
                command = bot_tools.parse_command(ctx.message.content, 0)
            except ValueError:
                return
            right_arrow = '\U000027A1'
            left_arrow = '\U00002B05'

            embeds = await create_help_embeds(ctx, cogs, other_commands)

            help_message = await ctx.send(embed=embeds[self.current])
            await help_message.add_reaction(left_arrow)
            await help_message.add_reaction(right_arrow)


            def check(reaction, user):
                return user == ctx.message.author and user != self.bot.user and (str(reaction.emoji) == right_arrow or left_arrow and reaction.message == help_message)

            while(True):
                task_add = asyncio.create_task(self.reaction_add(check, help_message, right_arrow, left_arrow, embeds))
                task_remove = asyncio.create_task(self.reaction_remove(check, help_message, right_arrow, left_arrow, embeds))

                try:
                    done, pending = await asyncio.wait({task_add, task_remove}, return_when=asyncio.FIRST_COMPLETED)
                except:
                    return
                if task_add in done or task_remove in done:
                    task_add.cancel()
                    task_remove.cancel()
    
        [_, command_name] = command
        command_name = command_name.replace('!','').replace('`','')
        requested_command = discord.utils.get(self.bot.commands, name=command_name)
        if requested_command is None:
            for command in self.bot.commands:
                if command_name in command.aliases:
                    requested_command = command
            if requested_command is None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx, 'Error', f'Not a recoginzed command. {ctx.command.usage}'))
                return
        await ctx.send(embed=create_commmand_help_embed(ctx, requested_command))


def setup(bot):
    bot.add_cog(HelpCommmand(bot))