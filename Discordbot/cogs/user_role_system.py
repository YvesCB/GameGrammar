from discord.ext import commands
import discord
import asyncio

import bot_tools
import bot_db


class UserRoleSystem(commands.Cog, name='User Role System'):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    @commands.guild_only()
    async def on_reaction_add(self, reaction, user):
        role_emotes = bot_db.get_role_emotes()[0]['role_emote']
        data = bot_db.get_role_data()
        if data is None or role_emotes is None:
            return
            
        if reaction.message.id != data[0]['message_id']:
            return

        for emote, role in role_emotes.items():
            if reaction.emoji.id == int(emote.split(':')[2]):
                role = discord.utils.get(reaction.message.guild.roles, id=role)
                await user.add_roles(role, reason=None, atomic=True)
                print(f'Added role {role.name} to member {user.name}')

    
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_reaction_remove(self, reaction, user):
        role_emotes = bot_db.get_role_emotes()[0]['role_emote']
        data = bot_db.get_role_data()
        if data is None or role_emotes is None:
            return
            
        if reaction.message.id != data[0]['message_id']:
            return

        for emote, role in role_emotes.items():
            if reaction.emoji.id == int(emote.split(':')[2]):
                role = discord.utils.get(reaction.message.guild.roles, id=role)
                await user.remove_roles(role, reason=None, atomic=True)
                print(f'Remove role {role.name} to member {user.name}')
            

    @commands.command(name='purge_role', aliases=['pr'], help='Removes the specified role from every user on the server.\nUsage: `!purge_role/!pr <role_name(s)>`')
    @bot_tools.is_admin()
    @commands.guild_only()
    async def purge_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To purge roles from all users use `!purge_role <role_name(s)>`.'))
            return

        [_, roles] = command
        roles = roles.split()
        invalid_roles = []
        valid_roles = []
        for role in roles:
            role_obj = discord.utils.get(ctx.guild.roles, name=role)
            if role_obj is None:
                invalid_roles.append(role)
            else:
                valid_roles.append(role_obj)

        invalid_roles_string = ' '.join(invalid_roles)
        if len(invalid_roles) > 0:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{invalid_roles_string} is/are not valid roles on this server.'))
            return

        for user in ctx.guild.members:
            for role in valid_roles:
                if role in user.roles:
                    await user.remove_roles(role, reason=None, atomic=True)

        roles_string = ' '.join(roles)
        await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Purge Role', _description=f'Successfully purged the role(s) {roles_string}.'))


    @commands.command(name='set_role_message', aliases=['srm'], help='Sets the channel and message for the reaction. If it is set already, it will overwrite after confirming with the user.\n Usage: `!set_role_message/!srm <channel_id> <message_id> `')
    @bot_tools.is_admin()
    @commands.guild_only()
    async def set_role_message(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To set or change the role message id and channel id, please use `!set_role_message/!srm <message_id> <channel_id>`.'))
            return
        
        [_, ch_id, msg_id] = command
        try:
            ch_id = int(ch_id)
            msg_id = int(msg_id)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='IDs must be numbers!'))
            return
        data = bot_db.get_role_data()
        if data is None: 
            channel = discord.utils.get(ctx.guild.text_channels, id=ch_id)
            if channel is None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid channel id!'))
                return
            message = discord.utils.get(await channel.history().flatten(), id=msg_id)
            if message is None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid message id!'))
                return
            bot_db.fill_role_data(msg_id, ch_id)
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Reaction Role Message', _description=f'Successfully set reaction role channel to <#{channel.id}> and message to {message.jump_url} !'))
        else:
            channel = discord.utils.get(ctx.guild.text_channels, id=data[0]['channel_id'])
            message = discord.utils.get(await channel.history().flatten(), id=data[0]['message_id'])
            
            response = await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Reaction Role Message', _description=f'The current reaction role channel is <#{channel.id}> and the message {message.jump_url} ! Are you sure you want to change it?'))
            check_mark = '\U00002714'
            cross_mark = '\U0000274C'
            await response.add_reaction(check_mark)
            await response.add_reaction(cross_mark)

            def check(reaction, user):
                return user == ctx.message.author and user != self.bot.user and (str(reaction.emoji) == check_mark or cross_mark)

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send('Timed out! Try again!')
                return
            else:
                if str(reaction.emoji) == check_mark:
                    channel = discord.utils.get(ctx.guild.text_channels, id=ch_id)
                    if channel is None:
                        await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid channel id!'))
                        return
                    message = discord.utils.get(await channel.history().flatten(), id=msg_id)
                    if message is None:
                        await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid message id!'))
                        return
                    bot_db.change_role_data(msg_id, ch_id)
                    await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Reaction Role Message', _description=f'Successfully set reaction role channel to <#{channel.id}> and message to {message.jump_url} !'))
                elif str(reaction.emoji) == cross_mark:
                    await ctx.send('Cancelled!')
                    return
        
        message_words = message.content.split()

        filtered_message = [entry.replace('<', '').replace('>','').replace('@&', '') for entry in message_words if '<' in entry]

        emote_dict = {}

        for emote, role in bot_tools.grouped(filtered_message, 2):
            emote_dict.update({emote: int(role)})

        bot_db.update_role_data(emote_dict)

        for emote, role in emote_dict.items():
            emote_id = emote.split(':')[2]
            emoji = self.bot.get_emoji(int(emote_id))
            await message.add_reaction(emoji)


    """
    Legacy role system
    """
    # @commands.command(name='user_role', aliases=['ur'], help='Assigns a role to a user or lists available roles if no role is specified.\nUsage: `!user_role/!ur <role_name>`')
    # @commands.guild_only()
    # async def get_remove_role(self, ctx):
    #     try:
    #         command = bot_tools.parse_command(ctx.message.content, 1)
    #     except ValueError:
    #         try:
    #             command = bot_tools.parse_command(ctx.message.content, 0)
    #         except ValueError:
    #             await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To remove/add a role, use `!user_role/!ur <name>`. Not specifying a name will list all available roles.'))
    #             return
    #     if len(command) == 1:
    #         user_roles = [user_roles['name'] for user_roles in bot_db.get_all_user_roles()]
    #         await ctx.send(embed=bot_tools.create_list_embed(ctx=ctx, _title='Self assignable roles', _description='Here is a list of all the roles you can assign to yourself.', _field_name='User roles', items=user_roles))
    #     else:
    #         [_, role_name] = command
    #         role_name = role_name.replace('<', '').replace('>', '')
    #         user_roles = [user_roles['name'] for user_roles in bot_db.get_all_user_roles()]
    #         for names in user_roles:
    #             if role_name.lower() == names.lower():
    #                 role_name = names
    #         if not bot_db.exists_user_role(role_name):
    #             await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is not on the list of self-assignable roles.'))
    #             return
    #         else:
    #             if role_name in [author_roles.name for author_roles in ctx.author.roles]:
    #                 role = next(role for role in ctx.author.roles if role.name == role_name)
    #                 await ctx.author.remove_roles(role, reason=None, atomic=True)
    #                 await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='User Roles', _description=f'Removed role `{role_name}` from your roles {ctx.author.name}!'))
    #             else:
    #                 role = next(role for role in ctx.guild.roles if role.name == role_name)
    #                 await ctx.author.add_roles(role, reason=None, atomic=True)
    #                 await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='User Roles', _description=f'Added role `{role_name}` to your roles {ctx.author.name}!'))


    # @commands.command(name='user_role_add', aliases=['ur_add'], help='Adds a role to the list of self-assignable roles.\nCan only be used by admins!\nUsage: `!user_role_add/!ur_add <role_name>`')
    # @bot_tools.is_admin()
    # @commands.guild_only()
    # async def add_user_role(self, ctx):
    #     try:
    #         command = bot_tools.parse_command(ctx.message.content, 1)
    #     except ValueError:
    #         await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To add a role to the self-assignable roles, use `!user_role_add/!ur_add <role_name>.'))
    #         return
    #     [_, role_name] = command
    #     if bot_db.exists_user_role(role_name):
    #         await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is already self-assignable.'))
    #         return
    #     else:
    #         if role_name in [roles.name for roles in ctx.guild.roles]:
    #             bot_db.add_user_role(role_name)
    #             await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='User Roles', _description=f'Successfully added the role `{role_name}` to the list of self-assignable roles.'))
    #         else:
    #             await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'Error: the role `{role_name}` does not exits on this server!'))


    # @commands.command(name='user_role_remove', aliases=['ur_remove'], help='Removes a role from the list of self-assignable roles.\nCan only be used by admins!\nUsage: `!user_role_remove/!ur_remove <role_name>`')
    # @bot_tools.is_admin()
    # @commands.guild_only()
    # async def remove_user_role(self, ctx):
    #     try:
    #         command = bot_tools.parse_command(ctx.message.content, 1)
    #     except ValueError:
    #         await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To remove a role from the self-assignable roles, use `!user_role_remove/!ur_remove <role_name>.'))
    #         return
    #     [_, role_name] = command
    #     if not bot_db.exists_user_role(role_name):
    #         await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is not self-assignable.'))
    #         return
    #     else:
    #         bot_db.remove_user_role(role_name)
    #         await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='User Roles', _description=f'Successfully removed the role `{role_name}` from the list of self-assignable roles.'))


def setup(bot):
    bot.add_cog(UserRoleSystem(bot))