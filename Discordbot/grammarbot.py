import discord
from discord.ext import commands
import random

import config
import bot_db
import bot_tools

bot = commands.Bot(command_prefix=config.command_prefix)

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
async def add_tag(ctx):
    if bot_tools.is_admin(ctx.author):
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
    else:
        await ctx.send('Error: **You must be an admin to use this command!**')

@bot.command(name='t_remove', help='Remove an existing tag. Usage: !t_remove <name>')
async def remove_tag(ctx):
    if bot_tools.is_admin(ctx.author):
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
    else:
        await ctx.send('Erorr: **You must be an admin to use this command!**')

@bot.command(name='admins', help='Shows a list of all current admin roles.')
async def list_admins(ctx):
    admins = [admins['name'] for admins in bot_db.get_all_admin_roles()]
    await ctx.send('The admin roles are: ```\n{}\n```'.format('\n'.join(admins)))

@bot.command(name='admin_add', help='Adds a role to the list of admins. **Can only be used by admins!**')
async def add_admin(ctx):
    if ctx.author.id == config.default_admin_id or bot_tools.is_admin(ctx.author):
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
    else:
        await ctx.send('**You must be an admin to use this command!**')

@bot.command(name='admin_remove', help='Removes a role from the list of admins. **Can only be used by admins!**')
async def remove_admin(ctx):
    if ctx.author.id == config.default_admin_id or bot_tools.is_admin(ctx.author):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send('Error: To add a role to admins, use !admin_add followed by the role name.')
            return
        [_, role_name] = command
        if not bot_db.exists_admin_role(role_name):
            await ctx.send(f'Error: The role `{role_name}` is not on the list of admins!')
            return
        else:
            bot_db.remove_admin_role(role_name)
            await ctx.send(f'Sucessfully removed the role `{role_name}` fromt the list of amdins!')
    else:
        await ctx.send('**You must be an admin to use this command!**')


bot.run(config.discord_token)