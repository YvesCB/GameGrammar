import discord
import json
import requests
import time
from discord.ext import commands, tasks

import config
import bot_tools


def create_embed(title, image_url, game, viewers):
    embed = discord.Embed(
        title="GameGrammar is live", colour=discord.Colour.blue(), url="https://twitch.tv/gamegrammar",
        description=title
    )
    embed.set_image(url=image_url)
    embed.set_thumbnail(
        url="https://static-cdn.jtvnw.net/jtv_user_pictures/6f4fd276-f717-41a7-986d-35f22cd68c38-profile_image-300x300.png"
    )

    embed.add_field(name="**Game**", value=game, inline=True)
    embed.add_field(name="**Viewers**", value=viewers, inline=True)
    return embed


class TwitchAPI(commands.Cog, name='Twitch API handling'):
    data = {}
    game = {}
    is_live = False
    went_live_at = 0
    
    def __init__(self, bot):
        self.bot = bot


    def get_data(self):
        para = {
            'Client-id': config.Client_id,
            'Authorization': config.Oauth2
        }

        r = requests.get('https://api.twitch.tv/helix/streams?user_id=427289393', headers=para)

        return r.text

    
    def get_game(self, game_id):
        para = {
            'Client-id': config.Client_id,
            'Authorization': config.Oauth2
        }

        r = requests.get(f'https://api.twitch.tv/helix/games?id={game_id}', headers=para)

        return r.text


    # check if at least six hours have passed
    def six_h_passed(self):
        return time.time() - self.went_live_at > 21600

    @tasks.loop(seconds=10)
    async def twitch_status(self):
        self.data = json.loads(self.get_data())
        try:
            # if stream online
            if len(self.data['data']) > 0 and not self.is_live and self.six_h_passed():
                guild = discord.utils.get(self.bot.guilds, name=config.discord_guild)
                channel = discord.utils.get(guild.channels, id=config.stream_channel_id)
                print(guild.name, channel.name)
                self.game = json.loads(self.get_game(self.data['data'][0]['game_id']))
                await channel.send(
                    content='Hey <@&739058472704016487> , GameGrammar has gone live!', 
                    embed=create_embed(
                        self.data['data'][0]['title'], 
                        self.data['data'][0]['thumbnail_url'].replace('{width}', '1280').replace('{height}', '720'),
                        self.game['data'][0]['name'], 
                        self.data['data'][0]['viewer_count']
                    )
                )
                self.went_live_at = time.time()
                self.is_live = True
                print('Stream went live')
            elif len(self.data['data']) == 0 and self.is_live:
                self.is_live = False
                print('Not live anymore!')
        except Exception as e:
            print('Error while trying to post live ping!', e)
            pass


def setup(bot):
    bot.add_cog(TwitchAPI(bot))
    bot.cogs.get('Twitch API handling').twitch_status.start()
    