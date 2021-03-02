import discord
from discord.ext import commands
import logging
import BostoBot.controller.Controller as Controller
from BostoBot.model.WalletModel import WalletModel
import BostoBot.toolbox.SuperPy.iterable as IsPy
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from matplotlib.cbook import get_sample_data
import matplotlib.dates as dates
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.font_manager as font_manager
import asyncio

class WalletController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, WalletModel)

    
    @commands.command()
    @commands.dm_only()
    @commands.check(Controller.EnsureBostoUser)
    async def wallet(self, ctx, *args):
        user = ctx.message.author
        path = "/usr/src/app/data/wallet.png"
        image = discord.File(path)
        totalWallet = self.model.getTotalWallet(user=user, convertToDict=True)
       
        allEmojis = self.client.BostoDict
        fig, ax = plt.subplots(figsize=(5, 10))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        y = {}
        index = 0
        for name in allEmojis.keys():
            y[name] = index
            index+=1
        x = [1] * len(y)
        ax.plot(x, y.values(), linestyle = 'None')
        zoom = 0.6 / len(y)
        prop = font_manager.FontProperties(fname="/usr/src/app/data/uni-sans.heavy-caps.ttf")
        for name, order in y.items():
            ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/{}.png'.format(name.lower())), zoom), (0.970, order), frameon=False)
            ax.add_artist(ab)
            ax.text(1 + (0.045/len(y)), order - 0.05, "× " + str(totalWallet[name.lower()]), fontsize=40, fontproperties=prop, color="white")
        
        plt.axis('off')
        plt.savefig(path, transparent=True)
        plt.close()
        try:
            
            await user.send(file=image, content="Your current wallet:")
        except Exception as err:
            logging.error("Error while creating/saving wallet graphic")
            logging.error(str(err))
            await user.send(content="Somethings gone wrong") #TODO BETTER MESSAGE
        return ctx




def setup(client):
    client.add_cog(WalletController(client))