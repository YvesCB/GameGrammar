import discord
from discord.ext import commands
import random


import config
import bot_db
import bot_tools


bot = commands.Bot(command_prefix=config.command_prefix)


def is_admin():
    async def predicate(ctx):
        if bot_tools.is_admin(ctx.author) or ctx.author.id == config.default_admin_id:
            return True
        else:
            await ctx.send('**You must be an admin to use this command!**')
            return False
    return commands.check(predicate)


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=config.discord_guild)
    print(
        f'{bot.user.name} has connected to Discord guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.command(name='tags', help='This command will list all available tags.')
async def list_tags(ctx):
    tags = [t['name'] for t in bot_db.get_all_tags()]
    await ctx.send('The available tags are: ```\n{}\n```'.format('\n'.join(tags)))


@bot.command(name='t', help='Call pre-written messages called tags.')
async def get_tag(ctx):
    try: 
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send('Error: Tags are all one word.')
        return
    [_, tag_name] = command
    tag = bot_db.get_tag(tag_name)
    if not bot_db.exists_tag(tag_name):
        await ctx.send(f'Error: The tag `{tag_name}` does not exist.')
    else:
        await ctx.send(tag['response'])


@bot.command(name='t_add', help='Add a new tag to the list of tags. Usage: !t_add <name> <message>')
@is_admin()
async def add_tag(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 2)
    except ValueError:
        await ctx.send('Error: To create tags, use !t_add followed by the name followed by the messsage.')
        return
    [_, tag_name, tag_content] = command
    if bot_db.exists_tag(tag_name):
        await ctx.send(f'Error: The tag `{tag_name}` already exists.')
        return
    else:
        bot_db.add_tag(tag_name, tag_content)
        await ctx.send(f'Successfully added tag `{tag_name}`!')


@bot.command(name='t_remove', help='Remove an existing tag. Usage: !t_remove <name>')
@is_admin()
async def remove_tag(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send('Error: To remove a tag, use !t_remove followed by just the name of tag.')
        return
    [_, tag_name] = command
    if not bot_db.exists_tag(tag_name):
        await ctx.send(f'Error: `{tag_name}` does not exists!')
        return
    else:
        bot_db.remove_tag(tag_name)
        await ctx.send(f'Sucessfully removed tag `{tag_name}`.')


@bot.command(name='admins', help='Shows a list of all current admin roles.')
@commands.guild_only()
async def list_admins(ctx):
    admins = [admins['name'] for admins in bot_db.get_all_admin_roles()]
    await ctx.send('The admin roles are: ```\n{}\n```'.format('\n'.join(admins)))


@bot.command(name='admin_add', help='Adds a role to the list of admins. **Can only be used by admins!**')
@is_admin()
@commands.guild_only()
async def add_admin(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send('Error: To add a role to admins, use !admin_add followed by the role name.')
        return
    [_, role_name] = command
    if bot_db.exists_admin_role(role_name):
        await ctx.send(f'Error: The role `{role_name}` is alreayd an admin.`')
        return
    else:
        if role_name in [roles.name for roles in ctx.guild.roles]:
            bot_db.add_admin_role(role_name)
            await ctx.send(f'Successfully added the role `{role_name}` to the list of admins.')
        else:
            await ctx.send(f'Error: The role `{role_name}` does not exists on this server!')


@bot.command(name='admin_remove', help='Removes a role from the list of admins. **Can only be used by admins!**')
@is_admin()
@commands.guild_only()
async def remove_admin(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send('Error: To remove a role from the list of admins, use !admin_remove followed by the role name.')
        return
    [_, role_name] = command
    if not bot_db.exists_admin_role(role_name):
        await ctx.send(f'Error: The role `{role_name}` is not on the list of admins!')
        return
    else:
        bot_db.remove_admin_role(role_name)
        await ctx.send(f'Sucessfully removed the role `{role_name}` fromt the list of amdins!')


@bot.command(name='user_role_add', help='Adds a role to the list of self-assignable roles. **Can only be used by admins!**')
@is_admin()
@commands.guild_only()
async def add_user_role(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send('Error: To add a role to the self-assignable roels, use !user_role_add followed by the role name.')
        return
    [_, role_name] = command
    if bot_db.exists_user_role(role_name):
        await ctx.send(f'Error: The role `{role_name}` is already self-assignable.')
        return
    else:
        if role_name in [roles.name for roles in ctx.guild.roles]:
            bot_db.add_user_role(role_name)
            await ctx.send(f'Successfully added the role `{role_name}` to the list of self-assignable roles.')
        else:
            await ctx.send(f'Error: the role `{role_name}` does not exits on this server!')


@bot.command(name='user_role_remove', help='Removes a role from the list of self-assignable roles.')
@is_admin()
@commands.guild_only()
async def remove_user_role(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        await ctx.send('Error: To remove a role from the list of self-assignable roles, use !user_role_remove followed by the role name.')
        return
    [_, role_name] = command
    if not bot_db.exists_user_role(role_name):
        await ctx.send(f'Error: The role `{role_name}` is not on the list of self-assignalbe roles!')
        return
    else:
        bot_db.remove_user_role(role_name)
        await ctx.send(f'Sucessfully removed the role `{role_name}` fromt the list of self-assignable roles!')


@bot.command(name='user_role', help='Assigns a role to a user or lists available roles.')
@commands.guild_only()
async def get_remove_role(ctx):
    try:
        command = bot_tools.parse_command(ctx.message.content, 1)
    except ValueError:
        try:
            command = bot_tools.parse_command(ctx.message.content, 0)
        except ValueError:
            await ctx.send('Error: To remove/add a role, use !user_role followed by the role name. Just !user_role will list the available roles.')
            return
    if len(command) == 1:
        user_roles = [user_roles['name'] for user_roles in bot_db.get_all_user_roles()]
        await ctx.send('The self-assignable roles are: ```\n{}\n```'.format('\n'.join(user_roles)))
    else:
        [_, role_name] = command
        if not bot_db.exists_user_role(role_name):
            await ctx.send(f'Error: The role `{role_name}` is not on the list of self-assignalbe roles!')
            return
        else:
            if role_name in [author_roles.name for author_roles in ctx.author.roles]:
                role = next(role for role in ctx.author.roles if role.name == role_name)
                await ctx.author.remove_roles(role, reason=None, atomic=True)
                await ctx.send(f'Removed role `{role_name}` from your roles {ctx.author.name}!')
            else:
                role = next(role for role in ctx.guild.roles if role.name == role_name)
                await ctx.author.add_roles(role, reason=None, atomic=True)
                await ctx.send(f'Added role `{role_name}` to your roles {ctx.author.name}!')

bot.run(config.discord_token)