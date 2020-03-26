from twitchio.ext import commands
import json
import requests

import unicodedata

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(irc_token='', client_id='junkcracker', nick='yvesbot', prefix='!',
                         initial_channels=['gamegrammar'])

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f'Ready | {self.nick}')

    async def event_message(self, message):
        print(message.content)
        await self.handle_commands(message)

    # Commands use a different decorator
    @commands.command(name='test')
    async def my_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command(name='j')
    async def jisho_command(self, ctx):
        message = ctx.message.content[3:]
        index = 0
        # print(message)
        if len(message) > 1:
            if len([int(s) for s in message.split() if s.isdigit()]) > 0:
                index = [int(s) for s in message.split() if s.isdigit()][0] - 1
                index_digit_count = len(str(index))
                message = message[:-(index_digit_count)]

        # print(message)
        # print(index) 

        searchres = self.jisho(message)

        if searchres == -1:
            await ctx.send('No results...')
        else:
            if index >= len(searchres):
                index = 0
            else:
                await ctx.send("gamegr2Hmmm " + searchres[index]["word_jp"] + " " + searchres[index]["reading"] + " " + str(searchres[index]["english"]).replace('[', '').replace(']','').replace('\'',"\"") + " " + str(searchres[index]["parts_of_speech"]).replace('\'', '') + " " + str(index+1) + "/" + str(len(searchres)))

    @commands.command(name='twitter')
    async def twitter_command(self, ctx):
        await ctx.send('')

    def jisho(self, keyword):
    
        data = json.loads(requests.get(
                "http://jisho.org/api/v1/search/words?keyword={}".format(keyword)).text)["data"]
        
        results = []

        if len(data) == 0:
            print("No results...")
            return(-1)
        else:
             for search_result in data:
                curr = {"word_jp" : "", "reading" : "", "english" : [], "parts_of_speech" : []}
                if "word" in search_result["japanese"][0]:
                    curr["word_jp"] = search_result["japanese"][0]["word"]
                if "reading" in search_result["japanese"][0]:
                    curr["reading"] = search_result["japanese"][0]["reading"]
                for eng in search_result["senses"][0]["english_definitions"]:
                    curr["english"].append(eng)
                for parts in search_result["senses"][0]["parts_of_speech"]:
                    curr["parts_of_speech"].append(parts)
                results.append(curr)
        return results

            # for key in range(len(data["data"])):
            #     results.append({"word_jp" : "", "reading" : "", "english" : [], "parts_of_speech" : []})
            #     for entry in range(len(data["data"][key]["japanese"])):
            #         if "word" in data["data"][key]["japanese"][entry]:
            #             results[key]["word_jp"] = data["data"][key]["japanese"][entry]["word"]
            #             # print(data["data"][key]["japanese"][entry]["word"] + ' ' + data["data"][key]["japanese"][entry]["reading"])
            #         if "reading" in data["data"][key]["japanese"][entry]:
            #             results[key]["reading"] = data["data"][key]["japanese"][entry]["reading"]
                
            #     for eng in data["data"][key]["senses"][0]["english_definitions"]:
            #         results[key]["english"].append(eng)
            #     for parts in data["data"][key]["senses"][0]["parts_of_speech"]:
            #         results[key]["parts_of_speech"].append(parts)
        


bot = Bot()
bot.run()