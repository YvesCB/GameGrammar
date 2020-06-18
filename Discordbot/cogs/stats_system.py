import discord
from discord.ext import commands

import bot_tools
import config


class StatsSystem(commands.Cog, name='Stats System'):
    count = 0
    
    def __init__(self, bot):
        self.bot = bot


    async def count_messages(self, channel, member):
        async for message in channel.history(limit=None):
            if message.author.id == member.id:
                self.count += 1


    async def create_user_embed(self, ctx, member):
        self.count = 0

        for channel in ctx.guild.channels:    
            if isinstance(channel, discord.TextChannel):
                await self.count_messages(channel, member)

        embed = discord.Embed(
            title = f'{member.name}\'s Info',
            color = discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'Requested by {ctx.author.name}')
        embed.add_field(
            name = 'Joined',
            value = member.created_at.strftime("%a, %d %b %Y, %H:%M:%S GMT"),
            inline = False
        )
        embed.add_field(
            name = 'Created',
            value = member.created_at.strftime("%a, %d %b %Y, %H:%M:%S GMT"),
            inline = False
        )
        embed.add_field(
            name = 'Messages',
            value = f'{self.count} in this server'
        )
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
            message = await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Stats', _description='Getting data... (Can take a few seconds)'))
            await message.edit(embed=await self.create_user_embed(ctx, member))
        else:
            [_, mention] = command
            user_id = 0
            try: 
                user_id = int(mention.replace('<@', '').replace('>', ''))
            except ValueError:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
                return
            member = ctx.guild.get_member(user_id)
            if member == None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            else:
                message = await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Stats', _description='Getting data...(Can take a few seconds'))
                await message.edit(embed=await self.create_user_embed(ctx, member))
        

    @commands.guild_only()
    @commands.command(name='server_info', aliases=['si'], help='Displays the info for the server.\nUsage: `!server_info/!si`')
    async def server_info(self, ctx):
        await ctx.send(embed=self.create_server_embed(ctx))


def setup(bot):
    bot.add_cog(StatsSystem(bot))