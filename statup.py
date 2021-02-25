import logging
logging.getLogger().setLevel(logging.INFO)


import json  # -> Getting Credentials
import discord
import os


#import my_commands
import BostoBot.toolbox.creds as creds
import BostoBot.toolbox.BostoGeneric as BostoGeneric
import logging
from discord.ext import commands


class BostoHandler:
    def __init__(self, client, method='msg'):
        self.client = client

    async def Message(self, message, *args):
        dm = not message.guild
        msgContent = tuple(message.content.split(' '))
        ctx = await self.client.get_context(message)
        
        
        if ctx.prefix == self.client.command_prefix:
            logging.info(message.author.name + "#" + message.author.discriminator  + " -> " + message.content)


        # Trigger commands in DM channel without prefix needed
        if dm:
            
            if ctx.prefix == None and msgContent[0].lower() in [str(i) for i in self.client.commands]:
                logging.info(message.author.name + "#" + message.author.discriminator  + " -> " + message.content)
                await ctx.invoke(self.client.get_command(message.content), *msgContent[1:])
                return


        await self.client.process_commands(message) #Send Message to automatic command sender
        
        

    async def Reaction(self, payload):
        pass
      #Note: This should be the controller in MVC!


def run(cogs):
    client = commands.Bot('b/')
    # On Bot Initiation
    ready_message = 'Meow from Bosto-Bot!.\nVersion 0.0.1'


    @client.event
    async def on_ready():
        logging.info(ready_message)
    # Load Cogs Command


    @client.command()
    async def load(ctx, extension):
      import BostoBot.controller.Points as Points
      if not Points.isAdmin(ctx.message.author): return
      if f'{extension}.py' in os.listdir('./cogs'):
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'Cog {extension} Loaded!')
      else:
        await ctx.send(f'Cog {extension} Not Found!')
    # Un-Load Cogs Command


    @client.command()
    async def unload(ctx, extension):
      import BostoBot.controller.Points as Points
      if not Points.isAdmin(ctx.message.author): return
      if f'cogs.{extension}' in client.extensions:
        client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Successfully Unloaded Cog: {extension}')
      else:
        await ctx.send(f'Cog {extension} Not Found!')
    # Catch All Event Handler


    @client.event
    async def on_message(message, *args):
      if message.author.id == client.user.id: return # Ignore self
      event = BostoHandler(client)
      await event.Message(message, *args)


    # Auto Cog Loader
    for filename in cogs:
      if filename.endswith('.py') and not filename.startswith("_"):
        logging.info(f"Loading Cog: " + filename)
        client.load_extension(f'BostoBot.view.cogs.{filename[:-3]}')
    # Login at end of script
    client.run(creds.TOKEN)

COGS = os.listdir('./BostoBot/view/cogs/')
run(COGS)


