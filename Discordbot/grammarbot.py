import discord
import logging
from discord.ext import commands, tasks
import random
import os
from datetime import datetime


import config
import bot_db
import bot_tools

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=config.command_prefix, intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    guilds = bot.guilds
    for guild in guilds: 
        print(
            f'{bot.user.name} has connected to Discord guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
    await bot.change_presence(activity=discord.Game('Try !help'))
    bot_db.server_update('update', new_value={'guild_name': guilds[0].name})
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_member_join(member):
    guild = bot.guilds[0]
    channel = discord.utils.get(guild.channels, id=bot_db.server_get()['welcome_channel_id'])
    msg = random.choice(bot_tools.welcome_messages).replace('<user>', f'<@{member.id}>')
    mutes = bot_db.user_get({'_id': member.id})
    if mutes is not None:
        mutes = mutes['mutes']
        for mute in mutes:
            now = datetime.utcnow()
            log_channel = discord.utils.get(member.guild.channels, id=bot_db.server_get()['log_channel_id'])
            if now < mute['until']:
                await member.add_roles(discord.utils.get(member.guild.roles, id=bot_db.server_get()['mute_role_id']), reason=None, atomic=True)
                await log_channel.send(f'Member <@{member.id}> tried to rejoin to get unmuted. Mute role was attached to them again until the unmute time has come.')
                return
    await channel.send(f'{msg}\nThere are a few Roles you can assign yourself. Check out <#759415738820853790>!\n自分にロールをつけることもできます。 <#759415738820853790> をチェックしてください！')


# @bot.event
# async def on_message(message):
#     if message.author.bot:
#         return
#     elif message.content == 'o/':
#         await message.channel.send('\\o')
#     elif message.content == '\\o':
#         await message.channel.send('o/')
#     await bot.process_commands(message)


@bot_tools.is_admin()
@bot.command(
        name='reload', 
        aliases=['rl'], 
        brief='Reload the cogs.',
        help='This command allows you to reload all the cogs. This means that if any changes were made to the code, then doing this can apply those changes without having to restart the bot. **This command can only be used by a user with an admin role.**',
        usage='Usage: `!reload\!rl`')
async def relaod(ctx):
    cogs = ''
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.reload_extension(f'cogs.{filename[:-3]}')
            cogs += filename + '\n'
    
    await ctx.send(embed=bot_tools.create_simple_embed(ctx, 'Reloading', cogs))


# @bot.command(name='help', aliases=['?', 'h'], help='Alliases: `!h/!?`\nDisplays the help message.\nUsage: `!help/!h/!?`')
# async def help_message(ctx):
#     await ctx.send(embed=await bot_tools.create_help_embed(ctx, bot.cogs))





bot.run(config.discord_token)