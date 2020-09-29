import discord
import json
import requests
import time
from discord.ext import commands, tasks

import config
import bot_tools


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


class TwitchAPI(commands.Cog, name='Twitch API handling'):
    is_live = False
    went_live_at = 0
    
    para = {
        'Client-id': config.Client_id,
        'Authorization': config.Oauth2,
    }

    def __init__(self, bot):
        self.bot = bot


    def get_live_data(self):
        live_data = requests.get(f'https://api.twitch.tv/helix/streams?user_id={config.user_id}', headers=self.para)

        return live_data.text


    def get_broadcaster_data(self):
        broadcaster_data = requests.get(f'https://api.twitch.tv/helix/channels?broadcaster_id={config.user_id}', headers=self.para)

        return broadcaster_data.text


    def get_user_info(self):
        user_data = requests.get(f'https://api.twitch.tv/helix/users?id={config.user_id}', headers=self.para)

        return user_data.text


    def get_videos(self):
        videos = requests.get(f'https://api.twitch.tv/helix/videos?user_id={config.user_id}', headers=self.para)

        return videos.text


    def get_follows(self):
        follows = requests.get(f'https://api.twitch.tv/helix/users/follows?to_id={config.user_id}', headers=self.para)

        return follows.text


    def get_subs(self):
        subs = json.loads(requests.get(f'https://api.twitch.tv/helix/subscriptions?broadcaster_id={config.user_id}', headers=self.para).text)
        
        next_subs = subs

        cursor = subs['pagination']['cursor']

        while bool(next_subs['pagination']):
            cursor = next_subs['pagination']['cursor']
            next_subs = json.loads(requests.get(f'https://api.twitch.tv/helix/subscriptions?broadcaster_id={config.user_id}&after={cursor}', headers=self.para).text)
            subs['data'].extend(next_subs['data'])

        return subs


    def get_game(self, game_id):
        game_data = requests.get(f'https://api.twitch.tv/helix/games?id={game_id}', headers=self.para)

        return game_data.text


    # check if at least six hours have passed
    def six_h_passed(self):
        return time.time() - self.went_live_at > 21600


    @commands.command(name='twitch_stats', aliases=['ts'], help='Shows statistics of the GameGrammar Twitch channel.\nUsage: `!twitch_stats/!ts`')
    @commands.guild_only()
    async def twitch_stats(self, ctx):
        data = json.loads(self.get_live_data())
        # if stream online
        if len(data['data']) > 0:
            game_data = json.loads(self.get_game(data['data'][0]['game_id']))
            follows = json.loads(self.get_follows())
            subs = self.get_subs()
            user_info = json.loads(self.get_user_info())

            await ctx.send(
                embed=create_live_embed(
                    ctx.author,
                    data['data'][0]['title'],
                    game_data['data'][0]['name'],
                    data['data'][0]['viewer_count'],
                    follows['total'],
                    len(subs['data']),
                    user_info['data'][0]['view_count'],
                    data['data'][0]['thumbnail_url'].replace('{width}', '1280').replace('{height}', '720')
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

            await ctx.send(
                embed=create_offline_embed(
                    ctx.author,
                    broadcaster_data['data'][0]['title'],
                    game_data['data'][0]['name'],
                    follows['total'],
                    len(subs['data']),
                    user_info['data'][0]['view_count'],
                    latest_video['data'][0]['title'],
                    latest_video['data'][0]['url']
                )
            )


    @tasks.loop(seconds=10)
    async def twitch_status(self):
        data = json.loads(self.get_live_data())
        try:
            # if stream online
            if len(data['data']) > 0 and not self.is_live and self.six_h_passed():
                guild = discord.utils.get(self.bot.guilds, name=config.discord_guild)
                channel = discord.utils.get(guild.channels, id=config.stream_channel_id)
                print(guild.name, channel.name)
                game = json.loads(self.get_game(data['data'][0]['game_id']))
                await channel.send(
                    content='Hey <@&739058472704016487> , GameGrammar has gone live!', 
                    embed=create_notif_embed(
                        data['data'][0]['title'], 
                        data['data'][0]['thumbnail_url'].replace('{width}', '1280').replace('{height}', '720'),
                        game['data'][0]['name'], 
                        data['data'][0]['viewer_count']
                    )
                )
                self.went_live_at = time.time()
                self.is_live = True
                print('Stream went live')
            elif len(data['data']) == 0 and self.is_live:
                self.is_live = False
                print('Not live anymore!')
        except Exception as e:
            print('Error while trying to post live ping!', e)
            pass


def setup(bot):
    bot.add_cog(TwitchAPI(bot))
    bot.cogs.get('Twitch API handling').twitch_status.start()
    