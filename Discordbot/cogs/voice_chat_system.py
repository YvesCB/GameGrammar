import discord
from discord.ext import commands

import bot_tools
import bot_db
import config

class VoiceSystem(commands.Cog, name='Voice Roles'):
    """The bot will keep track of what voice channel you are in and assign you a corresponding role. That role will unlock a text channel that belongs to your current voice channel. This way, the conversations inside the text channels that pertain to discussions in voice chat stay somewhat private and additionally it reduces the amount of visible channels when you're not in voice chat. It also helps you to know which channel to use since there will only be one option. The set up for all of this also also done via commands that can be used by administrators."""
    def __init__(self, bot):
        self.bot = bot


    # Update user role depending on voice chat. 3 cases:
    # 1: Enter voice chat -> give role
    # 2: Change voice chat -> change role
    # 3: Leave voice chat -> remove role
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # case 1
        if before.channel is None and after.channel is not None:
            entry = bot_db.server_get(project={'_id': 0, 'voice_text_roles': {'$elemMatch': {'voice_channel_id': after.channel.id}}})
            # entering into afk or non role channel
            if len(entry) == 0:
                return
            else:
                role = member.guild.get_role(entry['role_id'])
                await member.add_roles(role, reason='Joined voice chat', atomic=True)
                print(f'{member.name} entered {after.channel.name} and got role {role.name}')

        # case 2
        elif before.channel is not None and after.channel is not None and not before.channel == after.channel:
            entry_before = bot_db.server_get(project={'_id': 0, 'voice_text_roles': {'$elemMatch': {'voice_channel_id': before.channel.id}}})
            entry_after = bot_db.server_get(project={'_id': 0, 'voice_text_roles': {'$elemMatch': {'voice_channel_id': after.channel.id}}})
            # coming back from afk or other non-listed role channel
            if len(entry_before) == 0 and len(entry_after) != 0:
                role_after = member.guild.get_role(entry_after['role_id'])
                await member.add_roles(role_after, reason='Joined voice chat', atomic=True)
                print(f'{member.name} left {before.channel.name} and entered {after.channel.name} and received {role_after.name}')

            # going into afk or other non role channel
            elif len(entry_before) != 0 and len(entry_after) == 0:
                role_before = member.guild.get_role(entry_before['role_id'])
                await member.remove_roles(role_before, reason=None, atomic=True)
                print(f'{member.name} left {before.channel.name} and entered {after.channel.name} and lost {role_before.name}')

            elif len(entry_before) == 0 and len(entry_after) == 0:
                return

            else:
                role_before = member.guild.get_role(entry_before['role_id'])
                role_after = member.guild.get_role(entry_after['role_id'])
                await member.remove_roles(role_before, reason='Left voice chat', atomic=True)
                await member.add_roles(role_after, reason='Joined voice chat', atomic=True)
                print(f'{member.name} left {before.channel.name} and entered {after.channel.name} and changed roles from {role_before.name} to {role_after.name}')

        # case 3
        elif before.channel is not None and after.channel is None:
            entry = bot_db.server_get(project={'_id': 0, 'voice_text_roles': {'$elemMatch': {'voice_channel_id': after.channel.id}}})
            # leaving afk or other non role channel
            if len(entry) == 0:
                return
            else:
                role = member.guild.get_role(entry['role_id'])
                await member.remove_roles(role, reason='Left voice chat', atomic=True)
                print(f'{member.name} left {before.channel.name} and lost role {role.name}')


    # Define a voice channel and text channel. Bot will set up a role that has permission to see said text channel and save that configuration.
    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='vc_role_add', 
        aliases=['vr_add'], 
        brief='Create a role that will link a voice chat to a text chat.',
        help='This command will allow you to create a role that links a voice chat to a text chat. You specify the voice and text channels. The bot will then create a role that has the right permissions pre-set. You don\'t need to set up anything. A soon as this command has been used, users that join the voice chat will receive the role and the role then enables them to see and use the text channel specified. **This command can only be used by users with an admin role.**',
        usage='Usage: `!vc_role_add\!vr_add VoiceChID TextChID`')
    async def add_vc_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return
        [_, vc_id, tc_id] = command
        vc_id = int(vc_id)
        tc_id = int(tc_id)
        vc = ctx.guild.get_channel(vc_id)
        tc = ctx.guild.get_channel(tc_id)
        if len(bot_db.server_get(project={'_id': 0, 'voice_text_roles': {'$elemMatch': {'voice_channel_id': vc_id}}})) != 0:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role for `{vc.name}` is already set up.'))
            return
        else:
            if vc is None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'A voice channel with the provided id `{vc_id}` does not exist in this server!'))
                return
            elif tc is None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'A text channel with the provided id `{tc_id}` does not exist in this server!'))
                return
            else:
                # create role, set up perms, add db entry
                role = await ctx.guild.create_role(name=f'In {vc.name}')
                await tc.set_permissions(role, read_messages=True)
                bot_db.server_update('push', list_name='voice_text_roles', new_value={'voice_channel_id': vc_id, 'text_channel_id': tc_id, 'role_id': role.id})
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Voice role', _description=f'Successfully created the role `{role.name}` for users in `{vc.name}` to see `{tc.name}`.'))


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(
        name='vc_role_remove', 
        aliases=['vr_remove'], 
        brief='Remove a role that belongs to a voice chat.',
        help='This command can be used to remove an existing role that has been linked to a voice chat and text chat. That role will no longer be applied to users in said voice chat. This command only works with roles that have previously been linked to a voice chat. **This command can only be used by a user with an admin role.**',
        usage='Usage: `!vc_role_remove VoiceChID`')
    async def remove_vc_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return
        [_, vc_id] = command
        vc_id = int(vc_id)
        vc = ctx.guild.get_channel(vc_id)

        entry = bot_db.server_get(project={'_id': 0, 'voice_text_roles': {'$elemMatch': {'voice_channel_id': vc_id}}})
        if len(entry) != 0:
            role = ctx.guild.get_role(entry['role_id'])
            role_name = role.name
            tc = ctx.guild.get_channel(entry['text_channel_id'])
            await role.delete()
            bot_db.server_update('pull', list_name='voice_text_roles', pull_dict={'voice_channel_id': vc_id})
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Voice role', _description=f'Successfully removed the voice role `{role_name}` from the voice/text pair `{vc.name}`/`{tc.name}`.'))
            return
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The specified voice chat id `{vc_id}` does not correspond to any role currently associated with a voice/text channel pair.'))



def setup(bot):
    bot.add_cog(VoiceSystem(bot))