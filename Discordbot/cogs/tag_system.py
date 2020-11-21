from discord.ext import commands
import discord

import bot_tools
import bot_db


class TagSystem(commands.Cog, name='Tags'):
    """There are so-called \"Tags\" on the server you can use. A tag is simply a pre-written message that can be be posted by the bot. Each tag simply has a name and when called with post its contents. Some are text, others are pictures or vides. You can see the whole list by just using the tag command without an argument. Adding and removing of tags is limited to admins."""
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(
        name='tag', 
        aliases=['t'], 
        brief='Display the specified tag or show the list of tags when none specified.',
        help='Use the tag command to either see the tags you can use or to make the bot display a specific tag. If you use the command without a tag name specified it will show you the list of tags. Some tags are used to post information that is frequently needed and some others are more for fun. Feel free to test them out but don\'t spam them.',
        usage='Usage: `!tag\!t` or `!tag\!t TagName`')
    async def get_tag(self, ctx):
        try: 
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            try:
                command = bot_tools.parse_command(ctx.message.content, 0)
            except:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
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


    @bot_tools.is_admin()
    @commands.command(
        name='tag_add', 
        aliases=['t_add'], 
        brief='Add a new tag to the list of available tags.',
        help='With this command you can add a new tag to the list of tags available on the server. Make sure to give it a name and specify the content that it should have. It can be anything that you can write into the text bot. **This command can only be used by users with an admin role.**',
        usage='Usage: `!tag_add\!t_add TagName TagContent`')
    async def add_tag(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return
        [_, tag_name, tag_content] = command
        if bot_db.exists_tag(tag_name):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'The tag `{tag_name}` already exists.'))
            return
        else:
            bot_db.add_tag(tag_name, tag_content)
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Tag', _description=f'Successfully added tag `{tag_name}`!'))



    @bot_tools.is_admin()
    @commands.command(
        name='tag_remove', 
        aliases=['t_remove'], 
        brief='Remove one of the tags form the list of available tags.',
        help='With this command you can remove one of the existing tags from the list of available tags. This is not reversable so be careful. If you delete a tag accidentally it will have to be added again manually. **This command can only be used by users with an admin role.**',
        usage='Usage: `!tag_remove\!t_remove TagName`')
    async def remove_tag(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
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