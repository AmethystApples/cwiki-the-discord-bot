import os
import mysql.connector
from dotenv import load_dotenv
from datetime import date

load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

import discord
from discord.ext import commands 
from discord import app_commands

intents=discord.Intents.all()
intents.message_content = True
intents.messages = True
intents.members = True


bot = commands.Bot(command_prefix='/', intents = intents)



STARTUP_CHANNEL_ID = 1252983015169196177

conn = mysql.connector.connect(host="localhost",user="root", password="8o0k3d@ndW0ok3d",database="cwiki_schema")

c=conn.cursor(buffered=True)

@bot.hybrid_command()
async def ping(message: commands.Context):
    await message.send('pong')

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
    await bot.tree.sync()
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
        c.execute("SELECT discordid FROM cwiki_schema.accounts WHERE EXISTS(SELECT * FROM cwiki_schema.accounts WHERE discordid=%s)", (sender,))
        if c.fetchone():
            c.execute("SELECT username FROM accounts WHERE discordid=%s", (sender,))
            username=c.fetchone()
            await message.channel.send("Username: "+str(username[0]))
            print("user found")
        else: 
            c.execute("INSERT INTO cwiki_schema.accounts (discordid, username) VALUES (%s, %s)", (sender, user))
            conn.commit()
            print("user not found")
        # await message.channel.send(user)

@bot.hybrid_command(name="entry", description="define a term")        
async def entry(message, word: str = "term", definition: str ="your entry"):
    await message.send("Here is your word "+word+" and definitions "+definition)
    server=str(message.guild.id)

    #add word
    #need to check if word already exists in server
    c.execute("INSERT INTO cwiki_schema.words (serverid, wordname) VALUES (%s, %s)", (server, word))
    conn.commit()

    #add user
    sender=str(message.author.id)
    user=str(message.author.name)
    c.execute("SELECT discordid FROM cwiki_schema.accounts WHERE EXISTS(SELECT * FROM cwiki_schema.accounts WHERE discordid=%s)", (sender,))
    if c.fetchone():
        c.execute("SELECT username FROM accounts WHERE discordid=%s", (sender,))
        username=c.fetchone()
        await message.channel.send("Username: "+str(username[0]))
        print("user found")
    else: 
        c.execute("INSERT INTO cwiki_schema.accounts (discordid, username) VALUES (%s, %s)", (sender, user))
        conn.commit()
        print("user not found")

    #find user id and word id
    c.execute("SELECT userid FROM cwiki_schema.accounts WHERE discordid=%s", (sender,))
    temp=c.fetchone()
    userid= int(temp[0])
    print(userid)
    c.execute("SELECT wordid FROM cwiki_schema.words WHERE wordname=%s", (word,))
    temp=c.fetchone()
    wordid=int(temp[0])
    print(wordid)

    #add definition
    today = date.today()
    print(today)

    c.execute("INSERT INTO cwiki_schema.definitions (wordid, definition, userid, date) VALUES (%s, %s, %s, %s)", (wordid, definition, userid, today))
    conn.commit()

@bot.hybrid_command(name="define", description="get a term's deininition")
async def define(message, word: str = "term", member:discord.Member = None):
    server = str(message.guild.id)
    c.execute("SELECT wordid FROM words WHERE wordname=%s AND serverid=%s", (word,server,))
    
    temp = c.fetchone()
    if temp:
        wordid = int(temp[0])
        print(wordid)
        c.execute("SELECT definitionid FROM definitions WHERE wordid=%s", (wordid))
        temp = c.fetchone()
        if temp:
            i = 0
            for x in temp:
                definitionid=int(temp[0])
                i += 1
                c.execute("SELECT date FROM definitions WHERE definitionid=%s", (definitionid))
                temp1 = c.fetchone()
                date = int(temp1[0])
                embed = discord.Embed(title=word, description=date, color=discord.Color.random())
                c.execute("SELECT userid FROM definitions WHERE definitionid=%s", (definitionid))
                temp1 = c.fetchone()
                userid = int(temp1[0])
                member = message.server.get_member(id)
                embed.set_author(name=member.display_name, icon_url=member.display_avatar)
                c.execute("SELECT definition FROM definitions WHERE definitionid=%s", (definitionid))
                temp1 = c.fetchone()
                definition = str(temp1[0])
                embed.add_field(name="Definition", value=definition)
                embed.set_footer(text=i+" out of "+temp.len()+" definitions")
                await message.send(embed=embed)
        else:
          await message.send("No result found!")    
    else:
        await message.send("No result found!")
                


        

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run("MTI1Mjk4MTE2NjE4MTcxMTg3NA.GplJmK.CAPGvqFNy1OlfgSMtWznlTsd_HOov-VWRJVlyI")