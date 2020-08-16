import discord
from discord.ext import commands
from collections import Counter

import bot_tools
import bot_db
import config


class PointSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    def create_embed(self, ctx, value_string):
        embed = discord.Embed(
            title = 'Updating Point DB',
            color = discord.Color.blue()
        )
        embed.set_footer(text=f'Requested by {ctx.author.name}')

        embed.add_field(
            name = '**Checking Channels**',
            value = value_string,
            inline = False
        )

        return embed


    @commands.Cog.listener()
    @commands.guild_only()
    async def on_reaction_add(self, reaction, user):
        if isinstance(reaction.emoji, str):
            return
        elif reaction.emoji.id == config.point_emote_id and not reaction.message.author == user:
            bot_db.user_points_upsert(reaction.message.author.id, 'incr')
            user_points = bot_db.get_user_points(reaction.message.author.id)
            print(f'Incr. points for {reaction.message.author.name}. Now has {user_points["point_amount"]}')

    
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_reaction_remove(self, reaction, user):
        if isinstance(reaction.emoji, str):
            return
        elif reaction.emoji.id == config.point_emote_id and not reaction.message.author == user:
            bot_db.user_points_upsert(reaction.message.author.id, 'decr')
            user_points = bot_db.get_user_points(reaction.message.author.id)
            print(f'Decr. points for {reaction.message.author.name}. Now has {user_points["point_amount"]}')


    @commands.command(name='update_points', aliases=['up'], help='Update all point values for all users.\nCan only be used by admins!\nUsage: `!update_points/!up`')
    @bot_tools.is_admin()
    async def update_points(self, ctx):
        points = Counter()

        response = await ctx.send(embed=self.create_embed(ctx, 'Starting...'))

        value_string = ''
        reaction_count = 0

        print('Getting counts...')

        # response = await ctx.send(embed=self.create_embed(ctx, searched_channels, reaction_count))

        for channel in ctx.guild.text_channels:
            # print('Searching:', channel.name, '...')
            value_string += f'**{channel.name}** ...'
            reaction_count = 0
            # print(value_string)
            await response.edit(embed=self.create_embed(ctx, value_string))
            async for message in channel.history(limit=None):
                for reaction in message.reactions:
                    # print(type(reaction.emoji), reaction)
                    if not isinstance(reaction.emoji, str) and reaction.emoji.id == config.point_emote_id:
                        # print('Found Gamepad')
                        reaction_count += 1
                        async for user in reaction.users():
                            if user == message.author:
                                points[message.author.id] += reaction.count - 1
                                break
                        else:
                            points[message.author.id] += reaction.count
            value_string = value_string[:-3]
            value_string += f':white_check_mark: Found {reaction_count}\n'
            # print(value_string)
            await response.edit(embed=self.create_embed(ctx, value_string))
                    
        
        print(points)

        for elements in points.most_common():
            bot_db.user_points_update(elements[0], elements[1])


def setup(bot):
    bot.add_cog(PointSystem(bot))