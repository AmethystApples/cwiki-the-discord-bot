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
    embed = discord.Embed(title="Help", description="C-wiki tutorial", color=discord.Color.random())
    embed.add_field(name="/entry",value="Add an entry to C-wiki by entering the **word** you want to define, as well as its **definition**. \n\nFor example: /entry word:term definition:example",inline=True)
    embed.add_field(name="/define",value="See a list of definitions by entering the **word** you wish to see definitions of. You can also filter definitions by specifying the **member** who created them. \n\nFor example: /define word:term member:@Cwiki",inline=True)
    embed.add_field(name="Wooks: 📈 and 📉",value="Users can vote on entries by accessing their defintions and clicking the 📈 and 📉 buttons to add or subtract 'wooks'.",inline=True)
    await message.reply(embed=embed)

class DefView(discord.ui.View):
    current: int = 0
    max: int = 1
    word: str = "term"
    member: discord.Member = None
    server: str = ""
    current_definition: str = ""
    best: bool = False


    async def send(self, message, word: str = "term", member: discord.Member = None, best: bool = False):
        self.word = word
        self.member = member
        self.server = str(message.guild.id)
        self.best = best
        print(self.word)
        print(self.server)
        c.execute("SELECT wordid FROM words WHERE wordname=%s AND serverid=%s", (self.word,self.server,))
        temp = c.fetchone()
        if temp:
            if self.member != None:
                print("HELLO THANK YOU FOR INPUTTING A USER")
                wordid = int(temp[0])
                c.execute("SELECT userid FROM accounts WHERE discordid=%s", (self.member.id,))
                temp = c.fetchone()
                if temp:
                    userid = int(temp[0])
                    print(f"userid: {userid}")
                    c.execute("SELECT definitionid FROM definitions WHERE wordid=%s AND userid=%s", (wordid, userid))
            else:
                print("no user inputted")
                wordid = int(temp[0])
                c.execute("SELECT definitionid FROM definitions WHERE wordid=%s", (wordid,))
    
            temp = c.fetchall()
            if temp:
                self.max = len(temp)
                print(self.max)
            else:
                print("[in send] wasn't able to fetch list of definitions")
        else:
            print("[in send] wasn't able to get words")
        print(self.max)

        self.message = await message.send(view = self)
        await self.update_page()
        
        
    
    def create_page(self):
        colors = [discord.Colour.green(), discord.Colour.yellow(), discord.Colour.orange(), discord.Colour.red(), discord.Colour.purple()]
        thresholds = [5, 15, 30, 50, 100]
        
        c.execute("SELECT wordid FROM words WHERE wordname=%s AND serverid=%s", (self.word,self.server,))
    
        temp = c.fetchone()
        if temp:
            print(self.current)
            wordid = int(temp[0])
            print(wordid)
            if self.member != None:
                print("HELLO THANK YOU FOR INPUTTING A USER")
                wordid = int(temp[0])
                c.execute("SELECT userid FROM accounts WHERE discordid=%s", (self.member.id,))
                temp = c.fetchone()
                if temp:
                    userid = int(temp[0])
                    print(f"userid: {userid}")
                    if self.best:
                        c.execute("SELECT definitionid FROM definitions WHERE wordid=%s AND userid=%s ORDER BY points DESC", (wordid, userid))
                    else:
                        c.execute("SELECT definitionid FROM definitions WHERE wordid=%s AND userid=%s", (wordid, userid))

                else: 
                    print ("no user found")#add something here later

            else:
                print("no user inputted")
                wordid = int(temp[0])
                if self.best:
                    c.execute("SELECT definitionid FROM definitions WHERE wordid=%s ORDER BY points DESC", (wordid,))
                else:
                    c.execute("SELECT definitionid FROM definitions WHERE wordid=%s", (wordid,))

            temp = c.fetchall()

            if temp:
                self.current_definition=int(temp[self.current][0])
                c.execute("SELECT date FROM definitions WHERE definitionid=%s", (self.current_definition,))
                temp1 = c.fetchone()
                date = str(temp1[0])
                c.execute("SELECT points FROM definitions WHERE definitionid=%s", (self.current_definition,))
                temp1 = c.fetchone()
                points = int(temp1[0])
                embed_color = discord.Color.blurple()
                i = 4
                while i > -1:
                    if points >= thresholds[i]:
                        embed_color = colors[i]
                        i = 0
                    i -= 1
                embed = discord.Embed(title=self.word, description=date, color=embed_color)
                c.execute("SELECT userid FROM definitions WHERE definitionid=%s", (self.current_definition,))
                temp1 = c.fetchone()
                userid = int(temp1[0])
                c.execute("SELECT discordid FROM accounts WHERE userid=%s", (userid,))
                temp1 = c.fetchone()
                discordid = int(temp1[0])
                member = self.message.guild.get_member(discordid)
                embed.set_author(name=member.display_name, icon_url=member.display_avatar)
                c.execute("SELECT definition FROM definitions WHERE definitionid=%s", (self.current_definition,))
                temp1 = c.fetchone()
                definition = str(temp1[0])

                embed.add_field(name=f"Entry: {points} Wooks", value=definition)
                embed.set_footer(text=f"{self.current+1} out of {len(temp)} definitions")
                return embed
            else:
                print("[in create] wasn't able to fetch list of definitions")
        else:
            print("[in create] wasn't able to get words")

    async def update_page(self):
        await self.message.edit(embed = self.create_page(), view = self)


    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current -= 1
        if self.current < 0:
            self.current = self.max - 1
        await self.update_page()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current += 1
        if self.current >= self.max:
            self.current = 0
        await self.update_page()

    @discord.ui.button(label="📈", style=discord.ButtonStyle.blurple)
    async def wook_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        c.execute("SELECT points FROM definitions WHERE definitionid=%s", (self.current_definition,))
        temp1 = c.fetchone()
        points = int(temp1[0])

        c.execute("SELECT wook from wooks WHERE definitionid=%s AND discordid=%s", (self.current_definition,interaction.user.id,))
        temp = c.fetchone()
        if temp:
            if int(temp[0]) == -1:
                points += 2
                c.execute("UPDATE wooks SET wook = %s WHERE definitionid = %s AND discordid=%s", (1, self.current_definition,interaction.user.id,))
                conn.commit()
            if int(temp[0]) == 1:
                points -= 1
                c.execute("DELETE FROM wooks WHERE definitionid=%s AND discordid=%s", (self.current_definition,interaction.user.id,))
                conn.commit()
        else:
            points += 1
            c.execute("INSERT INTO wooks (definitionid, discordid, wook) VALUES (%s, %s, %s)", (self.current_definition, interaction.user.id, 1))
            conn.commit()

        c.execute("UPDATE definitions SET points = %s WHERE definitionid=%s", (points, self.current_definition))
        conn.commit()
        await self.update_page()

    @discord.ui.button(label="📉", style=discord.ButtonStyle.blurple)
    async def book_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        c.execute("SELECT points FROM definitions WHERE definitionid=%s", (self.current_definition,))
        temp1 = c.fetchone()
        points = int(temp1[0])

        c.execute("SELECT wook from wooks WHERE definitionid=%s AND discordid=%s", (self.current_definition,interaction.user.id,))
        temp = c.fetchone()
        if temp:
            if int(temp[0]) == 1:
                points -= 2
                c.execute("UPDATE wooks SET wook = %s WHERE definitionid = %s AND discordid=%s", (-1, self.current_definition,interaction.user.id,))
                conn.commit()
            if int(temp[0]) == -1:
                points += 1
                c.execute("DELETE FROM wooks WHERE definitionid=%s AND discordid=%s", (self.current_definition,interaction.user.id,))
                conn.commit()
        else:
            points -= 1
            c.execute("INSERT INTO wooks (definitionid, discordid, wook) VALUES (%s, %s, %s)", (self.current_definition, interaction.user.id, -1))
            conn.commit()

        c.execute("UPDATE definitions SET points = %s WHERE definitionid=%s", (points, self.current_definition))
        conn.commit()
        await self.update_page()

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
        definition_view = DefView(timeout=None)
        word = word.upper()
        await definition_view.send(message, word, member, best)
    
                


        

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run("MTI1Mjk4MTE2NjE4MTcxMTg3NA.GplJmK.CAPGvqFNy1OlfgSMtWznlTsd_HOov-VWRJVlyI")