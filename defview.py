import discord
from discord.ext import commands 
from discord import app_commands
import mysql.connector


intents=discord.Intents.all()
intents.message_content = True
intents.messages = True
intents.members = True


bot = commands.Bot(command_prefix='/', intents = intents)



STARTUP_CHANNEL_ID = 1252983015169196177

conn = mysql.connector.connect(host="localhost",user="root", password="8o0k3d@ndW0ok3d",database="cwiki_schema")
c=conn.cursor(buffered=True)

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