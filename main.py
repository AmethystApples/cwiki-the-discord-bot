import os
import mysql.connector
from dotenv import load_dotenv
from datetime import date

from transformers import BartTokenizer, BartForConditionalGeneration


tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')


load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

import discord
from discord.ext import commands 
from discord import app_commands

import defview

intents=discord.Intents.all()
intents.message_content = True
intents.messages = True
intents.members = True


bot = commands.Bot(command_prefix='/', intents = intents)



STARTUP_CHANNEL_ID = 1252983015169196177

conn = mysql.connector.connect(host="localhost",user="root", password="8o0k3d@ndW0ok3d",database="cwiki_schema")

c=conn.cursor(buffered=True)

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
async def entry(message, word: str = "", definition: str ="your entry"):
    if word=="":
        await message.reply("Please input a word.")
    else:
        await message.send("Entry added for "+word+" by "+message.author.name)
        server=str(message.guild.id)

        #add word
        #need to check if word already exists in server

        c.execute("SELECT wordid FROM words WHERE wordname=%s AND serverid=%s", (word,server,))
        temp = c.fetchone()
        if not temp:
            c.execute("INSERT INTO cwiki_schema.words (serverid, wordname) VALUES (%s, %s)", (server, word))
            conn.commit()


        #add user
        sender=str(message.author.id)
        user=str(message.author.name)
        c.execute("SELECT discordid FROM cwiki_schema.accounts WHERE EXISTS(SELECT * FROM cwiki_schema.accounts WHERE discordid=%s)", (sender,))
        if c.fetchone():
            c.execute("SELECT username FROM accounts WHERE discordid=%s", (sender,))
            username=c.fetchone()
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
        c.execute("SELECT wordid FROM cwiki_schema.words WHERE wordname=%s AND serverid=%s", (word, server))
        temp=c.fetchone()
        wordid=int(temp[0])
        print(wordid)

        #add definition
        today = date.today()
        print(today)

        c.execute("INSERT INTO cwiki_schema.definitions (wordid, definition, userid, date) VALUES (%s, %s, %s, %s)", (wordid, definition, userid, today))
        conn.commit()

bot.remove_command("help")
@bot.hybrid_command(name="help", description="C-wiki tutorial")        
async def helpmessage(message):
    print("hello")
    embed = discord.Embed(title="Help", description="C-wiki tutorial", color=discord.Color.blue())
    embed.add_field(name="/entry",value="Add an entry to C-wiki by entering the **word** you want to define, as well as its **definition**. \n\nFor example: /entry word:term definition:example",inline=True)
    embed.add_field(name="/define",value="See a list of definitions by entering the **word** you wish to see definitions of. You can also filter definitions by specifying the **member** who created them, or sort by the **best** wooked posts. \n\nFor example: /define word:term member:@Cwiki best:True",inline=True)
    embed.add_field(name="Wooks: 📈 and 📉",value="Users can vote on entries by accessing their defintions and clicking the 📈 and 📉 buttons to add or subtract 'wooks'.",inline=True)
    await message.reply(embed=embed)


def generate_summary(text):
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


@bot.hybrid_command(name="summarize", description="Summarize existing definitions")
async def summarize(message, word: str=""):
    if word=="":
        await message.reply("Please input a word.")
        run=False
    else:
        c.execute("SELECT wordid FROM words WHERE wordname=%s AND serverid=%s", (word, str(message.guild.id),))
        temp = c.fetchone()
        if temp:
            wordid = int(temp[0])
            c.execute("SELECT definitionid FROM definitions WHERE wordid=%s ORDER BY points DESC", (wordid,))
            #check how many defs
            temp = c.fetchall()
            if temp:
                if len(temp):
                    definitions= ""
                    for i in range(2):
                        definitions= definitions+"\n"+temp[i]
                    summary = generate_summary(definitions)

                    embed = discord.Embed(title="Help", description="C-wiki tutorial", color=discord.Color.blue())
                    embed.add_field(name="Summary",value=summary,inline=True)
                else:
                    await message.reply("This word does not have enough definitions.")

        else:
            await message.reply("That word has not been defined.")
            run = False 

    

@bot.hybrid_command(name="define", description="get a term's deininition")
async def define(message, word: str = "", member:discord.Member = None, best: bool = False):
    run: bool = True
    if word=="":
        await message.reply("Please input a word.")
        run=False
    else:
        c.execute("SELECT wordid FROM words WHERE wordname=%s AND serverid=%s", (word, str(message.guild.id),))
        temp = c.fetchone()
        if temp:
            if member != None:
                print("HELLO THANK YOU FOR INPUTTING A USER")
                wordid = int(temp[0])
                c.execute("SELECT userid FROM accounts WHERE discordid=%s", (member.id,))
                temp = c.fetchone()
                if temp:
                    userid = int(temp[0])
                    print(f"userid: {userid}")
                    c.execute("SELECT definitionid FROM definitions WHERE wordid=%s AND userid=%s", (wordid, userid))
                else: 
                    await message.send("No user has defined that word.")
                    run = False
        else:
            await message.reply("That word has not been defined.")
            run = False
    if run:
        definition_view = defview.DefView(timeout=None)
        word = word.upper()
        await definition_view.send(message, word, member, best)

bot.run(DISCORD_TOKEN)