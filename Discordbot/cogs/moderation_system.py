import discord
import time
from discord.ext import commands

import bot_tools
import bot_db
import config


class ModSystem(commands.Cog, name='Modaration'):
    """Contains command and functionality concerning server moderation. This includes (for now) checking people's rap sheet, which is a quick overview of the most recent infractions, and warning people. Soon muting them for a given amount of time and banning them will be available as well."""
    def __init__(self, bot):
        self.bot = bot
    
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

        warning = {'message': warn_message, 'time': time.strftime("%a, %d %b %Y, %H:%M:%S GMT", time.gmtime()), 'channel': ctx.message.channel.id}
        bot_db.add_warning(user_id, warning)


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
        
        if discord.utils.get(ctx.guild.members, id=user_id) == None:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='This user is not a member of this discord server!'))
            return

        warns = bot_db.get_user_warnings(user_id)
        if warns == None: 
            warns = []
        await ctx.send(embed=self.create_sheet(ctx, warns, discord.utils.get(ctx.guild.members, id=user_id)))


def setup(bot):
    bot.add_cog(ModSystem(bot))