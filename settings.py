import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

queueServer = os.getenv('QUEUE_SERVER')
queueChannel = os.getenv('QUEUE_CHANNEL')
loggingChannel = os.getenv('LOGGING_CHANNEL')

raidString = os.getenv('RAID_CODE_IDENTIFIER')
queueName = ""
