import discord
from discord.ext import commands

import bot_tools


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


class HelpCommmand(commands.Cog, name='Help command'):
    """This is the docstring"""
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='help', aliases=['?', 'h'], help='Displays the help message.\nUsage: `!help/!h/!?`')
    async def help_message(self, ctx):
        await ctx.send('\n'.join([f'{command.name} {command.cog.qualified_name}' for command in self.bot.commands if command.cog is not None]))


def setup(bot):
    bot.add_cog(HelpCommmand(bot))