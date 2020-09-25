import discord
from discord.ext import commands, tasks
import random
import os


import config
import bot_db
import bot_tools


bot = commands.Bot(command_prefix=config.command_prefix)
bot.remove_command('help')


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=config.discord_guild)
    print(
        f'{bot.user.name} has connected to Discord guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    await bot.change_presence(activity=discord.Game('Try !help'))


@bot.event
async def on_member_join(member):
    guild = discord.utils.get(bot.guilds, name=config.discord_guild)
    channel = discord.utils.get(guild.channels, id=410321201395924992)
    msg = random.choice(bot_tools.welcome_messages).replace('<user>', f'<@{member.id}>')
    await channel.send(f'{msg}\nThere are a few Roles you can assign yourself. Simply use `!ur` to get a list of the roles that are available.\n自分にロールをつけることもできます。 `!ur`を入力したら、ロールのリストが表示されます。')


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    elif message.content == 'o/':
        await message.channel.send('\\o')
    elif message.content == '\\o':
        await message.channel.send('o/')
    await bot.process_commands(message)


@bot_tools.is_admin()
@bot.command(name='reload', aliases=['rl'], help='Reloads all the cogs.\nUsage:')
async def relaod(ctx):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.reload_extension(f'cogs.{filename[:-3]}')

# @bot.command(name='help', aliases=['?', 'h'], help='Alliases: `!h/!?`\nDisplays the help message.\nUsage: `!help/!h/!?`')
# async def help_message(ctx):
#     await ctx.send(embed=await bot_tools.create_help_embed(ctx, bot.cogs))


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(config.discord_token)