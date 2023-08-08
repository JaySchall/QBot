import sys
import enum
from dotenv import set_key
import discord
import sqlite3
import os
from discord import app_commands
from dotenv import load_dotenv
import settings

con = sqlite3.connect("Queue.sqlite3")
cur = con.cursor()
embed = discord.Embed(title=settings.queueName)
embed.add_field(name="Users in Queue", value="1.")
embedMessages = {}
priority = []
queue = []
priorityUsers = []
queueEnabled = True
startSync = False

if len(sys.argv) > 1:
    if sys.argv[1] == "sync":
        startSync = True

class toggle(enum.Enum):
    enable = 1
    disable = 0

class JoinButton(discord.ui.View):
     def __init__(self, client):
         super().__init__()
         self.timeout=None
         self.client = client
     @discord.ui.button(label='Join Queue', style=discord.ButtonStyle.green)
     async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if queueEnabled == False:
             await interaction.response.send_message("Queue is currently closed, try again later", ephemeral=True)
             return
        user = interaction.user
        if user in queue:
            await interaction.response.send_message("You are already in queue", ephemeral=True)
            return
        guild = self.client.get_guild(settings.queueServer)
        roleUser = guild.get_member(user.id)
        for roleID in priority:
            if roleUser is not None and discord.utils.get(guild.roles, id=roleID) in roleUser.roles:
                priorityUsers.append(user)
        queue.append(user)
        print(f"{user.mention} joined queue")
        await updateEmbeds(self.client)
        await interaction.response.send_message("You have joined the queue", ephemeral=True)
         

     @discord.ui.button(label='Leave Queue', style=discord.ButtonStyle.green)
     async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user not in queue:
            await interaction.response.send_message("You already not in queue", ephemeral=True)
            return
        guild = self.client.get_guild(settings.queueServer)
        for roleID in priority:
            if discord.utils.get(guild.roles, id=roleID) in user.roles:
                priorityUsers.remove(user)
        queue.remove(user)
        print(f"{user.mention} left queue")
        await updateEmbeds(self.client)
        await interaction.response.send_message("You have left the queue", ephemeral=True)

async def updateEmbeds(client):
    embed.remove_field(index=0)
    s = ""
    i = 1
    for dude in queue:
        if dude in priorityUsers:
            s += str(i) + ". <:Shiny:1123782221778669629> " +  f"<@{dude.id}>" + "\n"
        else:
            s += str(i) + ". " +  f"<@{dude.id}>" + "\n"
        i+=1
    embed.add_field(name="Users in Queue", value=s)
    for id in embedMessages:
        channel = client.get_channel(id)
        msg = await channel.fetch_message(embedMessages[id])
        await msg.edit(embed=embed, view=JoinButton(client))
        print("an attempt")

async def onRaid(message, client):
    priorityPulled = 0
    s = message.content + "\n"
    for i in range(0, 3):
        if priorityPulled < settings.prioritySlots and len(priorityUsers) > 0:
            priorityPulled+=1
            guy = priorityUsers.pop(0)
            queue.remove(guy)
            await guy.send(message.content)
            print("Pulled From Priority")
        elif len(queue) > 0:
            guy = queue.pop(0)
            await guy.send(message.content)
            print("Pulled From Normal")
    await updateEmbeds(client)
        
def run_bot():
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    

    @client.event
    async def on_ready():
        print("Bot up and running")
        if startSync == True:
            synced = await tree.sync()
            print(f"Synced {len(synced)} commands")
        guild = client.get_guild(settings.queueServer)
        for entry in cur.execute("SELECT PrioID FROM Priority"):
            priority.append(entry[0])
            role = discord.utils.get(guild.roles, id=entry[0])
            print("Initiated role " + role.name + " with ID: " +  str(entry[0]) + " in priority queue")
        for entry in cur.execute("SELECT ChannelID, MessageID FROM Embeds"):
            embedMessages[entry[0]] = entry[1]
        await updateEmbeds(client)

    @tree.command(name="sync", description="sync commands")
    @app_commands.checks.has_permissions(administrator = True)
    async def sync(interaction: discord.Interaction):

        synced = await tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} commands")

    @tree.command(name="createembed", description="creates an embed used to join and leave the queue")
    @app_commands.checks.has_permissions(administrator = True)
    async def createembed(interaction: discord.Interaction):
        channel = interaction.channel
        if channel.id in embedMessages:
            await interaction.response.send_message(f"Channel already has an embed")
            return
        
        msg = await channel.send(embed=embed, view=JoinButton(client))
        embedMessages[channel.id] = msg.id
        cur.execute("INSERT INTO Embeds(ChannelID,MessageID) VALUES("+str(channel.id) + ","+ str(msg.id) + ")")
        con.commit()
        await interaction.response.send_message(f"Created embed")

    @tree.command(name="removeembed", description="deletes an embed used to join and leave the queue")
    @app_commands.checks.has_permissions(administrator = True)
    async def removeembed(interaction: discord.Interaction):
        channel = interaction.channel
        if channel.id not in embedMessages:
            await interaction.response.send_message(f"Channel doesn't have an embed")
            return
        msg = await channel.fetch_message(embedMessages[channel.id])
        await msg.delete()
        del embedMessages[channel.id]
        cur.execute("DELETE FROM Embeds WHERE ChannelID = "+str(channel.id))
        con.commit()
        await interaction.response.send_message(f"Removed embed")

    @tree.command(name="viewembeds", description="see where the embeds are located")
    @app_commands.checks.has_permissions(administrator = True)
    async def viewembeds(interaction: discord.Interaction):
        s = ""
        for id in embedMessages:
            channel = client.get_channel(id)
            msg = await channel.fetch_message(embedMessages[id])
            s+=channel.name+":\n" + msg.jump_url + "\n\n"
        await interaction.response.send_message(s)

    @tree.command(name="addpriority", description="adds a new priority role")
    @app_commands.checks.has_permissions(administrator = True)
    async def prioadd(interaction: discord.Interaction, number: str):
        if queueEnabled == True:
            await interaction.response.send_message("Queue must be disabled in order to change priority roles")
            return
        guild = client.get_guild(settings.queueServer)
        try:
            number = int(number)
            role = discord.utils.get(guild.roles, id=number)
            print(role.name)
        except:
            await interaction.response.send_message("invalid role id")
            return
        if number in priority:
            await interaction.response.send_message("role is already a priority role")
            return
        cur.execute("INSERT INTO Priority(PrioID) VALUES("+str(number)+ ")")
        con.commit()
        priority.append(number)
        await interaction.response.send_message(role.name + " added to priority roles")

    @tree.command(name="removepriority", description="removes a priority role")
    @app_commands.checks.has_permissions(administrator = True)
    async def prioremove(interaction: discord.Interaction, number: str):
        if queueEnabled == True:
            await interaction.response.send_message("Queue must be disabled in order to change priority roles")
            return
        guild = client.get_guild(settings.queueServer)
        try:
            number = int(number)
            role = discord.utils.get(guild.roles, id=number)
            print(role.name)
        except:
            await interaction.response.send_message("invalid role id")
            return
        if number not in priority:
            await interaction.response.send_message("role is not a priority role")
            return
        cur.execute("DELETE FROM Priority WHERE PrioID = "+str(number))
        con.commit()
        priority.remove(number)
        await interaction.response.send_message(role.name + " removed from priority roles")

    @tree.command(name="togglequeue", description="toggles the queue on or off")
    @app_commands.checks.has_permissions(administrator = True)
    async def togglequeue(interaction: discord.Interaction, toggle: toggle):
        global queueEnabled, queue, priorityUsers
        if toggle.value == 1:
            queueEnabled = True
            await interaction.response.send_message("enabled queue")
        elif toggle.value == 0:
            queue = []
            priorityUsers = []
            queueEnabled = False
            await updateEmbeds(client)
            await interaction.response.send_message("disabled queue")

    @tree.command(name="setqueuethumbnail", description="sets the queue thumbnail image using a url")
    @app_commands.checks.has_permissions(administrator = True)
    async def setthumbnail(interaction: discord.Interaction, thumbnail: str):
        embed.set_thumbnail(url=thumbnail)
        await updateEmbeds(client)
        await interaction.response.send_message("set thumbnail to " + thumbnail)
    @tree.command(name="setqueuechannel", description="changes queue channel to inputted one")
    @app_commands.checks.has_permissions(administrator = True)
    async def queuechannel(interaction: discord.Interaction, number: str):
        try:
            number = int(number)
            raidchannel = client.get_channel(number)
            print(raidchannel.name)
        except:
            await interaction.response.send_message("invalid raid channel id")
            return
        settings.queueChannel = number
        set_key(".env", 'QUEUE_CHANNEL', str(number))
        #os.environ['QUEUE_CHANNEL'] = str(number)
        await interaction.response.send_message("Changed raid channel to " + raidchannel.name)

    @tree.command(name="setloggingchannel", description="changes logging channel to inputted one")
    @app_commands.checks.has_permissions(administrator = True)
    async def loggingchannel(interaction: discord.Interaction, number: str):
        try:
            number = int(number)
            loggingchannel = client.get_channel(number)
            print(loggingchannel.name)
        except:
            await interaction.response.send_message("invalid logging channel id")
            return
        settings.loggingChannel = number
        set_key(".env", 'LOGGING_CHANNEL', str(number))
        await interaction.response.send_message("Changed logging channel to " + loggingchannel.name)

    @tree.command(name="setqueuename", description="changes queue name to inputted one")
    @app_commands.checks.has_permissions(administrator = True)
    async def queuename(interaction: discord.Interaction, name: str):
        embed.title = name
        set_key(".env", 'QUEUE_NAME', name)
        #os.environ['QUEUE_NAME'] = name
        await interaction.response.send_message("Changed queue title to " + name)
        await updateEmbeds(client)

    @tree.command(name="setraidtrigger", description="changes the keyword used to find raid codes")
    @app_commands.checks.has_permissions(administrator = True)
    async def raidtrigger(interaction: discord.Interaction, key: str):
        settings.raidString = key
        set_key(".env", 'RAID_CODE_IDENTIFIER', key)
        await interaction.response.send_message("Changed raid trigger to " + key)

    @tree.error
    async def on_app_command_error(interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(error)

    @client.event
    async def on_message(message):
        if client.get_channel(settings.queueChannel) == message.channel:
            print(message.content)
            if settings.raidString in message.content:
                await onRaid(message, client)
                print("HI OMG SOMETHING HAPPENED")

    client.run(settings.TOKEN)
if __name__ == "__main__":
    run_bot()