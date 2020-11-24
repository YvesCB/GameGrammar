import discord
from discord.ext import commands
from collections import Counter

import bot_tools
import bot_db
import config


class PointSystem(commands.Cog, name='Points'):
    """There is a point system on this server. You can give other people points when they post something useful, interesting or fun. The way you do this is by reaction to their message with the <:gamepad:602902421924085771> emote from this server. If you do that, a \"GrammarPoint\" will be added to the points of the user that posted the message. You get as many points as users react to your message. There is a leaderboard for the points you can check out via the leaderboard command."""
    def __init__(self, bot):
        self.bot = bot

    
    def create_leader_embed(self, points_dict, ctx):
        point_sum = 0
        for i, k in points_dict :
            point_sum += k

        embed = discord.Embed(
            title = 'Grammar Point Leader Board',
            description = f'See how you rank in terms of Grammar Points! A total of **{point_sum} Points** have been given on this server!',
            color = discord.Color.blue()
        )
        embed.set_footer(text=f'Requested by {ctx.author.name}')
        cnt = 1
        author_rank = 0
        author_points = 0

        for i, k in points_dict:
            member = ctx.guild.get_member(i)
            try :
                if member.id == ctx.author.id : 
                    author_rank = cnt
                    author_points = k
                if cnt <= 20: 
                    embed.add_field(
                        name = f'Rank {cnt}: {member.name}',
                        value = f'{k} Points!',
                        inline = True
                    )
                cnt += 1
            except : 
                print("Skipped member on lb that is no longer on the server.")

        if author_rank > 20 and author_rank != 0: 
            embed.add_field(
                name = f'Rank {author_rank}: {ctx.author.name}',
                value = f'{author_points} Points!',
                inline = True
            )
        return embed


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
    async def on_raw_reaction_add(self, payload):
        channel = discord.utils.get(self.bot.get_guild(payload.guild_id).text_channels, id=payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if isinstance(payload.emoji, str):
            return
        elif payload.emoji.id == config.point_emote_id and not message.author.id == payload.user_id:
            bot_db.user_points_upsert(message.author.id, 'incr')
            user_points = bot_db.get_user_points(message.author.id)
            print(f'Incr. points for {message.author.name}. Now has {user_points["point_amount"]}')

    
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_reaction_remove(self, payload):
        channel = discord.utils.get(self.bot.get_guild(payload.guild_id).text_channels, id=payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if isinstance(payload.emoji, str):
            return
        elif payload.emoji.id == config.point_emote_id and not message.author.id == payload.user_id:
            bot_db.user_points_upsert(message.author.id, 'decr')
            user_points = bot_db.get_user_points(message.author.id)
            print(f'Decr. points for {message.author.name}. Now has {user_points["point_amount"]}')


    @commands.guild_only()
    @commands.command(
        name='leaderboard', 
        aliases=['lb'], 
        brief='Display the GrammarPoint leaderboard for the server.',
        help='This command will display the GrammarPoint leaderboard for the top 20 users on the server. If you want to know more about how to get GrammarPoints check the help command for the point system section the help command.',
        usage='Usage: `!leaderboard\!lb`')
    async def leaderboard(self, ctx):
        user_points = bot_db.get_all_user_points()
        points_dict = {user_points[i]['id'] : user_points[i]['point_amount'] for i in range(0,len(user_points))}

        points_dict = sorted(points_dict.items(), key=lambda x: x[1], reverse=True)
        # for i, k in points_dict:
        #     print(i, k)

        await ctx.send(embed = self.create_leader_embed(points_dict, ctx))

    
    @bot_tools.is_admin()
    @commands.command(
        name='update_points', 
        aliases=['up'], 
        brief='Update all the GrammarPoint values for all users.',
        help='This command will go through every single message on the server and count the GamePad reactions for each message and will update the point values for each user accordingly. Note that this takes a while because it has to go through thousands of messages. **This command can only be used by users with an admin role.**',
        usage='Usage: `!update_points\!up`')
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