import discord
from discord.ext import commands
import numpy as np
import matplotlib.pyplot as plt


class TestCommands(commands.Cog) :
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
      await ctx.send(f'Meow! {round(self.client.latency * 1000)}ms') 

    @commands.command()
    async def logme(self, ctx, *args):
      log = {
        "Guild" : ctx.guild,
        "Channel" : ctx.channel,
        "User" : ctx.author,
        "Args" : args
      }
      await ctx.send('\n\n'.join("{!s}={!r}".format(key,val) for (key,val) in log.items()))
      

    @commands.command()
    async def test(self, ctx, *args):
      channel = self.client.get_channel(717429756831990102)
      await channel.send(args)

    @commands.command()
    async def listCommands(self, ctx, *args):
      helptext = "```"
      for command in self.client.commands:
        helptext+=f"{command}\n"
      helptext+="```"
      await ctx.send(helptext)

    @commands.command()
    async def plot_test(self, ctx, *args):
      x = args
      image = discord.File("/usr/src/app/data/plot.png")
      plt.bar(np.arange(len(x)), x)
      plt.savefig("/usr/src/app/data/plot.png")
      plt.close()
      await ctx.send(file=image)
      


    

def setup(client):
    client.add_cog(TestCommands(client))
