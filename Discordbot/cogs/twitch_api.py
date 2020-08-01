import discord
import json
import requests
import time
from discord.ext import commands, tasks

import config
import bot_tools


class TwitchAPI(commands.Cog, name='Twitch API handling'):
    data = {}
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


    # check if at least six hours have passed
    def six_h_passed(self):
        return time.time() - self.went_live_at > 21600

    @tasks.loop(seconds=60)
    async def twitch_status(self):
        self.data = json.loads(self.get_data())
        try:
            # if stream online
            if len(self.data['data']) > 0 and not self.is_live and self.six_h_passed():
                guild = discord.utils.get(self.bot.guilds, name=config.discord_guild)
                channel = discord.utils.get(guild.channels, id=config.stream_channel_id)
                print(guild.name, channel.name)
                await channel.send('Hey @Streamping , {} has gone live playing: {}\nhttps://twitch.tv/gamegrammar'.format(self.data['data'][0]['user_name'], self.data['data'][0]['title']))
                self.went_live_at = time.time()
                self.is_live = True
                print('Stream went live')
            elif len(self.data['data']) == 0 and self.is_live:
                self.is_live = False
                print('Not live anymore!')
        except:
            print('Error while trying to post live ping!')
            pass


def setup(bot):
    bot.add_cog(TwitchAPI(bot))
    bot.cogs.get('Twitch API handling').twitch_status.start()
    