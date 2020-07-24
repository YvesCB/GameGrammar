import discord
from discord.ext import commands

import bot_tools
import bot_db
import config


class StatsSystem(commands.Cog, name='Stats System'):
    count = 0
    
    def __init__(self, bot):
        self.bot = bot


    # async def count_messages(self, channel, member):
    #     async for message in channel.history(limit=None):
    #         if message.author.id == member.id:
    #             self.count += 1


    def create_user_embed(self, ctx, member):
        # self.count = 0

        # for channel in ctx.guild.channels:    
        #     if isinstance(channel, discord.TextChannel):
        #         await self.count_messages(channel, member)

        embed = discord.Embed(
            title = f'{member.name}\'s Info',
            color = discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'Requested by {ctx.author.name}')
        members = ctx.guild.members
        members = sorted(members, key=lambda member: member.joined_at)
        cnt = 1
        for member_rank in members:
            if member_rank.id == member.id : break
            cnt += 1

        suffix = 'th'
        if cnt % 10 == 1 and cnt != 11 : suffix = 'st'
        elif cnt % 10 == 2 and cnt != 12 : suffix = 'nd'
        elif cnt % 10 == 3 and cnt != 13 : suffix = 'rd'

        embed.add_field(
            name = 'Joined',
            value = f'{member.joined_at.strftime("%a, %d %b %Y, %H:%M:%S GMT")}\n{cnt}{suffix} to join this server!',
            inline = False
        )
        embed.add_field(
            name = 'Created',
            value = member.created_at.strftime("%a, %d %b %Y, %H:%M:%S GMT"),
            inline = False
        )
        user_points = bot_db.get_user_points(member.id)
        embed.add_field(
            name = 'Grammar points (Awarded by others via GamePad reaction)',
            value = user_points['amount'],
            inline = False
        )
        # embed.add_field(
        #     name = 'Messages',
        #     value = f'{self.count} in this server'
        # )
        return embed


    def create_server_embed(self, ctx):
        embed = discord.Embed(
            title = f'{ctx.guild.name}\'s Info',
            color = discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {ctx.author.name}')
        embed.add_field(
            name = 'Owner',
            value = ctx.guild.owner.name,
            inline = False
        )
        embed.add_field(
            name = 'Region',
            value = ctx.guild.region,
            inline = False
        )
        embed.add_field(
            name = 'Created at',
            value = ctx.guild.created_at.strftime("%a, %d %b %Y, %H:%M:%S GMT"),
            inline = False
        )
        embed.add_field(
            name = 'Member count',
            value = ctx.guild.member_count,
            inline = False
        )
        embed.add_field(
            name = 'Roles',
            value = ', '.join([roles.name for roles in ctx.guild.roles]),
            inline = False
        )
        return embed

    
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

        if author_rank > 20 : 
            embed.add_field(
                name = f'Rank {author_rank}: {ctx.author.name}',
                value = f'{author_points} Points!',
                inline = True
            )
        return embed


    
    @commands.guild_only()
    @commands.command(name='user_info', aliases=['ui'], help='Displays the info for a user. Your own if none is specified.\nUsage: `!user_info/!ui <user_ping>`')
    async def user_info(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            try:
                command = bot_tools.parse_command(ctx.message.content, 0)
            except ValueError:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Use `!user_info/!ui <ping>` or no ping to get your own.'))
                return
        if len(command) == 1:
            member = ctx.guild.get_member(ctx.author.id)
            await ctx.send(embed=self.create_user_embed(ctx, member))
        else:
            [_, mention] = command
            user_id = 0
            try: 
                user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
            except ValueError:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
                return
            member = ctx.guild.get_member(user_id)
            if member == None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            else:
                await ctx.send(embed=self.create_user_embed(ctx, member))
        

    @commands.guild_only()
    @commands.command(name='server_info', aliases=['si'], help='Displays the info for the server.\nUsage: `!server_info/!si`')
    async def server_info(self, ctx):
        await ctx.send(embed=self.create_server_embed(ctx))

    
    @commands.guild_only()
    @commands.command(name='leaderboard', aliases=['lb'], help='Displays the Grammar point Leaderboard for the server!\nUsage: `!leaderboard/!lb`')
    async def leaderboard(self, ctx):
        user_points = bot_db.get_all_user_points()
        points_dict = {user_points[i]['id'] : user_points[i]['amount'] for i in range(0,len(user_points))}

        points_dict = sorted(points_dict.items(), key=lambda x: x[1], reverse=True)
        # for i, k in points_dict:
        #     print(i, k)

        await ctx.send(embed = self.create_leader_embed(points_dict, ctx))


def setup(bot):
    bot.add_cog(StatsSystem(bot))