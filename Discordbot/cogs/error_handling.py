import traceback
import sys
from discord.ext import commands
import discord
import time

import bot_tools


class CommandErrorHandler(commands.Cog):
    """0 Functionality for error handling."""
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx    : Context
        error  : Exception"""

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return
        
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'{ctx.command} has been disabled.'))

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'{ctx.command} can not be used in DMs.'))
            except:
                pass


        elif isinstance(error, bot_tools.AdminCheckFailure):
            return await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'{ctx.command} can only be used by admins.'))

        elif isinstance(error, bot_tools.OwnerCheckFailure):
            return await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'{ctx.command} can only be used by the server owner.'))


        print(f'{time.strftime("%a, %d %b %Y, %H:%M:%S GMT", time.gmtime())}Ignoring exception in command {format(ctx.command)}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot)) 