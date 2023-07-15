import sys
import discord
import sqlite3
import os
from discord import app_commands
from dotenv import load_dotenv
con = sqlite3.connect("Queue.sqlite3")
cur = con.cursor()
queues = {}
embeds = {}
priority = []
people = 3
logging = 0
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
startSync = False
sillyMode = False

if len(sys.argv) > 1:
    if sys.argv[1] == "sync":
        startSync = True

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
                if logging != 0:
                    logchannel = self.guild.get_channel(logging)
                    await logchannel.send(f"{user.mention} joined priority queue for " + raidchannel.name, allowed_mentions = discord.AllowedMentions(users=False))
                await updateEmbed(self.id, interaction.channel)
                #await interaction.response.defer()
                return
         #await interaction.response.send_message(f"{user.mention} joined queue", allowed_mentions=False)
         queues[self.id][2].append(user)
         print(f"{user.mention} joined normal queue for " + raidchannel.name)
         if logging != 0:
            logchannel = self.guild.get_channel(logging)
            await logchannel.send(f"{user.mention} joined normal queue for " + raidchannel.name, allowed_mentions = discord.AllowedMentions(users=False))
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
                if logging != 0:
                    logchannel = self.guild.get_channel(logging)
                    await logchannel.send(f"{user.mention} left priority queue for " + raidchannel.name, allowed_mentions = discord.AllowedMentions(users=False))
                await updateEmbed(self.id, interaction.channel)
                #await interaction.response.defer()
                return
         #await interaction.response.send_message(f"{user.mention} left queue" , allowed_mentions=discord.AllowedMentions.all)
         queues[self.id][2].remove(user)
         print(f"{user.mention} left normal queue for " + raidchannel.name)
         if logging != 0:
            logchannel = self.guild.get_channel(logging)
            await logchannel.send(f"{user.mention} left normal queue for " + raidchannel.name, allowed_mentions = discord.AllowedMentions(users=False))
         await updateEmbed(self.id, interaction.channel)
        # await interaction.response.defer()

async def on_raid(message, queueID, channel, guild):
    s = message.content + "\n"
    
    print(message.content)
    for i in range(0, people):
        if len(queues[queueID][1]) > 0:
            guy = queues[queueID][1].pop(0)
            s+= str(i+1)+f". <@{guy.id}>" + "\n"
            await guy.send(message.content)
        elif len(queues[queueID][2]) > 0:
            guy = queues[queueID][2].pop(0)
            s+= str(i+1)+f". <@{guy.id}>" + "\n"
            await guy.send(message.content)
    if logging != 0:
        logchannel = guild.get_channel(logging)
        await logchannel.send(s, allowed_mentions = discord.AllowedMentions(users=False))
    await updateEmbed(queueID, channel)


def run_bot():
    TOKEN = os.getenv('TOKEN')

    
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    guild = client.get_guild(int(os.getenv('GUILD')))
    channel = client.get_channel(int(os.getenv('CHANNEL')))
    
    @tree.command(name="renamequeue", description="changes queue name")
    @app_commands.checks.has_permissions(administrator = True)
    async def renameq(interaction: discord.Interaction, number: str, title: str):
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        try:
            number = int(number)
            queuechannel = client.get_channel(number)
            print(queuechannel.name)
        except:
            await interaction.response.send_message("invalid channel id")
            return
        if number not in queues:
            await interaction.response.send_message("raid channel doesn't have a queue")
            return 
        embeds[number].title = title
        msg = await channel.fetch_message(queues[number][0])
        await msg.edit(embed=embeds[number])  
        await interaction.response.send_message(queuechannel.name + "queue is almost shown as " +title)
    @tree.command(name="setqueuelog", description="sets the channel for queue bot logging")
    @app_commands.checks.has_permissions(administrator = True)
    async def qlog(interaction: discord.Interaction, number: str):
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        try:
            number = int(number)
            queuechannel = client.get_channel(number)
            print(queuechannel.name)
        except:
            await interaction.response.send_message("invalid channel id")
            return
        global logging
        logging = number
        await interaction.response.send_message(queuechannel.name + " is now the logging channel")
    
    @tree.command(name="sync", description="sync commands")
    @app_commands.checks.has_permissions(administrator = True)
    async def sync(interaction: discord.Interaction):

        synced = await tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} commands")
    
    @tree.command(name="ping", description="testing")
    async def test(interaction: discord.Interaction): 
        await interaction.response.send_message("pong")

    

    @tree.command(name="listqueues", description="lists all queues")
    @app_commands.checks.has_permissions(administrator = True)
    async def queuelist(interaction: discord.Interaction):
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        s = ""
        for queue_ID in queues:
            raidchannel = client.get_channel(queue_ID)
            msg = await channel.fetch_message(queues[queue_ID][0])
            s+=raidchannel.name+":\n" + msg.jump_url + "\n\n"
        await interaction.response.send_message(s)

    @tree.command(name="addpriority", description="adds a new priority role")
    @app_commands.checks.has_permissions(administrator = True)
    async def prioadd(interaction: discord.Interaction, number: str):
        guild = client.get_guild(int(os.getenv('GUILD')))
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        try:
            number = int(number)
            role = discord.utils.get(channel.guild.roles, id=number)
            print(role.name)
        except:
            await interaction.response.send_message("invalid role id")
            return
        if number in priority:
            await interaction.response.send_message("role is already a priority role")
            return
        priority.append(number)
        cur.execute("INSERT INTO Priority(PrioID) VALUES("+str(number)+ ")")
        con.commit()
        await interaction.response.send_message(role.name + " added to priority roles")

    @tree.command(name="removepriority", description="removes a priority role")
    @app_commands.checks.has_permissions(administrator = True)
    async def prioremove(interaction: discord.Interaction, number: str):
        guild = client.get_guild(int(os.getenv('GUILD')))
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        try:
            number = int(number)
            role = discord.utils.get(channel.guild.roles, id=number)
            print(role.name)
        except:
            await interaction.response.send_message("invalid role id")
            return
        if number not in priority:
            await interaction.response.send_message("role is not a priority role")
            return
        priority.remove(number)
        cur.execute("DELETE FROM Priority WHERE PrioID = "+str(number))
        con.commit()
        await interaction.response.send_message(role.name + " removed from priority roles")

    @tree.command(name="addqueue", description="adds a queue")
    @app_commands.checks.has_permissions(administrator = True)
    async def queueadd(interaction: discord.Interaction, number: str):
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        guild = client.get_guild(int(os.getenv('GUILD')))
        try:
            queue_ID = int(number)
            
            raidchannel = client.get_channel(queue_ID)
            print(raidchannel.name)
        except:
            await interaction.response.send_message("invalid raid channel id")
            return
        if queue_ID in queues:
            await interaction.response.send_message("raid channel already has a queue")
            return
        embeds[queue_ID] = discord.Embed(title="Queue " + raidchannel.name)
        embeds[queue_ID].add_field(name="Priority Users in Queue", value="1.")
        embeds[queue_ID].add_field(name="Normal Users in Queue", value="1.")
        msg = await channel.send(embed=embeds[queue_ID], view=JoinButton(queue_ID, guild))
        msg_id = msg.id
        print(msg_id)    
        queues[queue_ID] = []
        queues[queue_ID].append(msg.id)
        queues[queue_ID].append([])
        queues[queue_ID].append([])
        queues[queue_ID].append(True)
        cur.execute("INSERT INTO Queues(QID,MID) VALUES("+str(queue_ID) + ","+ str(msg_id) + ")")
        con.commit()
        await interaction.response.send_message(raidchannel.name + " queue has been created")

    @tree.command(name="removequeue", description="removes a queue")
    @app_commands.checks.has_permissions(administrator = True)
    async def queueremove(interaction: discord.Interaction, number: str):
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        guild = client.get_guild(int(os.getenv('GUILD')))
        try:
            queue_ID = int(number)
            raidchannel = client.get_channel(queue_ID)
            print(raidchannel.name)
        except:
            await interaction.response.send_message("invalid raid channel id")
            return
        if queue_ID not in queues:
            await interaction.response.send_message("raid channel doesn't have a queue")
            return
        embeds.pop(queue_ID)
        msg = await channel.fetch_message(queues[queue_ID][0])
        await msg.delete()
        queues.pop(queue_ID)
        cur.execute("DELETE FROM Queues WHERE QID = "+str(queue_ID))
        con.commit()
        await interaction.response.send_message(raidchannel.name + " queue has been removed")
    @tree.command(name="setqueuethumbnail", description="sets the queue thumbnail image using a url")
    @app_commands.checks.has_permissions(administrator = True)
    async def setthumbnail(interaction: discord.Interaction, number: str, thumbnail: str):
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        guild = client.get_guild(int(os.getenv('GUILD')))
        try:
            queue_ID = int(number)
            raidchannel = client.get_channel(queue_ID)
            print(raidchannel.name)
        except:
            await interaction.response.send_message("invalid channel id")
            return
        if queue_ID not in queues:
            await interaction.response.send_message("channel doesn't have a queue")
            return
        embeds[queue_ID].set_thumbnail(url=thumbnail)
        msg = await channel.fetch_message(queues[queue_ID][0])
        await msg.edit(embed=embeds[queue_ID], view=JoinButton(queue_ID, guild))
        await interaction.response.send_message("Thumbnail has been changed for queue " + number)
    @tree.command(name="enablequeue", description="enable a disabled queue")
    @app_commands.checks.has_permissions(administrator = True)
    async def enable(interaction: discord.Interaction, number: str):
        try:
            queue_ID = int(number)
            raidchannel = client.get_channel(queue_ID)
            print(raidchannel.name)
        except:
            await interaction.response.send_message("invalid raid channel id")
            return
        if queue_ID not in queues:
            await interaction.response.send_message("raid channel doesn't have a queue")
            return
        if queues[queue_ID][3] == True:
            await interaction.response.send_message("queue is already active")
            return
        queues[queue_ID][3] = True
        await interaction.response.send_message("Queue enabled")
    @tree.command(name="disablequeue", description="disable a queue")
    @app_commands.checks.has_permissions(administrator = True)
    async def disable(interaction: discord.Interaction, number: str):
        try:
            queue_ID = int(number)
            raidchannel = client.get_channel(queue_ID)
            print(raidchannel.name)
        except:
            await interaction.response.send_message("invalid raid channel id")
            return
        if queue_ID not in queues:
            await interaction.response.send_message("raid channel doesn't have a queue")
            return
        if queues[queue_ID][3] == False:
            await interaction.response.send_message("queue is already disabled")
            return
        queues[queue_ID][3] = False
        await interaction.response.send_message("Queue disabled")
    @tree.error
    async def on_app_command_error(interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(error)
    @tree.command(name="sillytoggle", description="Toggles the sillies, obviously")
    @app_commands.checks.has_permissions(administrator = True)
    async def silly(interaction: discord.Interaction):
        global sillyMode
        if sillyMode == True:
            sillyMode = False
            await interaction.response.send_message("No more sillies :(", ephemeral=True)
        else:
            sillyMode = True
            await interaction.response.send_message("Silly time", ephemeral=True)

    @client.event
    async def on_ready():
        if startSync == True:
            synced = await tree.sync()
            print(f"Synced {len(synced)} commands")
        guild = client.get_guild(int(os.getenv('GUILD')))
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        print(guild.name)
        #synced = await tree.sync()
        #print(f"Synced {len(synced)} commands")
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
            queues[entry[0]].append(True)
            msg = await channel.fetch_message(entry[1])
            await msg.edit(embed=embeds[entry[0]], view=JoinButton(entry[0], guild))
            print("Initiated Queue " + raidchannel.name + " with ID: " + str(entry[0]))

    @client.event
    async def on_message(message):
        guild = client.get_guild(int(os.getenv('GUILD')))
        channel = client.get_channel(int(os.getenv('CHANNEL')))
        notify = client.get_channel(int(os.getenv('NOTIFICATION')))

        for queueID in queues:
            if client.get_channel(queueID) == message.channel:
                if "Raid Code" in message.content:
                    
                    await on_raid(message, queueID, channel, guild)
                    return
                elif "Preparing parameter for" in message.content:
                    await notify.send(message.content)
                    return


    client.run(TOKEN)
run_bot()