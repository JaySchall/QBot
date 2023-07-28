import sys
import discord
import sqlite3
import os
from discord import app_commands
from dotenv import load_dotenv
import settings

embeds = {}
priority = []
queue = []
priorityUsers = []

async def onRaid(message):
    patreonsPulled = 0
    s = message.content + "\n"
    for i in range(0, 3):
        if patreonsPulled < patreonsPulled and len(priorityUsers) > 0:
            guy = priorityUsers.pop(0)
            queue.remove(guy)
            await guy.send(message.content)
        elif len(queue) > 0:
            guy = queue.pop(0)
            await guy.send(message.content)
        
def run_bot():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    client.run(settings.TOKEN)

    @tree.command(name="sync", description="sync commands")
    @app_commands.checks.has_permissions(administrator = True)
    async def sync(interaction: discord.Interaction):

        synced = await tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} commands")

    @tree.command(name="createEmbed", description="creates an embed used to join and leave the queue")
    @app_commands.checks.has_permissions(administrator = True)
    async def sync(interaction: discord.Interaction):
        channel = interaction.channel
        print()

    @tree.error
    async def on_app_command_error(interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(error)

    @client.event
    async def on_message(message):
        if client.get_channel(settings.queueChannel) == message.channel:
            if settings.raidString in message.content:
                print("")

if __name__ == "__main__":
    run_bot()