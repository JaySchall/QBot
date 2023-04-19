import discord
import sqlite3
import os
from discord.ext import commands
from dotenv import load_dotenv
con = sqlite3.connect("Queue.sqlite3")
cur = con.cursor()
queues = {}
embeds = {}
priority = []
people = 3

load_dotenv()
embed = discord.Embed() 

async def updateEmbed(queueID, channel): 

    embeds[queueID].remove_field(index=0)
    embeds[queueID].remove_field(index=0)
    s = ""
    i = 1
    for dude in queues[queueID][1]:
        
        s += str(i) + ". " +  f"<@{dude.id}>" + "\n"
        i+=1
    embeds[queueID].add_field(name="Priority Users in Queue", value=s)
    s = ""
    i = 1
    for dude in queues[queueID][2]:
        
        s += str(i) + ". " +  f"<@{dude.id}>" + "\n"
        i+=1
    embeds[queueID].add_field(name="Normal Users in Queue", value=s)        
    msg = await channel.fetch_message(queues[queueID][0])
    await msg.edit(embed=embeds[queueID])
    



class JoinButton(discord.ui.View):
     def __init__(self, id, guild):
         super().__init__()
         self.id = id
         self.guild = guild
         self.timeout=None
     @discord.ui.button(label='Join Queue', style=discord.ButtonStyle.green)
     async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
         await interaction.response.edit_message(embed=embeds[self.id])
         user = interaction.user
         for queueID in queues:
            if user in queues[queueID][1] or user in queues[queueID][2]:
                #await interaction.response.defer()
                return
            
         raidchannel = self.guild.get_channel(self.id)
         for roleID in priority:
            if discord.utils.get(self.guild.roles, id=roleID) in user.roles:
                queues[self.id][1].append(user) 
                print(f"{user.mention} joined priority queue for " + raidchannel.name)
                await updateEmbed(self.id, interaction.channel)
                #await interaction.response.defer()
                return
         #await interaction.response.send_message(f"{user.mention} joined queue", allowed_mentions=False)
         queues[self.id][2].append(user)
         print(f"{user.mention} joined normal queue for " + raidchannel.name)
         await updateEmbed(self.id, interaction.channel)
         #await interaction.response.defer()

     @discord.ui.button(label='Leave Queue', style=discord.ButtonStyle.green)
     async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
         await interaction.response.edit_message(embed=embeds[self.id])
         user = interaction.user
         if user not in queues[self.id][1] and user not in queues[self.id][2]:
            #await interaction.response.defer()
            return
         raidchannel = self.guild.get_channel(self.id)
         for roleID in priority:
            if discord.utils.get(self.guild.roles, id=roleID) in user.roles:
                queues[self.id][1].remove(user)
                print(f"{user.mention} left priority queue for " + raidchannel.name)
                await updateEmbed(self.id, interaction.channel)
                #await interaction.response.defer()
                return
         #await interaction.response.send_message(f"{user.mention} left queue" , allowed_mentions=discord.AllowedMentions.all)
         queues[self.id][2].remove(user)
         print(f"{user.mention} left normal queue for " + raidchannel.name)
         await updateEmbed(self.id, interaction.channel)
        # await interaction.response.defer()

async def on_raid(message, queueID, channel):
    print(message.content)
    for i in range(0, people):
        if len(queues[queueID][1]) > 0:
            guy = queues[queueID][1].pop(0)
            await guy.send(message.content)
        elif len(queues[queueID][2]) > 0:
            guy = queues[queueID][2].pop(0)
            await guy.send(message.content)
    await updateEmbed(queueID, channel)

def run_bot():
    TOKEN = os.getenv('TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        channel = client.get_channel(1090735300298424410)
        guild = client.get_guild(1047657265517314108)
        
        print("up and running!")
        for entry in cur.execute("SELECT PrioID FROM Priority"):
            priority.append(entry[0])
            role = discord.utils.get(channel.guild.roles, id=entry[0])
            print("Initiated role " + role.name + " with ID: " +  str(entry[0]) + " in priority queue")
        for entry in cur.execute("SELECT QID, MID FROM Queues"):
            queues[entry[0]] = []
            raidchannel = client.get_channel(entry[0])
            embeds[entry[0]] = discord.Embed(title="Queue " + raidchannel.name)
            embeds[entry[0]].add_field(name="Priority Users in Queue", value="1.")
            embeds[entry[0]].add_field(name="Normal Users in Queue", value="1.")
            queues[entry[0]].append(entry[1])
            queues[entry[0]].append([])
            queues[entry[0]].append([])
            msg = await channel.fetch_message(entry[1])
            await msg.edit(embed=embeds[entry[0]], view=JoinButton(entry[0], guild))
            print("Initiated Queue " + raidchannel.name + " with ID: " + str(entry[0]))

    @client.event
    async def on_message(message):
    #create new queue
        #1084204436466962472
        #974890751920074772
        channel = client.get_channel(1090735300298424410)
        
        global msg_id
        global embed
        queue_ID = 0
        if message.channel == channel:
            content = message.content.split()
            if len(content) <= 0:
                return
            #adds new queue
            if content[0] == "add":
                try:
                    queue_ID = int(content[1])
                    guild = client.get_guild(1047657265517314108)
                    raidchannel = client.get_channel(queue_ID)
                    embeds[queue_ID] = discord.Embed(title="Queue " + raidchannel.name)
                    embeds[queue_ID].add_field(name="Priority Users in Queue", value="1.")
                    embeds[queue_ID].add_field(name="Normal Users in Queue", value="1.")
                    msg = await channel.send(embed=embeds[queue_ID], view=JoinButton(queue_ID, guild))
                    msg_id = msg.id
                    print(msg_id)
                except:
                    print("not a valid integer ID")
                    return
                if queue_ID not in queues and queue_ID != 0:
                    queues[queue_ID] = []
                    queues[queue_ID].append(msg.id)
                    queues[queue_ID].append([])
                    queues[queue_ID].append([])
                    cur.execute("INSERT INTO Queues(QID,MID) VALUES("+str(queue_ID) + ","+ str(msg_id) + ")")
                    con.commit()

                return
            elif content[0] == "priority" and int(content[1]) not in priority:
                roleID = int(content[1])
                priority.append(roleID)
                cur.execute("INSERT INTO Priority(PrioID) VALUES("+str(roleID)+ ")")
                con.commit()
                return
            
            elif content[0] == "join":
                if int(content[1]) in queues and message.author not in queues[int(content[1])]:
                    queues[int(content[1])][1].append(message.author)
                    
            elif content[0] == "leave":
                if int(content[1]) in queues and message.author in queues[int(content[1])]:
                    queues[int(content[1])][1].remove(message.author)
            else:
                return


        for queueID in queues:
            if client.get_channel(queueID) == message.channel:
                if "Raid Code" in message.content:
                    
                    await on_raid(message, queueID, channel)
                    
                return
    

    client.run(TOKEN)
run_bot()