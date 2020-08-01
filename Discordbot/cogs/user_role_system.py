from discord.ext import commands
import discord

import bot_tools
import bot_db


class UserRoleSystem(commands.Cog, name='User Role System'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='user_role', aliases=['ur'], help='Assigns a role to a user or lists available roles if no role is specified.\nUsage: `!user_role/!ur <role_name>`')
    @commands.guild_only()
    async def get_remove_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            try:
                command = bot_tools.parse_command(ctx.message.content, 0)
            except ValueError:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To remove/add a role, use `!user_role/!ur <name>`. Not specifying a name will list all available roles.'))
                return
        if len(command) == 1:
            user_roles = [user_roles['name'] for user_roles in bot_db.get_all_user_roles()]
            await ctx.send(embed=bot_tools.create_list_embed(ctx=ctx, _title='Self assignable roles', _description='Here is a list of all the roles you can assign to yourself.', _field_name='User roles', items=user_roles))
        else:
            [_, role_name] = command
            if not bot_db.exists_user_role(role_name):
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is not on the list of self-assignable roles.'))
                return
            else:
                if role_name in [author_roles.name for author_roles in ctx.author.roles]:
                    role = next(role for role in ctx.author.roles if role.name == role_name)
                    await ctx.author.remove_roles(role, reason=None, atomic=True)
                    await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='User Roles', _description=f'Removed role `{role_name}` from your roles {ctx.author.name}!'))
                else:
                    role = next(role for role in ctx.guild.roles if role.name == role_name)
                    await ctx.author.add_roles(role, reason=None, atomic=True)
                    await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='User Roles', _description=f'Added role `{role_name}` to your roles {ctx.author.name}!'))


    @commands.command(name='user_role_add', aliases=['ur_add'], help='Adds a role to the list of self-assignable roles.\nCan only be used by admins!\nUsage: `!user_role_add/!ur_add <role_name>`')
    @bot_tools.is_admin()
    @commands.guild_only()
    async def add_user_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To add a role to the self-assignable roles, use `!user_role_add/!ur_add <role_name>.'))
            return
        [_, role_name] = command
        if bot_db.exists_user_role(role_name):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is already self-assignable.'))
            return
        else:
            if role_name in [roles.name for roles in ctx.guild.roles]:
                bot_db.add_user_role(role_name)
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='User Roles', _description=f'Successfully added the role `{role_name}` to the list of self-assignable roles.'))
            else:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'Error: the role `{role_name}` does not exits on this server!'))


    @commands.command(name='user_role_remove', aliases=['ur_remove'], help='Removes a role from the list of self-assignable roles.\nCan only be used by admins!\nUsage: `!user_role_remove/!ur_remove <role_name>`')
    @bot_tools.is_admin()
    @commands.guild_only()
    async def remove_user_role(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To remove a role from the self-assignable roles, use `!user_role_remove/!ur_remove <role_name>.'))
            return
        [_, role_name] = command
        if not bot_db.exists_user_role(role_name):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is not self-assignable.'))
            return
        else:
            bot_db.remove_user_role(role_name)
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='User Roles', _description=f'Successfully removed the role `{role_name}` from the list of self-assignable roles.'))


def setup(bot):
    bot.add_cog(UserRoleSystem(bot))