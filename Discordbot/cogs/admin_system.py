from discord.ext import commands
import discord

import bot_tools
import bot_db


class AdminRoleSystem(commands.Cog, name='Admin Roles'):
    """Allows for existing Roles on the server to be added to or removed from a internal list of Admin Roles. Members with Admin Roles will be able to use all of the commands the bot supports. Only the Super Admin specified in the config can add and remove roles from this list."""
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(
        name='admins', 
        aliases=['a'], 
        brief='Lists the Admin Roles.',
        help='Shows a list of all current admin roles on the server. The list can only be modified by the Super Admin specified in the config file.\nUsage: `!admins/!a`',
        usage='Usage: `!admins/!a`')
    async def list_admins(self, ctx):
        admins = [admins['role_name'] for admins in bot_db.server_get()['admin_roles']]
        await ctx.send(embed=bot_tools.create_list_embed(ctx=ctx, _title='Admin roles', _description='Here is a list of all the admin roles for GrammarBot on this server.', _field_name='Admin roles', items=admins))


    @bot_tools.is_server_owner()
    @commands.guild_only()
    @commands.command(
        name='admin_add', 
        aliases=['a_add'], 
        brief='Add a role to the Admin Role list.',
        help='Use this command to add a role form this server to the internal list of Admin Roles. Members with Admin Roles can user all commands. **Only the server owner can add roles to the list.**',
        usage='Usage: `!admin_add/!a_add RoleName`')
    async def add_admin(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return
        [_, role_name] = command
        admin_roles = bot_db.server_get(project={'_id': 0, 'admin_roles': {'$elementMatch': {'admin_roles.name': role_name}}})
        if len(admin_roles) != 0:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is already an admin.'))
            return
        else:
            if role_name in [roles.name for roles in ctx.guild.roles]:
                bot_db.server_update(
                    'push', 
                    list_name='admin_roles',
                    new_value={'id': discord.utils.get(ctx.guild.roles, name=role_name).id, 'role_name': role_name}
                    )
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Admin roles', _description=f'Successfully added the role `{role_name}` to the list of admins.'))
            else:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` does not exist on this server.'))


    @bot_tools.is_server_owner()   
    @commands.guild_only()
    @commands.command(
        name='admin_remove', 
        aliases=['a_remove'], 
        brief='Remove a role from the Admin Role list.',
        help='Use this command to remove a role form this server from the internal list of Admin Roles. Members with Admin Roles can user all commands. **Only the server owner can remove roles from the list.**',
        usage='Usage: `!admin_remove/!a_remove RoleName`')
    async def remove_admin(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return
        [_, role_name] = command
        admin_roles = bot_db.server_get(project={'_id': 0, 'admin_roles': {'$elementMatch': {'admin_roles.name': role_name}}})
        if len(admin_roles) == 0:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is not on the list of admins.'))
            return
        else:
            bot_db.server_update(
                    'pull', 
                    list_name='admin_roles',
                    pull_dict={'role_name': role_name}
                    )
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Admin roles', _description=f'Successfully removed the role `{role_name}` from the list of admins.'))


def setup(bot):
    bot.add_cog(AdminRoleSystem(bot))