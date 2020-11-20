import discord
import random
from discord.ext import commands

import bot_tools
import bot_db
import config

eightball_answers = [
    'It is certain.',
    'It is decidedly so.',
    'Without a doubt.',
    'Yes - definitely.',
    'You may rely on it.',
    'As I see it, yes.',
    'Most likely.',
    'Outlook good.',
    'Yes.',
    'Signs point to yes.',
    'Reply hazy, try again.',
    'Ask again later.',
    'Better not tell you now.',
    'Cannot predict now.',
    'Concentrate and ask again.',
    'Don\'t count on it.',
    'My reply is no.',
    'My sources say no.',
    'Outlook not so good.',
    'Verby doubtful.'
]

def create_eightball_embed(author, message):
    answer = random.choice(eightball_answers)
    number = eightball_answers.index(answer)
    if number < 10:
        color = discord.Color.green()
    elif number > 9 and number < 15:
        color = discord.Color.gold()
    else:
        color = discord.Color.red()
    embed = discord.Embed(
        title = 'The magic 8 Ball will help you decide',
        description = 'Let\'s see...',
        color = color
    )
    embed.add_field(name='Your question:', value=message, inline=False)
    embed.add_field(name='My estimation:', value=answer, inline=False)
    embed.set_author(
        name = 'Magic 8 Ball',
        icon_url = 'https://magic-8ball.com/assets/images/magicBallStart.png'
    )
    embed.set_footer(text=f'Requsted by {author}')
    return embed


class ExtraStuff(commands.Cog, name='Extra fun stuff'):
    """An assortment of additional commands mostly for fun. These are the commands and functions of GrammarBot that are a little random and that don't really fit in any other category."""
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        name='magic_8ball', 
        aliases=['m8b'], 
        brief='Ask the Magic 8-Ball a question.',
        help='You can use this command to ask the Magic 8-Ball a question. Simply formulate your question after the command and the wise 8-Ball shall give you an answer. The answer are the official Magic 8-Ball answers.',
        usage='Usage: `!magic_8ball/!m8b YourQuestion`')
    async def eightball(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To ask the 8 Ball a question, make sure to add your question after the command. `!magic_8ball/!m8b <question>`.'))
            return

        [_, message] = command

        await ctx.send(embed=create_eightball_embed(ctx.author.name, message))


def setup(bot):
    bot.add_cog(ExtraStuff(bot))

        