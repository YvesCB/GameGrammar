import discord
from discord.ext import commands
from collections import Counter

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


    @commands.command(name='update_points', aliases=['up'], help='Update all point values for all users.\nCan only be used by admins!\nUsage: `!update_points/!up`')
    @bot_tools.is_admin()
    async def update_points(self, ctx):
        points = Counter()

        print('Getting counts...')

        for channel in ctx.guild.text_channels:
            async for message in channel.history(limit=None):
                for reaction in message.reactions:
                    print(type(reaction.emoji), reaction)
                    if not isinstance(reaction.emoji, str) and reaction.emoji.id == config.point_emote_id:
                        print('Beep')
                        async for user in reaction.users():
                            if user != message.author:
                                points[message.author.id] += reaction.count - 1
                                break
                        else:
                            points[message.author.id] += reaction.count
                    
        
        print(points)


def setup(bot):
    bot.add_cog(PointSystem(bot))