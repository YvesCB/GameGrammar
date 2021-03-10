import discord
from datetime import datetime, timedelta
from discord.ext import commands, tasks

import bot_tools
import bot_db
import config


class ModSystem(commands.Cog, name='Moderation'):
    """Contains command and functionality concerning server moderation. This includes warning, muting and baning people and checking people's rap sheet, which is a quick overview of the most recent infractions, warnings, mutes and bans."""

    def __init__(self, bot):
        self.bot = bot
        self.unban_unmute.start()

    
    def create_sheet(self, ctx, _warns, _mutes, _bans, user, user_id, user_name):
        if user is not None:
            embed = discord.Embed(
                title = f'Rap Sheet of {user.name} ({user.id})',
                description = f'All the infractions of the selected user <@{user.id}>',
                color = discord.Color.blue()
            )
            embed.set_thumbnail(url=user.avatar_url)
        else:
            embed = discord.Embed(
                title = f'Rap Sheet of {user_name} ({user_id})',
                description = 'All the infractions of the selected user. This user has deleted their account.',
                color = discord.Color.blue()
            )

        if len(_warns) == len(_mutes) == len(_bans) == 0:
            embed.add_field(
                name = 'Infractions',
                value = 'Nothing has been logged for this user.',
                inline = False
            )
            return embed

        now = datetime.utcnow()
        latest = datetime.min

        if len(_warns) > 0:
            warnings = ''
            cnt = 1
            for warning in _warns:
                warnings += f'**{cnt}:** \"{warning["message"]}\" by <@{warning["mod_id"]}>\n{warning["time"].strftime("%d %b %y, %H:%M:%S GMT")} **in** <#{warning["channel"]}>\n'
                cnt += 1
                if warning['time'] > latest:
                    latest = warning['time']

            embed.add_field(
                name = f'{len(_warns)} Warning(s)',
                value = warnings,
                inline = False
            )

        if len(_mutes) > 0:
            mutes = ''
            cnt = 1
            for mute in _mutes:
                mutes += f'**{cnt}:** \"{mute["message"]}\" by <@{mute["mod_id"]}>\n{mute["time"].strftime("%d %b %y, %H:%M:%S GMT")} **in** <#{mute["channel"]}>\nMuted for {mute["amount"]}\n'
                cnt += 1
                if mute['time'] > latest:
                    latest = mute['time']

            embed.add_field(
                name = f'{len(_mutes)} Mute(s)',
                value = mutes,
                inline = False
            )

        if len(_bans) > 0:
            bans = ''
            cnt = 1
            for ban in _bans:
                bans += f'**{cnt}:** \"{ban["message"]}\" by <@{ban["mod_id"]}>\n{ban["time"].strftime("%d %b %y, %H:%M:%S GMT")} **in** <#{ban["channel"]}>\nBanned for {ban["amount"]}\n'
                cnt += 1
                if ban['time'] > latest:
                    latest = ban['time']

            embed.add_field(
                name = f'{len(_bans)} Ban(s)',
                value = bans,
                inline = False
            )

        member = discord.utils.get(ctx.guild.members, id=user_id)
        if member is not None:
            embed.add_field(
                name = 'Joined Server',
                value = member.joined_at.strftime("%d %b %y, %H:%M:%S GMT"),
                inline = True
            )
        else:
            embed.add_field(
                name = 'Joined Server',
                value = 'Currently not on server',
                inline = True
            )

        if latest != datetime.min:
            latest = (now - latest).seconds
            timestring = ''
            days, remainder = divmod(latest, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            if days != 0:
                timestring += f'{days}d '
            if hours != 0 or len(timestring) != 0:
                timestring += f'{hours}h '
            if minutes != 0 or len(timestring) != 0:
                timestring += f'{minutes}m '
            if seconds != 0 or len(timestring) != 0:
                timestring += f'{seconds}s'
            embed.add_field(
                name = 'Time since latest action',
                value = timestring,
                inline = True
            )
        else:
            embed.add_field(
                name = 'Time since latest action',
                value = 'Never',
                inline = True
            )

        return embed


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='warn', 
        aliases=['w'], 
        brief='Warn a user and log the warning.',
        help='This command allows you to warn a user when they break a rule or misbehave. The warning will be logged in the logging channel and it will be saved in the user\'s rap sheet which can be viewed with the rap sheet command. **This command can only be used by people with an admin role.**',
        usage='Usage: `!warn/!w UserPing/UserID WarnMsg`')
    async def warn(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return
        
        [_, mention, warn_message] = command
        user_id = 0
        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return

        user = await self.bot.fetch_user(user_id)

        now = datetime.utcnow()

        if user is None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a valid user!'))
            return

        log_channel = discord.utils.get(ctx.guild.channels, id=config.log_channel_id)

        await log_channel.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Warning', _description=f'Warning <@{user_id}> ({user.name}: {user_id}) in <#{ctx.message.channel.id}>\n**Warning:**\n\"{warn_message}\" by <@{ctx.message.author.id}>'))

        await ctx.send(f'Warning logged.')

        user_info = bot_db.user_get({'_id': user_id})
        if user_info is None:
            user_info = bot_db.user_new(user_id, user.name)

        warning = {'message': warn_message, 'mod_id': ctx.message.author.id, 'time': now, 'channel': ctx.message.channel.id}
        bot_db.user_update(action='push', filter={'_id': user_id}, list_name='warnings', new_value=warning)

    
    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='mute',
        aliases=['m'],
        brief='Mute a user for a given amount of time.',
        help='This command can be used to mute a user for a specified amount of time. To specify the muted time please use a number followed by either the letter d for day, h for hour or m for minute. Only chose one and don\'t combine different time units. For example you can specify 10 hours as 10h but don\'t use 10h20m to combine hours and minutes. The user will receive the muted role for the time frame specified and will be unable to post messages, react to messages or join voice chats.',
        usage='Usage: `!mute/!m UserPing/UserID Time Reason`'
    )
    async def mute(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 3)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.`'))
            return
        
        [_, mention, time_amount, mute_message] = command

        error_embed = bot_tools.create_simple_embed(ctx, 'Erorr', f'Not a valid time format. Chose only one from days, hours, minutes. Don\'t mix them. Use `!help {ctx.command.name}` for more details.')

        user_id = 0
        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return

        user = await self.bot.fetch_user(user_id)

        now = datetime.utcnow()

        if user is None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a valid user!'))
            return

        if user not in ctx.guild.members:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not on this server and can thus not be muted!'))
            return

        member = discord.utils.get(ctx.guild.members, id=user.id)

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
                return
        else:
            await ctx.send(embed=error_embed)
            return

        new_time = now + delta

        await ctx.send(f'Muting {member.name} until {new_time.strftime("%d %b %y, %H:%M:%S GMT")}.')
        await member.add_roles(mute_role, reason=f'Muted by {ctx.message.author.name}', atomic=True)

        await log_channel.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Muting', _description=f'Muting <@{user_id}> ({member.name}: {user_id}) in <#{ctx.message.channel.id}> until {new_time.strftime("%d %b %y, %H:%M:%S GMT")}\n**Reason:**\n\"{mute_message}\" by <@{ctx.message.author.id}>'))

        user_info = bot_db.user_get({'_id': user_id})
        if user_info is None:
            user_info = bot_db.user_new(user_id, member.name)

        muting = {'message': mute_message, 'mod_id': ctx.message.author.id, 'time': now, 'amount': delta_string, 'until': new_time, 'channel': ctx.message.channel.id}
        bot_db.user_update(action='push', filter={'_id': user_id}, list_name='mutes', new_value=muting)


        bot_db.server_update(action='push', list_name='unmute_queue', new_value={'time': new_time, 'id': user_id})
        # await discord.utils.sleep_until(new_time)

        # # update member just in case
        # member = discord.utils.get(ctx.guild.members, id=user_id)
        # if member is not None:  
        #     await log_channel.send(f'Unmuting <@{user_id}>.')
        #     await member.remove_roles(mute_role, reason=None, atomic=True)
        # else:
        #     # Member most likely left the server
        #     await log_channel.send(f'Tried to unmute member <@{user_id}> but they are no longer on the server.')


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='ban',
        aliases=['b'],
        brief='Ban a member from the server for a specified amount of time.',
        help='This command can be used to ban a member from the server. You can specify a time for how long the member should stay banned. Use the letters d for day, h for hour and m for minute. Do not mix time formats. If that time ellapses, the member will be unbanned and is free to rejoin the server. If `perma` is used as a time, then the member will be permanentaly banned.',
        usage=r'Usage: `!ban\!b UserPing\UserID Time MsgDelDays Reason`'
    )
    async def ban(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 4)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.`'))
            return
        
        [_, mention, time_amount, del_days, ban_message] = command

        error_embed = bot_tools.create_simple_embed(ctx, 'Erorr', f'Not a valid time format. Chose only one from days, hours, minutes. Don\'t mix them. Use `!help {ctx.command.name}` for more details.')

        user_id = 0
        try: 
            user_id = int(mention.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid ping!'))
            return

        user = await self.bot.fetch_user(user_id)

        now = datetime.utcnow()

        if user is None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a valid user!'))
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
            return

        new_time = now + delta
        until = ''
        if time_amount == 'perma':
            until = 'permanentaly'
        else:
            until = f'until {new_time.strftime("%d %b %y, %H:%M:%S GMT")}'

        await ctx.send(f'Banning {user.name} {until}.')
        await ctx.guild.ban(user, reason=ban_message, delete_message_days=del_days)

        await log_channel.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Banning', _description=f'Banning <@{user_id}> ({user.name}: {user_id}) in <#{ctx.message.channel.id}> {until}.\n**Reason:**\n\"{ban_message}\" by <@{ctx.message.author.id}>'))

        user_info = bot_db.user_get({'_id': user_id})
        if user_info is None:
            user_info = bot_db.user_new(user_id, user_name)

        banning = {'message': ban_message, 'mod_id': ctx.message.author.id, 'time': now, 'amount': delta_string, 'until': new_time, 'channel': ctx.message.channel.id}
        bot_db.user_update(action='push', filter={'_id': user_id}, list_name='bans', new_value=banning)

        if time_amount == 'perma':
            return

        bot_db.server_update(action='push', list_name='unban_queue', new_value={'time': new_time, 'id': user_id})
        
        # await discord.utils.sleep_until(new_time)

        # # update member just in case
        # await log_channel.send(f'Unbanning <@{user_id}>.')
        # await ctx.guild.unban(self.bot.get_user(user_id), reason='Ban time elapsed')


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='remove_warning', 
        aliases=['rw'], 
        brief='Remove a warning from the user.',
        help='This command will remove the specified warning from the user\'s list of warnings. The warning list can be found in the user\'s rap sheet. Use the number listed in the sheet to see which warning to remove. **This command can only be used by users with an admin role.**',
        usage='Usage: `!remove_warning/!rw UserPing/UserID WarnNum`')
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

        if not number.isdigit():
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help{ctx.command.name}` for more details.'))
            return

        number = int(number)

        user_info = bot_db.user_get({'_id': user_id})

        if user_info is None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no warning with that number for this user!'))
            return

        if len(user_info['warnings']) >= number:
            bot_db.user_update('pull', filter={'_id': user_id}, list_name='warnings', pull_dict={'time': user_info['warnings'][number - 1]['time']})
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Warnings', _description=f'Successfully removed warning **{number}** from <@{user_id}>\'s warnings.'))

        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no warning with that number!'))

    
    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='remove_mute',
        aliases=['rm'],
        brief='Remove a mute from the user.',
        help='This command can be used to remove a mute entry from the User\'s rap sheet and the internal database. This is mostly to remove accidental, wrong or test entries. To specify the entry to remove, use the number that is shown for the entry on the rap sheet.',
        usage='Usage: `!remove_mute/!rm UserPing/UserID MuteNum`'
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

        if not number.isdigit():
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help{ctx.command.name}` for more details.'))
            return
        
        now = datetime.utcnow()

        number = int(number)

        user_info = bot_db.user_get({'_id': user_id})

        if user_info is None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no mute with that number!'))
            return

        mute_role = discord.utils.get(ctx.guild.roles, id=config.mute_role_id)
        log_channel = discord.utils.get(ctx.guild.channels, id=config.log_channel_id)

        if len(user_info['mutes']) >= number:
            bot_db.user_update('pull', filter={'_id': user_id}, list_name='mutes', pull_dict={'time': user_info['mutes'][number - 1]['time']})
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Mutes', _description=f'Successfully removed mute **{number}** from <@{user_id}>\'s mutes.'))
            if now <= user_info['mutes'][number - 1]['until']:
                member = discord.utils.get(ctx.guild.members, id=user_id)
                if member is not None:
                    await member.remove_roles(mute_role, reason='Mute removed', atomic=True)
                    await log_channel.send(f"Unmuting <@{user_info['_id']}>.")
                else:
                    await log_channel.send(f"Tried to unmute member <@{user_info['_id']}> but they are no longer on the server.")
                bot_db.server_update('pull', list_name='unmute_queue', pull_dict={'time': user_info['mutes'][number - 1]['until']})
        
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no mute with that number!'))


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='remove_ban',
        aliases=['rb'],
        brief='Remove a ban from the user.',
        help='This command can be used to remove a ban entry from the User\'s rap sheet and the internal database. This is mostly to remove accidental, wrong or test entries. To specify the entry to remove, use the number that is shown for the entry on the rap sheet.',
        usage=r'Usage: `!remove_ban/!rb UserPing/UserID BanNum`'
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

        if not number.isdigit():
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help{ctx.command.name}` for more details.'))
            return
        
        now = datetime.utcnow()

        number = int(number)

        user_info = bot_db.user_get({'_id': user_id})

        if user_info is None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no ban with that number!'))
            return

        log_channel = discord.utils.get(ctx.guild.channels, id=config.log_channel_id)

        if len(user_info['bans']) <= number:
            bot_db.user_update('pull', filter={'_id': user_id}, list_name='bans', pull_dict={'time': user_info['bans'][number - 1]['time']})
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Bans', _description=f'Successfully removed ban **{number}** from <@{user_id}>\'s bans.'))
            if now <= user_info['bans'][number - 1]['until']:
                user = await self.bot.fetch_user(user_id)
                guild = ctx.guild
                if user is not None:
                    await guild.unban(user, reason='Manually unbanned')
                    await log_channel.send(f"Unbanning <@{user_id}>.")
                else:
                    await log_channel.send(f"Tried to unban member <@{unban['id']}> but the account no longer seems to exist.")
                bot_db.server_update('pull', list_name='unban_queue', pull_dict={'time': user_info['bans'][number - 1]['until']})

        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'There is no ban with that number!'))


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='rap_sheet', 
        aliases=['rs'], 
        brief='Display the rap sheet of the user.',
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

        user = None
        user_name = ''
        try:
            user = await self.bot.fetch_user(user_id)
        except:
            user_name = 'Unavailalbe'

        if user is not None: 
            user_name = user.name

        user_info = bot_db.user_get({'_id': user_id})
        if user_info is None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='No logs exist.'))
            return

        await ctx.send(embed=self.create_sheet(ctx, user_info['warnings'], user_info['mutes'], user_info['bans'], user, user_id, user_name))


    def cog_unload(self):
        self.unban_unmute.cancel()


    @tasks.loop(minutes=1)
    async def unban_unmute(self):
        unmute_queue = bot_db.server_get()['unmute_queue']
        unban_queue = bot_db.server_get()['unban_queue']
        guild = self.bot.guilds[0]
        mute_role = discord.utils.get(guild.roles, id=bot_db.server_get()['mute_role_id'])
        log_channel = discord.utils.get(guild.channels, id=bot_db.server_get()['log_channel_id'])
        now = datetime.utcnow()
        for unmute in unmute_queue:
            if now > unmute['time']:
                member = discord.utils.get(guild.members, id=unmute['id'])
                if member is not None:
                    await member.remove_roles(mute_role, reason='Mute time elapsed', atomic=True)
                    await log_channel.send(f"Unmuting <@{unmute['id']}>.")
                else:
                    await log_channel.send(f"Tried to unmute member <@{unmute['id']}> but they are no longer on the server.")
                bot_db.server_update('pull', list_name='unmute_queue', pull_dict={'time': unmute['time']})
        for unban in unban_queue:
            if now > unban['time']:
                user = await self.bot.fetch_user(unban['id'])
                if user is not None:
                    await guild.unban(user, reason='Ban time elapsed')
                    await log_channel.send(f"Unbanning <@{unban['id']}>.")
                else:
                    await log_channel.send(f"Tried to unban member <@{unban['id']}> but the account no longer seems to exist.")
                bot_db.server_update('pull', list_name='unban_queue', pull_dict={'time': unban['time']})


def setup(bot):
    bot.add_cog(ModSystem(bot))