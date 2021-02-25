
import json  # -> Getting Credentials
import discord
import os
#import my_commands
import BostoBot
import BostoBot.toolbox.creds as creds
from BostoBot.toolbox.BostoHandler import BostoHandler as BostoHandler
import logging
from discord.ext import commands
# Bot Prefix

client = commands.Bot('b/')
# On Bot Initiation

ready_message = 'Meow from Bosto-Bot!.\nVersion 0.0.1'


@client.event
async def on_ready():
  print(ready_message)
# Load Cogs Command


@client.command()
async def load(ctx, extension):
  import Points
  if not Points.isAdmin(ctx.message.author): return
  if f'{extension}.py' in os.listdir('./cogs'):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Cog {extension} Loaded!')
  else:
    await ctx.send(f'Cog {extension} Not Found!')
# Un-Load Cogs Command


@client.command()
async def unload(ctx, extension):
  import Points
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
for filename in BostoBot.COGS:
  if filename.endswith('.py') and not filename.startswith("_"):
    logging.info(f"Loading Cog: " + filename)
    client.load_extension(f'BostoBot.cogs.{filename[:-3]}')
# Login at end of script
client.run(creds.TOKEN)
