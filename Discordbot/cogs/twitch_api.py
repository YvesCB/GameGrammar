
import discord
import json
import requests
from datetime import datetime, timedelta
from discord.ext import commands, tasks

import config
import bot_tools
import bot_db


def create_notif_embed(title, image_url, game, viewers):
    embed = discord.Embed(
        title="GameGrammar is live", colour=discord.Colour.blue(), url="https://twitch.tv/gamegrammar",
        description=title
    )
    embed.set_image(url=image_url)
    embed.set_thumbnail(
        url="https://static-cdn.jtvnw.net/jtv_user_pictures/6f4fd276-f717-41a7-986d-35f22cd68c38-profile_image-300x300.png"
    )

    embed.add_field(name="Game", value=game, inline=True)
    embed.add_field(name="Viewers", value=viewers, inline=True)
    return embed


def create_offline_embed(user, latest_title, latest_game, follow_count, sub_count, view_count, latest_vid_title, latest_vid_url):
    embed = discord.Embed(
        title="GameGrammar Twitch Stats", 
        colour=discord.Colour.blue(), 
        url="https://twitch.tv/gamegrammar", 
        description="The stats for the GameGrammar Twitch channel!"
    )

    embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/6f4fd276-f717-41a7-986d-35f22cd68c38-profile_image-300x300.png")
    embed.set_footer(text=f"Requested by {user.name}")

    embed.add_field(
        name="Status", 
        value="**Offline**", 
        inline=False
    )
    embed.add_field(
        name="Latest Title", 
        value=latest_title, 
        inline=True
    )
    embed.add_field(
        name="Latest Game", 
        value=latest_game, 
        inline=True
    )
    embed.add_field(
        name="Total views", 
        value=view_count, 
        inline=False
    )
    embed.add_field(
        name="Followers", 
        value=follow_count, 
        inline=False
    )
    embed.add_field(
        name="Subscribers", 
        value=sub_count-1, 
        inline=False
    )
    embed.add_field(
        name="Latest video", 
        value=f"{latest_vid_title}\n{latest_vid_url}", 
        inline=False
    )

    return embed


def create_live_embed(user, title, game, live_views, follow_count, sub_count, view_count, thumb_url):
    embed = discord.Embed(
        title="GameGrammar Twitch Stats", 
        colour=discord.Colour.blue(), 
        url="https://twitch.tv/gamegrammar", 
        description="The stats for the GameGrammar Twitch channel!"
    )

    embed.set_image(url=thumb_url)
    embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/6f4fd276-f717-41a7-986d-35f22cd68c38-profile_image-300x300.png")
    embed.set_footer(text=f"Requested by {user.name}")

    embed.add_field(
        name="Status", 
        value="**Live**", 
        inline=False
    )
    embed.add_field(
        name="Title", 
        value=title, 
        inline=True
    )
    embed.add_field(
        name="Game", 
        value=game, 
        inline=True
    )
    embed.add_field(
        name="Live viewers", 
        value=live_views, 
        inline=False
    )
    embed.add_field(
        name="Total views", 
        value=view_count, 
        inline=False
    )
    embed.add_field(
        name="Followers", 
        value=follow_count, 
        inline=False
    )
    embed.add_field(
        name="Subscribers", 
        value=sub_count-1, 
        inline=False
    )

    return embed


class TwitchAPI(commands.Cog, name='Twitch API'):
    """There is a number of functionality that makes use of the Twitch API. The bot monitors when a GameGrammar stream goes live and will automatically post a message in the appropriate channel. You can also get some staticsts of the Twitch channel by using the Twitch stats command. This will include things like Follower count, Subscriber count, latest VOD and, if the stream is currently live, viewer count."""
    is_live = False
    

    def __init__(self, bot):
        self.bot = bot
        is_live = False
        went_live_at = bot_db.server_get()
        if 'last_live' not in went_live_at['twitch'].keys():
            bot_db.server_update('update', new_value={'twitch.last_live': datetime.utcnow()})
        self.message = None
        self.twitch_status.start()


    def get_standard_headers(self):
        headers = {
                'Client-id': bot_db.server_get()['twitch']['client_id'],
                'Authorization': bot_db.server_get()['twitch']['oauth2']
                }
        return headers


    def get_access_token(self, code):
        headers = {
                'client_id': bot_db.server_get()['twitch']['client_id'],
                'client_secret': bot_db.server_get()['twitch']['client_secret'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://localhost'
                }
        access_data = requests.post(f'https://id.twitch.tv/oauth2/token', params=headers)

        return access_data.text


    def refresh_token(self):
        headers = {
                'Client-id': bot_db.server_get()['twitch']['client_id'],
                'Authorization': bot_db.server_get()['twitch']['oauth2'],
                'Client-secret': bot_db.server_get()['twitch']['client_secret']
                }
        params = {
                'refresh_token': bot_db.server_get()['twitch']['refresh'],
                'grant_type': 'refresh_token'
                }
        refresh_data = requests.post(f'https://id.twitch.tv/oauth2/token', params=params, headers=headers)

        return refresh_data.text


    def get_live_data(self):
        params = {
                'user_id': bot_db.server_get()['twitch']['channel_id']
                }
        live_data = requests.get(f'https://api.twitch.tv/helix/streams', params=params, headers=self.get_standard_headers())

        return live_data.text


    def get_broadcaster_data(self):
        params = {
                'broadcaster_id': f'{bot_db.server_get()["twitch"]["channel_id"]}',
                }
        broadcaster_data = requests.get(f'https://api.twitch.tv/helix/channels', params=params, headers=self.get_standard_headers())

        return broadcaster_data.text


    def get_user_info(self):
        params = {
                'id': bot_db.server_get()['twitch']['channel_id']
                }
        user_data = requests.get(f'https://api.twitch.tv/helix/users', params=params, headers=self.get_standard_headers())

        return user_data.text


    def get_videos(self):
        params = {
                'user_id': bot_db.server_get()['twitch']['channel_id']
                }
        videos = requests.get(f'https://api.twitch.tv/helix/videos', params=params, headers=self.get_standard_headers())

        return videos.text


    def get_follows(self):
        params = {
                'to_id': bot_db.server_get()['twitch']['channel_id']
                }
        follows = requests.get(f'https://api.twitch.tv/helix/users/follows', params=params, headers=self.get_standard_headers())

        return follows.text


    def get_subs(self):
        params = {
                'broadcaster_id': bot_db.server_get()['twitch']['channel_id']
                }
        subs = json.loads(requests.get(f'https://api.twitch.tv/helix/subscriptions', params=params, headers=self.get_standard_headers()).text)
        
        next_subs = subs

        cursor = subs['pagination']['cursor']

        while bool(next_subs['pagination']):
            cursor = next_subs['pagination']['cursor']
            next_subs = json.loads(requests.get(f'https://api.twitch.tv/helix/subscriptions?&after={cursor}', params=params, headers=self.get_standard_headers()).text)
            subs['data'].extend(next_subs['data'])

        return subs


    def get_game(self, game_id):
        params = {
                'id': game_id
                }
        game_data = requests.get(f'https://api.twitch.tv/helix/games', params=params, headers=self.get_standard_headers())

        return game_data.text


    # check if at least six hours have passed
    def six_h_passed(self):
        return datetime.utcnow > bot_db.server_get()['twitch']['last_live'] + timedelta(hours=6)


    @bot_tools.is_server_owner()
    @commands.command(
            name='twitch_authorize',
            aliases=['ta'],
            brief='Authorizes the bot with the Twitch API and returns OAuth Token and Refresh Token',
            help='With this command you can generate the OAuth Token and the Refresh Token for Twitch. It requires the code generated via the POST request <https://id.twitch.tv/oauth2/authorize?client_id=<your client ID>&redirect_uri=<your registered redirect URI>&response_type=code&scope=<space-separated list of scopes>>.',
            usage='Usage: `!twitch_authorize\!ta <code>`')
    async def twitch_authorize(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except:
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
            return
        
        [_, code] = command
        data = json.loads(self.get_access_token(code))

        if("status" in data):
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'An error occured. Response:\n```{data}```'))
            return
        else:
            await ctx.send(f'Successfully created credentials!')

        now = datetime.utcnow()
        delta = timedelta(seconds=(data['expires_in'] - 200))

        bot_db.server_update('update', new_value={'twitch.oauth2': f'Bearer {data["access_token"]}'})
        bot_db.server_update('update', new_value={'twitch.refresh': f'{data["refresh_token"]}'})
        bot_db.server_update('update', new_value={'twitch.refreshtime': now + delta})

        await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Twitch Authorization', _description=f'Updated Twitch credentials!\nToken: `{bot_db.server_get()["twitch"]["oauth2"]}`\nRefresh Token: `{bot_db.server_get()["twitch"]["refresh"]}`\nRefresh at: {bot_db.server_get()["twitch"]["refreshtime"].strftime("%d %b %y, %H:%M:%S GMT")}'))


    @bot_tools.is_server_owner()
    @commands.command(
            name='twitch_print_data',
            aliases=['tpd'],
            brief='Print the current Twitch API Data. Including Tokens.',
            help='With this command, you can display all the current information about the Twitch API. This includes things like the OAuth Token and the Cleint ID/Secret.',
            usage='Usage: `!twitch_print_data\!tpd`')
    async def twitch_print_data(self, ctx):
        client_id = bot_db.server_get()['twitch']['client_id']
        client_secret = bot_db.server_get()['twitch']['client_secret']
        oauth2 = bot_db.server_get()['twitch']['oauth2']
        refresh_token = bot_db.server_get()['twitch']['refresh']
        refresh_time = bot_db.server_get()['twitch']['refreshtime'].strftime("%d %b %y, %H:%M:%S GMT")
        last_live = bot_db.server_get()['twitch']['last_live'].strftime("%d %b %y, %H:%M:%S GMT")

        await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Twitch Data', _description=f'Client ID: `{client_id}`\nClient Secret: `{client_secret}`\nOAuth2 Token: `{oauth2}`\nRefresh Token: `{refresh_token}`\nRefresh Time: `{refresh_time}`\nLast Live: `{last_live}`'))


    @bot_tools.is_server_owner()
    @commands.command(
            name='twitch_change_id',
            aliases=['tci'],
            brief='Show or Change the saved Client ID for the Twitch API in the Database',
            help='With this comman you can either show the current Client ID for the Twitch API or change it to a new one. To show the current one, simply use the command without an argument.',
            usage='Usage: `!twitch_change_id\!tci <ID>`')
    async def twitch_change_id(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except:
            try:
                command = bot_tools.parse_command(ctx.message.content, 0)
            except:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
                return
            
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Twitch Client ID', _description=f'The current Client ID is: `{bot_db.server_get()["twitch"]["client_id"]}`'))
            return
        
        [_, client_id] = command
        old_id = bot_db.server_get()['twitch']['client_id']
        bot_db.server_update('update', new_value={'twitch.client_id': client_id})

        await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Twitch Client ID', _description=f'Changed Client ID\nFrom: `{old_id}`\nTo:`{bot_db.server_get()["twitch"]["client_id"]}`'))


    @bot_tools.is_server_owner()
    @commands.command(
            name='twitch_change_secret',
            aliases=['tcs'],
            brief='Show or Change the saved Client Secret for the Twitch API in the Database',
            help='With this comman you can either show the current Client Secret for the Twitch API or change it to a new one. To show the current one, simply use the command without an argument.',
            usage='Usage: `!twitch_change_secret\!tcs <Secret>`')
    async def twitch_change_secret(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except:
            try:
                command = bot_tools.parse_command(ctx.message.content, 0)
            except:
                await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Error', _description=f'{ctx.command.usage}. Use `!help {ctx.command.name}` for more details.'))
                return
            
            await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Twitch Client Secret', _description=f'The current Client secret is: `{bot_db.server_get()["twitch"]["client_secret"]}`'))
            return
        
        [_, client_secret] = command
        old_secret = bot_db.server_get()['twitch']['client_secret']
        bot_db.server_update('update', new_value={'twitch.client_secret': client_secret})

        await ctx.send(embed=bot_tools.create_simple_embed(ctx=ctx, _title='Twitch Client Secret', _description=f'Changed Client ID\nFrom: `{old_secret}`\nTo:`{bot_db.server_get()["twitch"]["client_secret"]}`'))


    @commands.guild_only()
    @commands.command(
        name='twitch_stats', 
        aliases=['ts'], 
        brief='Shows statistics of the GameGrammar Twitch channel.',
        help='With this command you can at any point see information about the GameGrammar Twitch channel. Especially useful if you want a quick link to the channel or the lastes VOD.',
        usage='Usage: `!twitch_stats\!ts`')
    async def twitch_stats(self, ctx):
        data = json.loads(self.get_live_data())
        
        # if stream online
        if len(data['data']) > 0:
            game_data = json.loads(self.get_game(data['data'][0]['game_id']))
            follows = json.loads(self.get_follows())
            subs = self.get_subs()
            user_info = json.loads(self.get_user_info())

            title = data['data'][0]['title']
            game_name = ''
            try:
                game_name = game_data['data'][0]['name']
            except:
                game_name = 'None'
            viewer_count = data['data'][0]['viewer_count']
            follow_count = follows['total']
            sub_count = len(subs['data'])
            view_count = user_info['data'][0]['view_count']
            thumb_url = data['data'][0]['thumbnail_url'].replace('{width}', '1280').replace('{height}', '720')

            await ctx.send(
                embed=create_live_embed(
                    ctx.author,
                    title,
                    game_name,
                    viewer_count,
                    follow_count,
                    sub_count,
                    view_count,
                    thumb_url
                )
            )
    
        # if stream offline
        else:
            broadcaster_data = json.loads(self.get_broadcaster_data())
            game_data = json.loads(self.get_game(broadcaster_data['data'][0]['game_id']))
            follows = json.loads(self.get_follows())
            subs = self.get_subs()
            user_info = json.loads(self.get_user_info())
            latest_video = json.loads(self.get_videos())

            title = broadcaster_data['data'][0]['title']
            game_name = ''
            try:
                game_name = game_data['data'][0]['name']
            except:
                game_name = 'None'

            follower_count = follows['total']
            sub_count = len(subs['data'])
            view_count = user_info['data'][0]['view_count']
            latest_video_title = latest_video['data'][0]['title']
            latest_video_url = latest_video['data'][0]['url']

            await ctx.send(
                embed=create_offline_embed(
                    ctx.author,
                    title,
                    game_name,
                    follower_count,
                    sub_count,
                    view_count,
                    latest_video_title,
                    latest_video_url
                )
            )


    def cog_unload(self):
        self.twitch_status.cancel()


    @tasks.loop(seconds=60)
    async def twitch_status(self):
        data = json.loads(self.get_live_data())
        try:
            # if stream online
            guild = discord.utils.get(self.bot.guilds, name=bot_db.server_get()["guild_name"])
            channel = discord.utils.get(guild.channels, id=bot_db.server_get()["stream_channel_id"])
            if len(data['data']) > 0 and not self.is_live and self.six_h_passed():
                game = json.loads(self.get_game(data['data'][0]['game_id']))
                title = data['data'][0]['title']
                thumb_url =  data['data'][0]['thumbnail_url'].replace('{width}', '1280').replace('{height}', '720')
                game_name = ''
                try:
                    game_name = game['data'][0]['name']
                except:
                    game_name = 'None'
                viewer_count = data['data'][0]['viewer_count']

                self.message = await channel.send(
                    content='Hey <@&739058472704016487> , GameGrammar has gone live!', 
                    embed=create_notif_embed(
                        title,
                        thumb_url,
                        game_name,
                        viewer_count
                    )
                )
                bot_db.server_update('update', new_value={'twitch.live_at': datetime.utcnow()})
                self.is_live = True
                print('Stream went live')
            elif len(data['data']) == 0 and self.is_live:
                self.is_live = False
                print('Not live anymore!')
            elif len(data['data']) > 0 and self.is_live:
                game = json.loads(self.get_game(data['data'][0]['game_id']))
                title = data['data'][0]['title']
                thumb_url =  data['data'][0]['thumbnail_url'].replace('{width}', '1280').replace('{height}', '720')
                game_name = ''
                try:
                    game_name = game['data'][0]['name']
                except:
                    game_name = 'None'
                viewer_count = data['data'][0]['viewer_count']

                await self.message.edit( 
                    content='Hey <@&739058472704016487> , GameGrammar has gone live!', 
                    embed=create_notif_embed(
                        title,
                        thumb_url,
                        game_name,
                        viewer_count
                    )
                )
        except Exception as e:
            print('Error while trying to post live ping!', e)
            print(data)
            pass

        refreshtime = bot_db.server_get()['twitch']['refreshtime']
        now = datetime.utcnow()

        if now > refreshtime:
            raw_data = self.refresh_token()
            print(raw_data)
            refresh_data = json.loads(self.refresh_token())

            if not "status" in refresh_data:
                delta = timedelta(seconds=(refresh_data['expires_in'] - 200))
                bot_db.server_update('update', new_value={'twitch.oauth2': f'Bearer {refresh_data["access_token"]}'})
                bot_db.server_update('update', new_value={'twitch.refresh': f'{refresh_data["refresh_token"]}'})
                bot_db.server_update('update', new_value={'twitch.refreshtime': now + delta})

                print(f'Updated Twitch credentials!\nToken: {bot_db.server_get()["twitch"]["oauth2"]}\nRefresh Token: {bot_db.server_get()["twitch"]["refresh"]}\nRefresh at: {bot_db.server_get()["twitch"]["refreshtime"].strftime("%d %b %y, %H:%M:%S GMT")}')

            else:
                print(f'Error while trying to refresh oauth token\n{refresh_data}')



def setup(bot):
    bot.add_cog(TwitchAPI(bot))
