# QBot - Discord Queue Bot

Bot can be used to create multiple queues to send codes for Pokemon raids

## Setup

Requires Python 3 and a few libraries which can be installed using the following pip commands:

```sh
pip install -U discord.py
pip install python-dotenv
```

The .env file requires you to fill in three fields: the TOKEN of your discord bot, the ID of your server/guild, and the ID of the channel you want the queues to be in.

In the command line, enter the directory the queue bot files are located in, and type the following command:

```sh
python bot.py
```

For the first time running the bot, use the following instead:

```sh
python bot.py sync
```

This will run the queue bot.

## Commands

To check if the bot is online, type:

```sh
/ping
```

To sync up any new commands, type:

```sh
/sync
```

To add a queue for a channel, get the channel ID of the channel. Then go into the channel you want the queues to be in and type:

```sh
/addqueue number:channelID
```

where channelID is the ID number for the channel.

To remove a queue for a channel, get the channel ID of the channel. Then go into the channel you want the queues to be in and type:

```sh
/removequeue number:channelID
```

To add a priority role, get the role ID of the role. Then go into the channel you want the queues to be in and type:

```sh
/addpriority number:priorityID
```

where priorityID is the ID number for the role.

To remove a priority role, get the role ID of the role. Then go into the channel you want the queues to be in and type:

```sh
/removepriority number:priorityID
```

To see all of the commands, type:

```sh
/listqueues
```

To set a channel as the logging channel, type:

```sh
/setqueuelog number:channelID
```

this currently has to be done each time the bot resets.

To rename a queue, type:

```sh
/setqueuelog number:channelID title:channelName
```
