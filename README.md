# QBot - Discord Queue Bot

Discord Bot used to manage queues for Pokemon Raids.

## Creating a Discord Bot

In order to run the program, you need to create a discord bot. This can be done at https://discord.com/developers/.

If you have not done this, you will need to:
1. Create an application
2. Add a bot to the application
3. Copy the bot token. We will need this later, keep it safe and private

You can now invite the bot into your main server and setup the required channels it will need.

## Setting up the Enviroment

At this point, you should download the repository on your device if you haven't already. All files are necessary except for the README.

In order to run the program, you need to have Python installed. The bot scripts are written in Python and require some additional libraries. If you wish to setup a virtual environment, you can.
Otherwise you can simply run the following command in a terminal in the directory where you downloaded the files:

```sh
pip install -r requirements.txt
```

This should install the required libraries

## Filling in the .env

Once you have a discord bot and everything installed, you need to fill out some information inside the .env file:
1. The discord bot's token
2. The ID of your main server
3. The ID where the raid code gets posted
4. The channel the bot will log information in

You can also change the string it checks for, how many priority members to pull, and the queue name.
