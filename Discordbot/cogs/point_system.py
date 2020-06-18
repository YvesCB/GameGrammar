import discord
from discord.ext import commands

import bot_tools
import bot_db
import config


class PointSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_reaction_add(self, reaction, user):
        if isinstance(reaction.emoji, str):
            return
        elif reaction.emoji.id == config.point_emote_id and not reaction.message.author == user:
            bot_db.user_points_upsert(reaction.message.author.id, 'incr')
            user_points = bot_db.get_user_points(reaction.message.author.id)
            print(f'Incr. points for {reaction.message.author.name}. Now has {user_points["amount"]}')

    
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_reaction_remove(self, reaction, user):
        if isinstance(reaction.emoji, str):
            return
        elif reaction.emoji.id == config.point_emote_id and not reaction.message.author == user:
            bot_db.user_points_upsert(reaction.message.author.id, 'decr')
            user_points = bot_db.get_user_points(reaction.message.author.id)
            print(f'Decr. points for {reaction.message.author.name}. Now has {user_points["amount"]}')


def setup(bot):
    bot.add_cog(PointSystem(bot))