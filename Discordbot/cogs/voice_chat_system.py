import discord
from discord.ext import commands

import bot_tools
import bot_db
import config

class VoiceSystem(commands.Cog):
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
            entry = bot_db.get_voice_text(after.channel.id)
            role = member.guild.get_role(entry['r_id'])
            if role is not None:
                await member.add_roles(role, reason=None, atomic=True)
                print(f'{member.name} entered {after.channel.name} and got role {role.name}')
            else:
                return

        # case 2
        elif before.channel is not None and after.channel is not None and not before.channel == after.channel:
            entry_before = bot_db.get_voice_text(before.channel.id)
            entry_after = bot_db.get_voice_text(after.channel.id)
            role_before = member.guild.get_role(entry_before['r_id'])
            role_after = member.guild.get_role(entry_after['r_id'])
            if role_after is not None and role_before is not None:
                await member.remove_roles(role_before, reason=None, atomic=True)
                await member.add_roles(role_after, reason=None, atomic=True)
                print(f'{member.name} left {before.channel.name} and entered {after.channel.name} and changed roles from {role_before.name} to {role_after.name}')
            else:
                return

        # case 3
        elif before.channel is not None and after.channel is None:
            entry = bot_db.get_voice_text(before.channel.id)
            role = member.guild.get_role(entry['r_id'])
            if role is not None:
                await member.remove_roles(role, reason=None, atomic=True)
                print(f'{member.name} left {before.channel.name} and lost role {role.name}')
            else:
                return


    # Define a voice channel and text channel. Bot will set up a role that has permission to see said text channel and save that configuration.
    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(name='vc_role_add', aliases=['vr_add'], help='Add a role to a voice channel and corresponding text channel.\nUsage: `!vc_role_add/!vr_add <voice_ch_id> <text_ch_id>`')
    async def add_vc_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To add a new voice role please, use `!vc_role_add/!vc_add <voice_ch_id> <text_ch_id>`.'))
            return
        [_, vc_id, tc_id] = command
        vc_id = int(vc_id)
        tc_id = int(tc_id)
        vc = ctx.guild.get_channel(vc_id)
        tc = ctx.guild.get_channel(tc_id)
        if bot_db.exists_voice_text(vc_id):
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
                bot_db.add_voice_text(vc_id, tc_id, role.id)
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Voice role', _description=f'Successfully created the role `{role.name}` for users in `{vc.name}` to see `{tc.name}`.'))


    @commands.guild_only()
    @bot_tools.is_admin()
    @commands.command(name='vc_role_remove', aliases=['vr_remove'], help='Remove a role that belongs to a voic/text pair (for example if the name of the voice/text channel changes or the voice/text channel is deleted).\nUsage: `!vc_role_add/!vr_add <voice_ch_id> <text_ch_id>`')
    async def remove_vc_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To remove a voice/text role please, use `!vc_role_remove/!vr_remove <voice_ch_id>`.'))
            return
        [_, vc_id] = command
        vc_id = int(vc_id)
        vc = ctx.guild.get_channel(vc_id)

        if bot_db.exists_voice_text(vc_id):
            entry = bot_db.get_voice_text(vc_id)
            role = ctx.guild.get_role(entry['r_id'])
            role_name = role.name
            tc = ctx.guild.get_channel(entry['tc_id'])
            await role.delete()
            bot_db.remove_voic_text(vc_id)
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Voice role', _description=f'Successfully removed the voice role `{role_name}` from the voice/text pair `{vc.name}`/`{tc.name}`.'))
            return
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The specified voice chat id `{vc_id}` does not correspond to any role currently associated with a voice/text channel pair.'))



def setup(bot):
    bot.add_cog(VoiceSystem(bot))