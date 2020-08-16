import discord
import time
from discord.ext import commands

import bot_tools
import bot_db
import config


class ModSystem(commands.Cog, name='Modaration System'):

    
    def create_sheet(self, ctx, _warns, member):
        embed = discord.Embed(
            title = f'Rap Sheet of {member.name} ({member.id})',
            description = 'All the infractions of the selected user.',
            color = discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar_url)

        if len(_warns) == 0:
            embed.add_field(
                name = 'Warnings',
                value = 'None',
                inline = False
            )
        else:
            warnings = ''
            cnt = 1
            for warning in _warns:
                warnings += f'**{cnt}:** {warning["message"]}\n{warning["time"]} **in** <#{warning["channel"]}>\n'
                cnt += 1

            embed.add_field(
                name = 'Warnings',
                value = warnings,
                inline = False
            )

        return embed


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(name='warn', aliases=['w'], help='Warns a user and stores the warning message, channel and time.\nUsage: `!warn/!w <user_ping>`')
    async def warn(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Use `!warn/w <user_ping> <warn message>`.'))
            return
        
        [_, mention, warn_message] = command
        warn_message = f'\"{warn_message}\" by <@{ctx.message.author.id}>'
        user_id = 0
        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return

        if discord.utils.get(ctx.guild.members, id=user_id) == None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a member of this discord server!'))
            return

        log_channel = discord.utils.get(ctx.guild.channels, id=config.log_channel_id)

        await log_channel.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Warning', _description=f'Warning <@{user_id}> ({discord.utils.get(ctx.guild.members, id=user_id).name}: {user_id}) in <#{ctx.message.channel.id}>\n**Warning:**\n{warn_message}'))

        warning = {'message': warn_message, 'time': time.strftime("%a, %d %b %Y, %H:%M:%S GMT", time.gmtime()), 'channel': ctx.message.channel.id}
        bot_db.add_warning(user_id, warning)


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(name='remove_warning', aliases=['rw'], help='Removes the specified warning from the user\'s Rap Sheet.\nUsage: `!remove_warning/!rw <user_ping> <number>`')
    async def rem_warn(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Use `!remove_warning/rw <number>`.'))
            return

        [_, mention, number] = command
        user_id = 0

        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return

        if discord.utils.get(ctx.guild.members, id=user_id) == None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a member of this discord server!'))
            return

        if not number.isdigit():
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Use `!remove_warning/rw <number>`.'))
            return
        
        if bot_db.remove_warning(user_id, int(number)):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Warnings', _description=f'Successfully removed warning **{number}** from <@{user_id}>\'s warnings.'))
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no warning with that number!'))


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(name='rap_sheet', aliases=['rs'], help='Displays the user\'s rap sheet with a list of warnings and mutes.\nUsage: `!rap_sheet/!rs <user_ping>`')
    async def rap_sheet(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Use `!rap_sheet/rs <user_ping>`.'))
            return

        [_, mention] = command
        user_id = 0
        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return
        
        if discord.utils.get(ctx.guild.members, id=user_id) == None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a member of this discord server!'))
            return

        warns = bot_db.get_user_warnings(user_id)
        await ctx.send(embed=self.create_sheet(ctx, warns, discord.utils.get(ctx.guild.members, id=user_id)))


def setup(bot):
    bot.add_cog(ModSystem(bot))