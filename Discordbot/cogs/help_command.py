import discord
from discord.ext import commands

import bot_tools


class HelpCommmand(commands.Cog, name='Help command'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='help', aliases=['?', 'h'], help='Displays the help message.\nUsage: `!help/!h/!?`')
    async def help_message(self, ctx):
        await ctx.send(embed=await bot_tools.create_help_embed(ctx, self.bot.cogs))


def setup(bot):
    bot.add_cog(HelpCommmand(bot))