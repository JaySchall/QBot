import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

queueServer = int(os.getenv('QUEUE_SERVER'))
queueChannel = int(os.getenv('QUEUE_CHANNEL'))
loggingChannel = int(os.getenv('LOGGING_CHANNEL'))

raidString = os.getenv('RAID_CODE_IDENTIFIER')
prioritySlots = int(os.getenv('PRIORITY_NUMBER'))
queueName = os.getenv('QUEUE_NAME')
def reload():
    queueServer = int(os.getenv('QUEUE_SERVER'))
    queueChannel = int(os.getenv('QUEUE_CHANNEL'))
    loggingChannel = int(os.getenv('LOGGING_CHANNEL'))

    raidString = os.getenv('RAID_CODE_IDENTIFIER')
    prioritySlots = int(os.getenv('PRIORITY_NUMBER'))
    queueName = os.getenv('QUEUE_NAME')

