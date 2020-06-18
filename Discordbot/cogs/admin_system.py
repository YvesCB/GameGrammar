from discord.ext import commands
import discord

import bot_tools
import bot_db


class AdminRoleSystem(commands.Cog, name='Admin role system'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='admins', aliases=['a'], help='Shows a list of all current admin roles.\nUsage: `!admins/!a`')
    @commands.guild_only()
    async def list_admins(self, ctx):
        admins = [admins['name'] for admins in bot_db.get_all_admin_roles()]
        await ctx.send(embed=bot_tools.create_list_embed(ctx=ctx, _title='Admin roles', _description='Here is a list of all the admin roles for GrammarBot on this server.', _field_name='Admin roles', items=admins))


    @commands.command(name='admin_add', aliases=['a_add'], help='Adds a role to the list of admins.\nCan only be used by admins!\nUsage: `!admin_add/!a_add <role_name>`')
    @bot_tools.is_admin()
    @commands.guild_only()
    async def add_admin(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To add a role to the list of admins, use `!admin_add/!a_add <role_name>`.'))
            return
        [_, role_name] = command
        if bot_db.exists_admin_role(role_name):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is already an admin.'))
            return
        else:
            if role_name in [roles.name for roles in ctx.guild.roles]:
                bot_db.add_admin_role(role_name)
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Admin roles', _description=f'Successfully added the role `{role_name}` to the list of admins.'))
            else:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` does not exist on this server.'))


    @commands.command(name='admin_remove', aliases=['a_remove'], help='Removes a role from the list of admins.\nCan only be used by admins!\nUsage: `!admin_remove/!a_remove <role_name>`')
    @bot_tools.is_admin()
    @commands.guild_only()
    async def remove_admin(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To remove a role from the list of admins, use `!admin_remove/!a_remove <role_name>`.'))
            return
        [_, role_name] = command
        if not bot_db.exists_admin_role(role_name):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The role `{role_name}` is not on the list of admins.'))
            return
        else:
            bot_db.remove_admin_role(role_name)
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Admin roles', _description=f'Successfully removed the role `{role_name}` from the list of admins.'))


def setup(bot):
    bot.add_cog(AdminRoleSystem(bot))