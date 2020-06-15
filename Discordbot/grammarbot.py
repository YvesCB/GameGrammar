import discord
from discord.ext import commands
import random


import config
import bot_db
import bot_tools


bot = commands.Bot(command_prefix=config.command_prefix)
bot.remove_command('help')


def is_admin():
    async def predicate(ctx):
        return bot_tools.is_admin(ctx.author) or ctx.author.id == config.default_admin_id  
    return commands.check(predicate)


async def admin_check_fail(ctx):
    await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='You must be an admin to use this command!'))


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=config.discord_guild)
    print(
        f'{bot.user.name} has connected to Discord guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.event
async def on_member_join(member):
    guild = discord.utils.get(bot.guilds, name=config.discord_guild)
    channel = discord.utils.get(guild.channels, id=410321201395924992)
    msg = random.choice(bot_tools.welcome_messages).replace('<user>', f'<@{member.id}>')
    await channel.send(msg)


@bot.command(name='tag', aliases=['t'], help='Alliases: `!t`\nCall pre-written messages called tags. Show list of tags if no tag is specified.\nUsage: `!tag/!t <name>`')
async def get_tag(ctx):
    try: 
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        try:
            command = bot_tools.parse_command(ctx.message.content, 0)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='All tags are one word only.'))
            return
    if len(command) == 1:
        tags = [t['name'] for t in bot_db.get_all_tags()]
        await ctx.send(embed=bot_tools.create_list_embed(_title='Tags', _description='Here is a list of all the tags you can use.', _field_name='Tags', items=tags))
    else:
        [_, tag_name] = command
        tag = bot_db.get_tag(tag_name)
        if not bot_db.exists_tag(tag_name):
            await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'The Tag `{tag_name}` does not exists.'))
        else:
            await ctx.send(tag['response'])


@bot.command(name='tag_add', aliases=['t_add'], help='Alliases: `!t_add`\nAdd a new tag to the list of tags.\nCan only be used by admins!\nUsage: `!tag_add/!t_add <name> <message>`')
@is_admin()
async def add_tag(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 2)
    except ValueError:
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='To create tags, use `!tag_add/!t_add <name> <message>`.'))
        return
    [_, tag_name, tag_content] = command
    if bot_db.exists_tag(tag_name):
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'The tag `{tag_name}` already exists.'))
        return
    else:
        bot_db.add_tag(tag_name, tag_content)
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Tag', _description=f'Successfully added tag `{tag_name}`!'))


@add_tag.error
async def add_tag_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        admin_check_fail(ctx)


@bot.command(name='tag_remove', aliases=['t_remove'], help='Alliases: `!t_remove`\nRemove an existing tag.\nCan only be used by admins!\nUsage: `!tag_remove/!t_remove <name>`')
@is_admin()
async def remove_tag(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='To remove a tag, use `!t_remove <name>`.'))
        return
    [_, tag_name] = command
    if not bot_db.exists_tag(tag_name):
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'`{tag_name}` does not exists!'))
        return
    else:
        bot_db.remove_tag(tag_name)
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'Successfully removed tag `{tag_name}`'))


@remove_tag.error
async def remove_tag_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        admin_check_fail(ctx)


@bot.command(name='admins', aliases=['a'], help='Alliases: `!a`\nShows a list of all current admin roles.\nUsage: `!admins/!a`')
@commands.guild_only()
async def list_admins(ctx):
    admins = [admins['name'] for admins in bot_db.get_all_admin_roles()]
    await ctx.send(embed=bot_tools.create_list_embed(_title='Admin roles', _description='Here is a list of all the admin roles for GrammarBot on this server.', _field_name='Admin roles', items=admins))


@bot.command(name='admin_add', aliases=['a_add'], help='Alliases: `!a_add`\nAdds a role to the list of admins.\nCan only be used by admins!\nUsage: `!admin_add/!a_add <role_name>`')
@is_admin()
@commands.guild_only()
async def add_admin(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='To add a role to the list of admins, use `!admin_add/!a_add <role_name>`.'))
        return
    [_, role_name] = command
    if bot_db.exists_admin_role(role_name):
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'The role `{role_name}` is already an admin.'))
        return
    else:
        if role_name in [roles.name for roles in ctx.guild.roles]:
            bot_db.add_admin_role(role_name)
            await ctx.send(embed=bot_tools.create_simple_embed(_title='Admin roles', _description=f'Successfully added the role `{role_name}` to the list of admins.'))
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'The role `{role_name}` does not exist on this server.'))


@add_admin.error
async def add_admin_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        admin_check_fail(ctx)


@bot.command(name='admin_remove', aliases=['a_remove'], help='Alliase: `!a_remove`\nRemoves a role from the list of admins.\nCan only be used by admins!\nUsage: `!admin_remove/!a_remove <role_name>`')
@is_admin()
@commands.guild_only()
async def remove_admin(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='To remove a role from the list of admins, use `!admin_remove/!a_remove <role_name>`.'))
        return
    [_, role_name] = command
    if not bot_db.exists_admin_role(role_name):
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'The role `{role_name}` is not on the list of admins.'))
        return
    else:
        bot_db.remove_admin_role(role_name)
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Admin roles', _description=f'Successfully removed the role `{role_name} from the list of admins.`'))


@remove_admin.error
async def remove_admin_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        admin_check_fail(ctx)


@bot.command(name='user_role_add', aliases=['ur_add'], help='Alliases: `!ur_add`\nAdds a role to the list of self-assignable roles.\nCan only be used by admins!\nUsage: `!user_role_add/!ur_add <role_name>`')
@is_admin()
@commands.guild_only()
async def add_user_role(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='To add a role to the self-assignable roles, use `!user_role_add/!ur_add <role_name>.'))
        return
    [_, role_name] = command
    if bot_db.exists_user_role(role_name):
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'The role `{role_name}` is already self-assignable.'))
        return
    else:
        if role_name in [roles.name for roles in ctx.guild.roles]:
            bot_db.add_user_role(role_name)
            await ctx.send(embed=bot_tools.create_simple_embed(_title='User Roles', _description=f'Successfully added the role `{role_name}` to the list of self-assignable roles.'))
        else:
            await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'Error: the role `{role_name}` does not exits on this server!'))


@add_user_role.error
async def add_user_role_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        admin_check_fail(ctx)


@bot.command(name='user_role_remove', aliases=['ur_remove'], help='Alliases: `!ur_remove`\nRemoves a role from the list of self-assignable roles.\nCan only be used by admins!\nUsage: `!user_role_remove/!ur_remove <role_name>`')
@is_admin()
@commands.guild_only()
async def remove_user_role(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='To remove a role from the self-assignable roles, use `!user_role_remove/!ur_remove <role_name>.'))
        return
    [_, role_name] = command
    if not bot_db.exists_user_role(role_name):
        await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'The role `{role_name}` is not self-assignable.'))
        return
    else:
        bot_db.remove_user_role(role_name)
        await ctx.send(embed=bot_tools.create_simple_embed(_title='User Roles', _description=f'Successfully removed the role `{role_name}` from the list of self-assignable roles.'))


@remove_user_role.error
async def remove_user_role_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        admin_check_fail(ctx)


@bot.command(name='user_role', aliases=['ur'], help='Alliases: `!ur`\nAssigns a role to a user or lists available roles if no role is specified.\nUsage: `!user_role/!ur <role_name>`')
@commands.guild_only()
async def get_remove_role(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        try:
            command = bot_tools.parse_command(ctx.message.content, 0)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description='To remove/add a role, use `!user_role/!ur <name>`. Not specifying a name will list all available roles.'))
            return
    if len(command) == 1:
        user_roles = [user_roles['name'] for user_roles in bot_db.get_all_user_roles()]
        await ctx.send(embed=bot_tools.create_list_embed(_title='Self assignable roles', _description='Here is a list of all the roles you can assign to yourself.', _field_name='User roles', items=user_roles))
    else:
        [_, role_name] = command
        if not bot_db.exists_user_role(role_name):
            await ctx.send(embed=bot_tools.create_simple_embed(_title='Error', _description=f'The role `{role_name}` is not on the list of self-assignalbe roles.'))
            return
        else:
            if role_name in [author_roles.name for author_roles in ctx.author.roles]:
                role = next(role for role in ctx.author.roles if role.name == role_name)
                await ctx.author.remove_roles(role, reason=None, atomic=True)
                await ctx.send(embed=bot_tools.create_simple_embed(_title='User Roles', _description=f'Removed role `{role_name}` from your roles {ctx.author.name}!'))
            else:
                role = next(role for role in ctx.guild.roles if role.name == role_name)
                await ctx.author.add_roles(role, reason=None, atomic=True)
                await ctx.send(embed=bot_tools.create_simple_embed(_title='User Roles', _description=f'Added role `{role_name}` to your roles {ctx.author.name}!'))


@bot.command(name='help', aliases=['?', 'h'], help='Alliases: `!h/!?`\nDisplays the help message.\nUsage: `!help/!h/!?`')
async def help_message(ctx):
    await ctx.send(embed=bot_tools.create_help_embed(bot.commands))


bot.run(config.discord_token)