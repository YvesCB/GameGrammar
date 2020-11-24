import discord
import time
from datetime import datetime, timedelta
from discord.ext import commands

import bot_tools
import bot_db
import config


class ModSystem(commands.Cog, name='Moderation'):
    """Contains command and functionality concerning server moderation. This includes (for now) checking people's rap sheet, which is a quick overview of the most recent infractions, and warning people. Soon muting them for a given amount of time and banning them will be available as well."""
    def __init__(self, bot):
        self.bot = bot

    
    def create_sheet(self, ctx, _warns, _mutes, _bans, member):
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
                name = f'{len(_warns)} Warning(s)',
                value = warnings,
                inline = False
            )

        if len(_mutes) == 0:
            embed.add_field(
                name = 'Mutes',
                value = 'None',
                inline = False
            )
        else:
            mutes = ''
            cnt = 1
            for mute in _mutes:
                mutes += f'**{cnt}:** {mute["message"]}\n{mute["time"]} **in** <#{mute["channel"]}>\nMuted for {mute["amount"]}\n'
                cnt += 1

            embed.add_field(
                name = f'{len(_mutes)} Mute(s)',
                value = mutes,
                inline = False
            )

        if len(_bans) == 0:
            embed.add_field(
                name = 'Bans',
                value = 'None',
                inline = False
            )
        else:
            bans = ''
            cnt = 1
            for ban in _bans:
                bans += f'**{cnt}:** {ban["message"]}\n{ban["time"]} **in** <#{ban["channel"]}>\nBanned for {ban["amount"]}\n'
                cnt += 1

            embed.add_field(
                name = f'{len(_bans)} Ban(s)',
                value = bans,
                inline = False
            )

        return embed


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='warn', 
        aliases=['w'], 
        brief='Warn a user and log the warning.',
        help='This command allows you to warn a user when they break a rule or misbehave. The warning will be logged in the logging channel and it will be saved in the user\'s rap sheet which can be viewed with the rap sheet command. **This command can only be used by people with an admin role.**',
        usage='Usage: `!warn/!w UserPing/UserID WarningMessage`')
    async def warn(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
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

        await ctx.send(f'Warning logged.')

        warning = {'message': warn_message, 'time': time.strftime("%a, %d %b %Y, %H:%M:%S GMT", time.gmtime()), 'channel': ctx.message.channel.id}
        bot_db.add_warning(user_id, warning)

    
    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='mute',
        aliases=['m'],
        brief='Mute a user for a given amount of time.',
        help='This command can be used to mute a user for a specified amount of time. To specify the muted time please use a number followed by either the letter d for day, h for hour or m for minute. Only chose one and don\'t combine different time units. For example you can specify 10 hours as 10h but don\'t use 10h20m to combine hours and minutes. The user will receive the muted role for the time frame specified and will be unable to post messages, react to messages or join voice chats.',
        usage='Usage: `!warn/!w UserPing/UserID TimeAmount MuteReasonMessage`'
    )
    async def mute(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 3)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.`'))
            return
        
        [_, mention, time_amount, mute_message] = command

        error_embed = bot_tools.create_simple_embed(ctx, 'Erorr', f'Not a valid time format. Chose only one from days, hours, minutes. Don\'t mix them. Use `!help {ctx.command.name}` for more details.')

        mute_message = f'\"{mute_message}\" by <@{ctx.message.author.id}>'
        user_id = 0
        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return

        member = discord.utils.get(ctx.guild.members, id=user_id)
        if member == None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a member of this discord server!'))
            return

        mute_role = discord.utils.get(ctx.guild.roles, id=config.mute_role_id)
        log_channel = discord.utils.get(ctx.guild.channels, id=config.log_channel_id)

        # parse the time_amount:
        delta_string = ''
        if 'd' in time_amount:
            time_amount = time_amount.replace('d', '')
            if time_amount.isdigit():
                delta = timedelta(days=int(time_amount))
                delta_string = f'{time_amount} Day(s)'
            else:
                await ctx.send(embed=error_embed)
        elif 'h' in time_amount:
            time_amount = time_amount.replace('h', '')
            if time_amount.isdigit():
                delta = timedelta(hours=int(time_amount))
                delta_string = f'{time_amount} Hour(s)'
            else:
                await ctx.send(embed=error_embed)
        elif 'm' in time_amount:
            time_amount = time_amount.replace('m', '')
            if time_amount.isdigit():
                delta = timedelta(minutes=int(time_amount))
                delta_string = f'{time_amount} Minute(s)'
            else:
                await ctx.send(embed=error_embed)
        else:
            await ctx.send(embed=error_embed)

        new_time = datetime.utcnow() + delta

        await ctx.send(f'Muting {member.name} until {time.strftime("%a, %d %b %Y, %H:%M:%S GMT", new_time.timetuple())}.')
        await member.add_roles(mute_role, reason=None, atomic=True)

        await log_channel.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Muting', _description=f'Muting <@{user_id}> ({member.name}: {user_id}) in <#{ctx.message.channel.id}> Until {time.strftime("%a, %d %b %Y, %H:%M:%S GMT", new_time.timetuple())}\n**Reason:**\n{mute_message}'))

        muting = {'message': mute_message, 'time': time.strftime("%a, %d %b %Y, %H:%M:%S GMT", time.gmtime()), 'amount': delta_string, 'until': time.strftime("%a, %d %b %Y, %H:%M:%S GMT", new_time.timetuple()), 'channel': ctx.message.channel.id}
        bot_db.add_mute(user_id, muting)

        await discord.utils.sleep_until(new_time)

        # update member just in case
        member = discord.utils.get(ctx.guild.members, id=user_id)
        if member is not None:  
            await log_channel.send(f'Unmuting <@{user_id}>.')
            await member.remove_roles(mute_role, reason=None, atomic=True)
        else:
            # Member most likely left the server
            await log_channel.send(f'Tried to unmute member <@{user_id}> but they are no longer on the server.')


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='ban',
        aliases=['b'],
        brief='Ban a member from the server for a specified amount of time.',
        help='This command can be used to ban a member from the server. You can specify a time for how long the member should stay banned. Use the letters d for day, h for hour and m for minute. Do not mix time formats. If that time ellapses, the member will be unbanned and is free to rejoin the server. If `perma` is used as a time, then the member will be permanentally banned.',
        usage=r'Usage: `!ban\!b UserPing\UserID TimeAmount MessageDeleteDays BanReason`'
    )
    async def ban(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 4)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.`'))
            return
        
        [_, mention, time_amount, del_days, ban_message] = command

        error_embed = bot_tools.create_simple_embed(ctx, 'Erorr', f'Not a valid time format. Chose only one from days, hours, minutes. Don\'t mix them. Use `!help {ctx.command.name}` for more details.')

        ban_message = f'\"{ban_message}\" by <@{ctx.message.author.id}>'
        user_id = 0
        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return

        member = discord.utils.get(ctx.guild.members, id=user_id)
        if member == None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a member of this discord server!'))
            return

        log_channel = discord.utils.get(ctx.guild.channels, id=config.log_channel_id)

        # parse the time_amount:
        delta_string = ''
        if 'd' in time_amount:
            time_amount = time_amount.replace('d', '')
            if time_amount.isdigit():
                delta = timedelta(days=int(time_amount))
                delta_string = f'{time_amount} Day(s)'
            else:
                await ctx.send(embed=error_embed)
        elif 'h' in time_amount:
            time_amount = time_amount.replace('h', '')
            if time_amount.isdigit():
                delta = timedelta(hours=int(time_amount))
                delta_string = f'{time_amount} Hour(s)'
            else:
                await ctx.send(embed=error_embed)
        elif 'm' in time_amount:
            time_amount = time_amount.replace('m', '')
            if time_amount.isdigit():
                delta = timedelta(minutes=int(time_amount))
                delta_string = f'{time_amount} Minute(s)'
            else:
                await ctx.send(embed=error_embed)
        elif time_amount == 'perma':
            delta = datetime.utcnow()
            delta_string = 'Permanentaly'
        else:
            await ctx.send(embed=error_embed)

        new_time = datetime.utcnow() + delta
        until = ''
        if time_amount == 'perma':
            until = 'permanentaly'
        else:
            until = f'until {time.strftime("%a, %d %b %Y, %H:%M:%S GMT", new_time.timetuple())}'

        await ctx.send(f'Banning {member.name} {until}.')
        await ctx.guild.ban(member, reason=ban_message, delete_message_days=del_days)

        await log_channel.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Banning', _description=f'Banning <@{user_id}> ({member.name}: {user_id}) in <#{ctx.message.channel.id}> {until}.\n**Reason:**\n{ban_message}'))

        banning = {'message': ban_message, 'time': time.strftime("%a, %d %b %Y, %H:%M:%S GMT", time.gmtime()), 'amount': delta_string, 'until': until, 'channel': ctx.message.channel.id}
        bot_db.add_ban(user_id, banning)

        if time_amount == 'perma':
            return

        await discord.utils.sleep_until(new_time)

        # update member just in case
        await log_channel.send(f'Unbanning <@{user_id}>.')
        await ctx.guild.unban(self.bot.get_user(user_id), reason='Ban time elapsed')


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='remove_warning', 
        aliases=['rw'], 
        brief='Remove a given warning from the user.',
        help='This command will remove the specified warning from the user\'s list of warnings. The warning list can be found in the user\'s rap sheet. Use the number listed in the sheet to see which warning to remove. **This command can only be used by users with an admin role.**',
        usage='Usage: `!remove_warning/!rw UserPing/UserID WarningNumber`')
    async def rem_warn(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
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
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help{ctx.command.name}` for more details.'))
            return
        
        if bot_db.remove_warning(user_id, int(number)):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Warnings', _description=f'Successfully removed warning **{number}** from <@{user_id}>\'s warnings.'))
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no warning with that number!'))

    
    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='remove_mute',
        aliases=['rm'],
        brief='Remove a given mute from the user.',
        help='This command can be used to remove a mute entry from the User\'s rap sheet and the internal database. This is mostly to remove accidental, wrong or test entries. To specify the entry to remove, use the number that is shown for the entry on the rap sheet.',
        usage='Usage: `!remove_mute/!rm UserPing/UserID MuteNumber`'
    )
    async def rem_mute(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
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
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help{ctx.command.name}` for more details.'))
            return
        
        if bot_db.remove_mute(user_id, int(number)):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Mutes', _description=f'Successfully removed mute **{number}** from <@{user_id}>\'s mutes.'))
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no mute with that number!'))


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='remove_ban',
        aliases=['rb'],
        brief='Remove a given ban from the user.',
        help='This command can be used to remove a ban entry from the User\'s rap sheet and the internal database. This is mostly to remove accidental, wrong or test entries. To specify the entry to remove, use the number that is shown for the entry on the rap sheet.',
        usage=r'Usage: `!remove_ban/!rb UserPing/UserID BanNumber`'
    )
    async def rem_ban(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
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
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help{ctx.command.name}` for more details.'))
            return
        
        if bot_db.remove_ban(user_id, int(number)):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Bans', _description=f'Successfully removed ban **{number}** from <@{user_id}>\'s bans.'))
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no bans with that number!'))


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='rap_sheet', 
        aliases=['rs'], 
        brief='Display the rap sheet of the specified user.',
        help='This command will show you the rap sheet of the specified user. The rap sheet is a summary of the user\'s past recieved warnings, mutes and bans. The rap sheet serves as an overview of the user\'s behaviour on the server. **This command can only be used by users with an admin role.**',
        usage='Usage: `!rap_sheet/!rs UserPing/UserID`')
    async def rap_sheet(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return

        [_, mention] = command
        user_id = 0
        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return

        warns = bot_db.get_user_warnings(user_id)
        mutes = bot_db.get_user_mutes(user_id)
        bans = bot_db.get_user_bans(user_id)
        if warns == None: 
            warns = []
        if mutes == None:
            mutes = []
        if bans == None:
            bans = []
        await ctx.send(embed=self.create_sheet(ctx, warns, mutes, bans, self.bot.get_user(user_id)))


def setup(bot):
    bot.add_cog(ModSystem(bot))