from discord.ext import commands
import discord

import config
import bot_db

welcome_messages = [
    'Hello <user>, what a joy to have you here! よろしく！',
    'I feel better already, knowing that we have <user> here now! よろしく！',
    'I too have a passion for Grammar you see, so I\'m sure we\'ll get along <user>! よろしく！',
    'It is my pleasure as the bot of this here discord to welcome you <user>! よろしく！',
    'You must be new here <user> but don\'t worry, we\'ve banned all the members that bite so no need to be shy! よろしく!',
    'You know, I wasn\'t sure what to think of today but now that <user> is here, things are starting to look up! よろしく!', 
    'お初にお目にかかります<user>様、グラマーボットです。どうぞよろしくおねがいします！',
    'A good day to you <user>! I hope you\'ll feel at home here! よろしく！', 
    'Positions everyone! <user> is here now! I want everyone on their best behaviour! よろしく!',
    'なんと！<user>さんがサーバーに参加しました！よろしくおねがいします！',
    'ようこそ、<user>さん！どうぞごゆっくりしてください！'
]


class AdminCheckFailure(commands.CheckFailure):
    pass


def is_admin():
    async def predicate(ctx):
        is_admin_bool = common_member([r['name'] for r in bot_db.get_all_admin_roles()], [roles.name for roles in ctx.author.roles]) or ctx.author.id == config.default_admin_id 
        if not is_admin_bool:
            raise AdminCheckFailure()
        return True 
    return commands.check(predicate)


def parse_command(message, n_arguments=None):
    """
    Splits a message into its command's components. A command has the structure:

    ```
    !<name>[ <argument>]*
    ```

    So for example `!hello`, `!hello a` or `!hello a b`.

    If we know we only have `n_arguments`, we can collapse the superfluous arguments into one
    string. This is useful for example when we have `!add_tag hello Hello everyone!`. Parsing
    this with `n_arguments = 2` yields `['add_tag', 'hello', 'Hello everyone!']`.
    """
    splits = message[1:].split(' ')
    if len(splits) - 1 < n_arguments:
        raise ValueError(
            'Too few arguments. Expected {} and got {}.'.format(n_arguments, len(splits) - 1)
        )
    if n_arguments is None:
        return splits
    else:
        return splits[:n_arguments] + [' '.join(splits[n_arguments:])]


def common_member(a, b):
    a_set = set(a)
    b_set = set(b)
    if len(a_set.intersection(b_set)) > 0:
        return(True)
    return(False)


async def create_help_embed(ctx, commands):
    help_embed = discord.Embed(
        title = 'Commands',
        description = 'Here are all the commands supported by GrammarBot',
        color = discord.Color.blue()
    )
    help_embed.set_footer(text='WIP')
    for command in commands:
        try:
            await command.can_run(ctx)
            help_embed.add_field(name = f'!{command.name}', value=f'{command.help}', inline=False)
        except:
            pass
    return help_embed
    

def create_list_embed(_title, _description, _field_name, items):
    list_embed = discord.Embed(
        title = _title,
        description = _description,
        color = discord.Color.blue()
    )
    list_embed.set_footer(text='WIP')
    if len(items) == 0:
        list_embed.add_field(name = 'Roles', value = 'There are currently no user assignable roles. An admin can add them useing `!user_role_add/!ur_add <role_name>`')
    else:
        list_embed.add_field(name = _field_name, value = '{}'.format('\n'.join(items)), inline=False)
    return list_embed


def create_simple_embed(_title, _description):
    sipmle_embed = discord.Embed(
        title = _title,
        description = _description,
        color = discord.Color.blue()
    )        
    sipmle_embed.set_footer(text='WIP')
    return sipmle_embed