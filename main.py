import os
from dotenv import load_dotenv
load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

import discord 

bot = discord.Client(intents=discord.Intents.default())

STARTUP_CHANNEL_ID = 1252983015169196177

@bot.event

async def on_ready():
    guild_count=0

    for guild in bot.guilds:
        # PRINT THE SERVER'S ID AND NAME.
        print(f"- {guild.id} (name: {guild.name})")
        # INCREMENTS THE GUILD COUNTER.
        guild_count = guild_count + 1
        
    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")

    #channel = bot.get_channel(STARTUP_CHANNEL_ID)
    #if channel:
    #   await channel.send("SampleDiscordBot has started and is now online!")

@bot.event
async def on_message(message):
	# CHECKS IF THE MESSAGE THAT WAS SENT IS EQUAL TO "HELLO".
    #if message.author == bot.user:
    #    return

    print("wow, i just got a message")
    if message.content == "hello":
		# SENDS BACK A MESSAGE TO THE CHANNEL.
        print("hi")
        channel = bot.get_channel(STARTUP_CHANNEL_ID)
        if channel:
            await channel.send("SampleDiscordBot has started and is now online!")

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run("MTI1Mjk4MTE2NjE4MTcxMTg3NA.GplJmK.CAPGvqFNy1OlfgSMtWznlTsd_HOov-VWRJVlyI")