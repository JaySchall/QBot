import discord
import sqlite3

con = sqlite3.connect("Queue.sqlite3")
cur = con.cursor()
queues = {}
embeds = {}
people = 3

embed = discord.Embed() 

class JoinButton(discord.ui.View):
     def __init__(self, id):
         super().__init__()
         self.id = id
         self.timeout=None
     @discord.ui.button(label='Join Queue', style=discord.ButtonStyle.green)
     async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
         if interaction.user in queues[self.id][1]:
             await interaction.response.edit_message(embed=embeds[self.id])
             return
         print("join button")
         s = ""
         queues[self.id][1].append(interaction.user)
         for dude in queues[self.id][1]:
            s += f"<@{dude.id}>" + "\n"
         embeds[self.id].remove_field(index=0)
         embeds[self.id].add_field(name="Users in Queue", value=s)

         await interaction.response.edit_message(embed=embeds[self.id])
     @discord.ui.button(label='Leave Queue', style=discord.ButtonStyle.green)
     async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
         if interaction.user not in queues[self.id][1]:
            await interaction.response.edit_message(embed=embeds[self.id])
            return
         print("leave button")
         s = ""
         queues[self.id][1].remove(interaction.user)
         for dude in queues[self.id][1]:
            s += f"<@{dude.id}>" + "\n"
         embeds[self.id].remove_field(index=0)
         embeds[self.id].add_field(name="Users in Queue", value=s)

         await interaction.response.edit_message(embed=embeds[self.id])

async def on_raid(message, queueID, channel):
    print(message.content)
    for i in range(0, people):
        if len(queues[queueID][1]) > 0:
            guy = queues[queueID][1].pop(0)
            await guy.send(message.content)
    s = ""
    for dude in queues[queueID][1]:
        print(f"<@{dude.id}>")
        s += f"<@{dude.id}>" + "\n"
    embeds[queueID].remove_field(index=0)
    embeds[queueID].add_field(name="Users in Queue", value=s)
            
    msg = await channel.fetch_message(queues[queueID][0])
    await msg.edit(embed=embeds[queueID])

def run_bot():
    TOKEN = ""
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    
    @client.event
    async def on_ready():
        channel = client.get_channel(1084204436466962472)
        print("up and running!")
        for entry in cur.execute("SELECT QID, MID FROM Queues"):
            queues[entry[0]] = []
            embeds[entry[0]] = discord.Embed(title="Queue " + str(entry[0]))
            embeds[entry[0]].add_field(name="Users in Queue", value="1.")
            queues[entry[0]].append(entry[1])
            queues[entry[0]].append([])
            msg = await channel.fetch_message(entry[1])
            await msg.edit(embed=embeds[entry[0]], view=JoinButton(entry[0]))
            print(entry[0])

    @client.event
    async def on_message(message):
    #create new queue
        #1084204436466962472
        #974890751920074772
        channel = client.get_channel(1084204436466962472)
        
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
                    
                    embeds[queue_ID] = discord.Embed(title="Queue " + str(queue_ID))
                    embeds[queue_ID].add_field(name="Users in Queue", value="1.")
                    msg = await channel.send(embed=embeds[queue_ID], view=JoinButton(queue_ID))
                    msg_id = msg.id
                    print(msg_id)
                except:
                    print("not a valid integer ID")
                if queue_ID not in queues and queue_ID != 0:
                    queues[queue_ID] = []
                    queues[queue_ID].append(msg.id)
                    queues[queue_ID].append([])
                    cur.execute("INSERT INTO Queues(QID,MID) VALUES("+str(queue_ID) + ","+ str(msg_id) + ")")
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
            s = ""
            for dude in queues[int(content[1])][1]:
                s += f"<@{dude.id}>" + "\n"
            embeds[int(content[1])].remove_field(index=0)
            embeds[int(content[1])].add_field(name="Users in Queue", value=s)
            
            msg = await channel.fetch_message(msg_id)
            await msg.edit(embed=embeds[int(content[1])])


        for queueID in queues:
            if client.get_channel(queueID) == message.channel:
                if "Raid Code" in message.content:
                    
                    await on_raid(message, queueID, channel)
                    
                return
    

    client.run(TOKEN)
run_bot()