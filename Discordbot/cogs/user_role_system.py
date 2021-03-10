from discord.ext import commands
import discord
import asyncio

import bot_tools
import bot_db


class UserRoleSystem(commands.Cog, name='User Roles'):
    """The bot will assign you the roles you want! You simply have to go to the <#759415738820853790> channel react with the emotes corresponding to the roles you would like to have. Removing the reaction will also remove the role from you. Setup for the roles and the role channel is also done via commands. That part is left to administrators though."""
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_reaction_add(self, payload):
        server_data = bot_db.server_get()
        if 'user_role_data' not in list(server_data.keys()):
            return
            
        if payload.message_id != server_data['user_role_data']['message_id']:
            return

        for emote, role in server_data['user_role_data']['emote_role'].items():
            if payload.emoji.id == int(emote.split(':')[2]):
                guild = self.bot.get_guild(payload.guild_id)
                role = discord.utils.get(guild.roles, id=role)
                user = discord.utils.get(guild.members, id=payload.user_id)
                await user.add_roles(role, reason='Reaction role', atomic=True)
                print(f'Added role {role.name} to member {user.name}')

    
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_reaction_remove(self, payload):
        server_data = bot_db.server_get()
        if 'user_role_data' not in list(server_data.keys()):
            return
            
        if payload.message_id != server_data['user_role_data']['message_id']:
            return

        for emote, role_id in server_data['user_role_data']['emote_role'].items():
            if payload.emoji.id == int(emote.split(':')[2]):
                guild = self.bot.get_guild(payload.guild_id)
                role = discord.utils.get(guild.roles, id=role_id)
                user = discord.utils.get(guild.members, id=payload.user_id)
                await user.remove_roles(role, reason=None, atomic=True)
                print(f'Removed role {role.name} from member {user.name}')
            

    @bot_tools.is_admin()
    @commands.guild_only()
    @commands.command(
        name='purge_role', 
        aliases=['pr'], 
        brief='Remove the specified role(s) from every user on the server.',
        help='This command can be used to purge a role from the server. That means that the specified role or multiple roles will be removed from every single member on the server that has said role. **This command can only be used by users with an admin role.**',
        usage='Usage: `!purge_role\!pr RoleName(s)`')
    async def purge_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return

        [_, roles] = command
        roles = roles.split()
        role_ids = [int(role.replace('<@&', '').replace('>', '')) for role in roles]
        invalid_roles = []
        valid_roles = []
        for role in role_ids:
            role_obj = discord.utils.get(ctx.guild.roles, id=role)
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


    @bot_tools.is_admin()
    @commands.guild_only()
    @commands.command(
        name='set_role_message', 
        aliases=['srm'], 
        brief='Set the message that the bot will use for users to select their roles.',
        help='This command can be used to set or change the message used for the self-assignable roles. The channel and the message ID need to be specified, the bot will then automatically read the roles and emotes mentioned in the message and add the emotes as reactions. From then on, whenever a user reacts with one of the emotes, the bot will assign the corresponding role to the user and remove the role when the user removes the reaction. **This command can only be used by users with an admin role.**',
        usage='Usage: `!set_role_message\!srm ChannelID MessageID`')
    async def set_role_message(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return
        
        [_, ch_id, msg_id] = command
        try:
            ch_id = int(ch_id)
            msg_id = int(msg_id)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='IDs must be numbers!'))
            return
        data = bot_db.server_get()
        if 'user_role_data' not in list(data.keys()): 
            channel = discord.utils.get(ctx.guild.text_channels, id=ch_id)
            if channel is None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid channel id!'))
                return
            message = discord.utils.get(await channel.history().flatten(), id=msg_id)
            if message is None:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='Not a valid message id!'))
                return
            bot_db.server_update('update', new_value={'user_role_data.message_id': msg_id})
            bot_db.server_update('update', new_value={'user_role_data.channel_id': ch_id})
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Reaction Role Message', _description=f'Successfully set reaction role channel to <#{channel.id}> and message to {message.jump_url} !'))
        else:
            channel = discord.utils.get(ctx.guild.text_channels, id=bot_db.server_get()['user_role_data']['channel_id'])
            message = discord.utils.get(await channel.history().flatten(), id=bot_db.server_get()['user_role_data']['message_id'])
            
            try:
                response = await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Reaction Role Message', _description=f'The current reaction role channel is <#{channel.id}> and the message {message.jump_url} ! Are you sure you want to change it?'))
            except:
                response = await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Reaction Role Message', _description=f'The current reaction role channel is <#{channel.id}> but the message cannot be found. It was most likely deleted. Do you want to overwrite?'))
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
                    bot_db.server_update('update', new_value={'user_role_data.message_id': msg_id})
                    bot_db.server_update('update', new_value={'user_role_data.channel_id': ch_id})
                    await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Reaction Role Message', _description=f'Successfully set reaction role channel to <#{channel.id}> and message to {message.jump_url} !'))
                elif str(reaction.emoji) == cross_mark:
                    await ctx.send('Cancelled!')
                    return
        
        message_words = message.content.split()

        filtered_message = [entry.replace('<', '').replace('>','').replace('@&', '') for entry in message_words if '<' in entry]

        emote_dict = {}

        for emote, role in bot_tools.grouped(filtered_message, 2):
            emote_dict.update({emote: int(role)})

        bot_db.server_update('update', new_value={'user_role_data.emote_role': emote_dict})

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