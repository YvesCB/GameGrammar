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
    await channel.send(msg)


@bot.event
async def on_message(ctx):
    if ctx.author.bot:
        return
    elif ctx.content == 'o/':
        await ctx.channel.send('\\o')
    elif ctx.content == '\\o':
        await ctx.channel.send('o/')


@bot.command(name='help', aliases=['?', 'h'], help='Alliases: `!h/!?`\nDisplays the help message.\nUsage: `!help/!h/!?`')
async def help_message(ctx):
    await ctx.send(embed=await bot_tools.create_help_embed(ctx, bot.commands))


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(config.discord_token)