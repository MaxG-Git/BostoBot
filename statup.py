from discord.ext import commands
import BostoBot.toolbox.BostoGeneric as BostoGeneric
import BostoBot.toolbox.creds as creds
import os
import discord
import json  # -> Getting Credentials
import logging
logging.getLogger().setLevel(logging.INFO)



#import my_commands


class BostoHandler:
    def __init__(self, client, method='msg'):
        self.client = client

    async def Message(self, message, *args):
        pass

    async def Reaction(self, payload):
        pass
      # Note: This should be the controller in MVC!


def run(cogs):
    client = commands.Bot('b/')
    # On Bot Initiation
    ready_message = 'Meow from Bosto-Bot!.\nVersion 0.0.2'

    @client.event
    async def on_ready():
        logging.info(ready_message)
        from BostoBot.model.Model import Model
        Model.SetLocalPoints()
        client.BostoDict = dict(Model.GetDbPoints())
        await client.change_presence(activity=discord.Game(name="DM \"help\" for a list of commands"))
        

    # Load Cogs Command
    @client.command()
    @commands.is_owner()
    async def load(ctx, extension):
        if f'{extension.capitalize()}Controller.py' in os.listdir('./BostoBot/controller/cogs/'):
            client.load_extension(f'BostoBot.controller.cogs.{extension.capitalize()}Controller')
            await ctx.send(f'Cog {extension.capitalize()} Loaded!')
        else:
            await ctx.send(f'Cog {extension.capitalize()} Not Found!')

    # Un-Load Cogs Command

    @client.command()
    @commands.is_owner()
    async def unload(ctx, extension):
        if f'BostoBot.controller.cogs.{extension.capitalize()}Controller' in client.extensions:
            client.unload_extension(f'BostoBot.controller.cogs.{extension.capitalize()}Controller')
            await ctx.send(f'Successfully Unloaded Cog: {extension.capitalize()}')
        else:
            await ctx.send(f'Cog {extension.capitalize()} Not Found!')
    # Catch All Event Handler


    @client.event
    async def on_message(message, *args):
        if message.author.id == client.user.id:
            return  # Ignore self
        dm = not message.guild
        msgContent = tuple(message.content.split(' '))
        ctx = await client.get_context(message)

        if ctx.prefix == client.command_prefix:
            logging.info(message.author.name + "#" +
                         message.author.discriminator + " -> " + message.content)

        # Trigger commands in DM channel without prefix needed
        if dm:

            if ctx.prefix == None and msgContent[0].lower() in [str(i) for i in client.commands]:
                message.content = str(client.command_prefix) + str(message.content)
                logging.info(message.author.name + "#" +
                             message.author.discriminator + " -> " + message.content)
                await client.process_commands(message)
                #await ctx.invoke(client.get_command(message.content.lower()), *msgContent[1:])
                return
        # Send Message to automatic command sender
        await client.process_commands(message)


    # Auto Cog/Controller Loader
    for filename in cogs:
        if filename.endswith('Controller.py') and not filename.startswith("_"):
            logging.info(f"Loading Cog/Controller: " + filename)
            client.load_extension(f'BostoBot.controller.cogs.{filename[:-3]}')
    # Login at end of script
    client.run(creds.TOKEN)


COGS = os.listdir('./BostoBot/controller/cogs/')
run(COGS)

