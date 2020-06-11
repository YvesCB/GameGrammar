import discord

import config

client = discord.Client()

@client.event
async def on_ready():
    guild = client.guilds[0]
    print(
        f'{client.user} has connected to Discord guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

client.run(config.discord_token)