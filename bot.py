import sys
import discord
import sqlite3
import os
from discord import app_commands
from dotenv import load_dotenv
import settings

embed = discord.Embed(title="Queue")
embed.add_field(name="Users in Queue", value="1.")
embedMessages = {}
priority = []
queue = []
priorityUsers = []

class JoinButton(discord.ui.View):
     def __init__(self, client):
         super().__init__()
         self.timeout=None
         self.client = client
     @discord.ui.button(label='Join Queue', style=discord.ButtonStyle.green)
     async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user in queue:
            await interaction.response.send_message("You are already in queue", ephemeral=True)
            return
        guild = self.client.get_guild(settings.queueServer)
        for roleID in priority:
            if discord.utils.get(guild.roles, id=roleID) in user.roles:
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
        await msg.edit(embed=embed)
        print("an attempt")

async def onRaid(message, client):
    priorityPulled = 0
    s = message.content + "\n"
    for i in range(0, 3):
        if priorityPulled < settings.prioritySlots and len(priorityUsers) > 0:
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
        print("HAIII")
        #synced = await tree.sync()
        #print(f"Synced {len(synced)} commands")

    @tree.command(name="sync", description="sync commands")
    @app_commands.checks.has_permissions(administrator = True)
    async def sync(interaction: discord.Interaction):

        synced = await tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} commands")

    @tree.command(name="createembed", description="creates an embed used to join and leave the queue")
    @app_commands.checks.has_permissions(administrator = True)
    async def sync(interaction: discord.Interaction):
        channel = interaction.channel
        if channel in embedMessages:
            await interaction.response.send_message(f"Channel already has an embed")
            return
        msg = await channel.send(embed=embed, view=JoinButton(client))
        embedMessages[channel.id] = msg.id
        await interaction.response.send_message(f"Created embed")

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
        priority.append(number)
        await interaction.response.send_message(role.name + " added to priority roles")

    @tree.command(name="removepriority", description="removes a priority role")
    @app_commands.checks.has_permissions(administrator = True)
    async def prioremove(interaction: discord.Interaction, number: str):
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
        priority.remove(number)
        await interaction.response.send_message(role.name + " removed from priority roles")

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