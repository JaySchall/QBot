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

if __name__ == "__main__":
    run_bot()