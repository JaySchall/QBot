import sys
import discord
import sqlite3
import os
from discord import app_commands
from dotenv import load_dotenv
import settings

priority = []

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