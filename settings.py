import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def token():
    return os.getenv('DISCORD_TOKEN')

def queueServer():
    return int(os.getenv('QUEUE_SERVER'))

def queueChannel():
    return int(os.getenv('QUEUE_CHANNEL'))

def loggingChannel():
    return int(os.getenv('LOGGING_CHANNEL'))

def raidString():
    return os.getenv('RAID_CODE_IDENTIFIER')

def prioritySlots():
    return int(os.getenv('PRIORITY_NUMBER'))

def queueName():
    return os.getenv('QUEUE_NAME')