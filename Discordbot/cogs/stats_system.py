import discord
from discord.ext import commands

import bot_tools
import bot_db
import config


class StatsSystem(commands.Cog, name='Stats'):
    """You can view a whole bunch of statistics about yourself, other users or the server itself. For now you can see some user stats like when a user joined the server or you can see stats about the server itself like the amount of users on it."""
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
            value = user_points['point_amount'],
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

    
    @commands.guild_only()
    @commands.command(
        name='user_info', 
        aliases=['ui'], 
        brief='Desplay the info for a user.',
        help='Use this command to see some stats about a given user. It will show when the user account was created, when they joined this server and a bunch of other stats. If you don\'t specify a user via a ping or the ID then it will display your own info.',
        usage=r'Usage: `!user_info\!ui (UserPing\UserID)`')
    async def user_info(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            try:
                command = bot_tools.parse_command(ctx.message.content, 0)
            except ValueError:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
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
    @commands.command(
        name='server_info', 
        aliases=['si'], 
        brief='Display the server info.',
        help='This command will show you some information about the server. This includes the number of users, the roles that exist, the server owner, the current voice chat server, when the server was created etc.',
        usage='Usage: `!server_info\!si`')
    async def server_info(self, ctx):
        await ctx.send(embed=self.create_server_embed(ctx))


def setup(bot):
    bot.add_cog(StatsSystem(bot))