import discord
from discord.ext import commands
import logging
import BostoBot.controller.Controller as Controller
from BostoBot.model.StatsModel import StatsModel
import BostoBot.toolbox.SuperPy.iterable as IsPy
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from matplotlib.cbook import get_sample_data
import matplotlib.dates as dates
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import datetime

class StatsController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, StatsModel)

    @commands.command()
    @commands.dm_only()
    @commands.check(Controller.EnsureBostoUser)
    async def stats(self, ctx, *args):
        if ctx.guild is not None: return
        if not self.model.ensureUser(ctx.message.author): return
        imageRef = discord.File("/usr/src/app/data/plot.png")
        sep = any(arg.lower() == 'sep' for arg in args)
        days = IsPy.first(args, 7, lambda arg: arg.isdigit() and int(arg) < 32 and int(arg) > 4, int)
        emojiCode = self.client.BostoDict[tuple(self.client.BostoDict.keys())[0]]['code']
        user = ctx.author
        

        #Get Data
        received = {dates.date2num(datetime.datetime.now().date() - datetime.timedelta(i)):0 for i in range(days, 0, -1)}
        given = received.copy()

        listReplaceNone = lambda result: result if result != None else []
        received.update({dates.date2num(d):int(v) for d,v in listReplaceNone(self.model.getPointTimeStatReceived(user, days))})
        given.update({dates.date2num(d):int(v) for d,v in listReplaceNone(self.model.getPointTimeStatGiven(user, days))})

        y_received = list(received.values())
        x_received = list(received.keys())
        y_given = list(given.values())
        x_given = list(given.keys())


        if sep:
            fig, (ax1, ax2) = plt.subplots(2)
            axes = (ax1, ax2)
        else:
            ax = plt.subplot()
            fig = plt.gcf()
            axes = (ax,)
    
        fig.patch.set_facecolor('none')
        fig.patch.set_alpha(0)

        d_format = dates.DateFormatter('%m/%d')

        for a in axes:
            a.xaxis.set_major_formatter(d_format)
            a.yaxis.set_major_locator(MaxNLocator(integer=True))
            a.xaxis.set_major_formatter("%d")
            a.tick_params(colors='white')
            a.patch.set_facecolor('white')
            a.patch.set_alpha(1)

        if sep:
            ax1.plot(x_received, y_received)
            ax2.plot(x_given, y_given)
            ax1.set_title("Points Received", color="white")
            ax2.set_title("Points Given", color="white")

            for x0, y0 in received.items():
                ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/bostopoint.png'), 0.14/days), (x0, y0), frameon=False)
                ax1.add_artist(ab)

            for x0, y0 in given.items():
                ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/bostopoint.png'), 0.14/days), (x0, y0), frameon=False)
                ax2.add_artist(ab)
        else:
            ax.plot(x_received, y_received)
            ax.plot(x_given, y_given)
            plt.legend(['Points Received', 'Points Given'], loc='upper left')
            for x0, y0 in received.items():
                ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/bostopoint.png'), 0.14/days), (x0, y0), frameon=False)
                ax.add_artist(ab)

            for x0, y0 in given.items():
                ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/bostopoint.png'), 0.14/days), (x0, y0), frameon=False)
                ax.add_artist(ab)


        plt.tight_layout(pad=1.5)

        ticks = []
        for a in axes:
            ticks += a.xaxis.get_ticklabels() + a.yaxis.get_ticklabels()

        [t.set_color('white') for t in ticks]

        plt.savefig("/usr/src/app/data/plot.png", facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        await user.send(file=imageRef, content="Your {} statistics for the past {} days:".format(emojiCode, days))

        
        
    

def setup(client):
    client.add_cog(StatsController(client))