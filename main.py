import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

import discord 

intents=discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True

bot = discord.Client(intents = intents)

STARTUP_CHANNEL_ID = 1252983015169196177

conn = mysql.connector.connect(host="localhost",user="root", password="8o0k3d@ndW0ok3d",database="cwiki_schema")
conn.commit=True
c=conn.cursor(buffered=True)

@bot.event

#async def test(ctx):
#    sender=str(ctx.author.id)
#    c.execute("SELECT username FROM accounts WHERE discordid=%s", (sender,))
#    username=c.fetchone()
#    await ctx.respond("Username: "+str(username[0]))

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
    if message.content == "hello":
        # SENDS A MESSAGE BACK TO THE CHANNEL.
        await message.channel.send("hey dirtbag")
        sender=str(message.author.id)
        user=str(message.author.name)
        
       # c.execute("INSERT INTO `cwiki_schema`.`accounts` (`id`, `discordid`, `username`) VALUES ('2', '"+sender+"', '"+user+"')")

        #await message.channel.send(user)
        c.execute("SELECT username FROM accounts WHERE discordid=%s", (sender,))
        username=c.fetchone()
        await message.channel.send("Username: "+str(username[0]))


# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run("MTI1Mjk4MTE2NjE4MTcxMTg3NA.GplJmK.CAPGvqFNy1OlfgSMtWznlTsd_HOov-VWRJVlyI")