from discord.ext import commands
import discord

import bot_tools
import bot_db


class TagSystem(commands.Cog, name='Tag system'):
    """This is the docstring"""
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(name='tag', aliases=['t'], help='Call pre-written messages called tags. Show list of tags if no tag is specified.\nUsage: `!tag/!t <name>`')
    async def get_tag(self, ctx):
        try: 
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            try:
                command = bot_tools.parse_command(ctx.message.content, 0)
            except:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='All tags are one word only.'))
                return
        if len(command) == 1:
            tags = [t['name'] for t in bot_db.get_all_tags()]
            await ctx.send(embed=bot_tools.create_list_embed(ctx=ctx, _title='Tags', _description='Here is a list of all the tags you can use.', _field_name='Tags', items=tags))
        else:
            [_, tag_name] = command
            tag = bot_db.get_tag(tag_name)
            if not bot_db.exists_tag(tag_name):
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The Tag `{tag_name}` does not exists.'))
            else:
                await ctx.send(tag['response'])


    @commands.command(name='tag_add', aliases=['t_add'], help='Add a new tag to the list of tags.\nCan only be used by admins!\nUsage: `!tag_add/!t_add <name> <message>`')
    @bot_tools.is_admin()
    async def add_tag(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To create tags, use `!tag_add/!t_add <name> <message>`.'))
            return
        [_, tag_name, tag_content] = command
        if bot_db.exists_tag(tag_name):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The tag `{tag_name}` already exists.'))
            return
        else:
            bot_db.add_tag(tag_name, tag_content)
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Tag', _description=f'Successfully added tag `{tag_name}`!'))



    @commands.command(name='tag_remove', aliases=['t_remove'], help='Remove an existing tag.\nCan only be used by admins!\nUsage: `!tag_remove/!t_remove <name>`')
    @bot_tools.is_admin()
    async def remove_tag(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description='To remove a tag, use `!t_remove <name>`.'))
            return
        [_, tag_name] = command
        if not bot_db.exists_tag(tag_name):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'`{tag_name}` does not exists!'))
            return
        else:
            bot_db.remove_tag(tag_name)
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Tag', _description=f'Successfully removed tag `{tag_name}`'))


def setup(bot):
    bot.add_cog(TagSystem(bot))