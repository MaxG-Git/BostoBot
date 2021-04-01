import logging
import os
import BostoBot.model.Model as Model
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from matplotlib.cbook import get_sample_data
import matplotlib.dates as dates
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.font_manager as font_manager
import asyncio
import BostoBot.creds as creds


class PointModel(Model.Model):
    
    def __init__(self, client):
        super().__init__(client)


    
    def GraphPoints(self, 
        path, 
        marker = lambda ax, textX, textY, name: ax.text(textX, textY, name),
        yPos = lambda yImage: yImage - 0.05,
        xPos = lambda yLength: 1 + (0.045/yLength),
        ):
        allEmojis = self.BostoPoints.copy()
        fig, ax = plt.subplots(figsize=(5, 10))
        ax.set_zorder(-1)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        y = {}
        index = 0
        for name in allEmojis.keys():
            y[name] = index
            index+=1
        x = [1] * len(y)
        ax.plot(x, y.values(), linestyle = 'None')
        zModifier = len(y) if len(y) > 2 else 3
        zoom = 4.6 / zModifier
        index = 0
        for name, order in y.items():
            textX = xPos(len(y))
            textY = yPos(order)
            imgX = 0.976
            imgY = order
            ab = AnnotationBbox(OffsetImage(plt.imread( '{}/img/{}.png'.format(creds.CONFIG['LOCAL_FILE_STORAGE'], name.lower())) , zoom), (imgX, imgY), frameon=False)
            ab.set_zorder(-1)
            ax.add_artist(ab)
            marker(ax, textX, textY, name)
            #ax.text(textX, textY, marker(name), **textOptions)

            path = '{}/wallet.png'.format(creds.CONFIG['LOCAL_FILE_STORAGE'])
        
        plt.axis('off')
        plt.savefig(path, transparent=True)
        plt.close()
        return True
        


    @Model.BostoConnected
    def getWallet(self, reactionType, user=None, userId=None, **kwargs):
        if userId == None:
            return kwargs['connection'].getWallet(reactionType, user.id, self.BostoList)
        else:
            return kwargs['connection'].getWallet(reactionType, userId, self.BostoList)

    '''DEPRICATED
    @Model.BostoConnected
    def getTotalWallet(self, user=None, userId=None, convertToDict=False, **kwargs):
        if userId == None:
            result = kwargs['connection'].getTotalWallet(user.id, self.BostoList)
        else:
            result = kwargs['connection'].getTotalWallet(userId, self.BostoList)
        if convertToDict:
            return dict(zip(self.BostoList, result))
        else:
            return result
    '''
    
    
    @Model.BostoConnected
    def getTotalWallet(self, user=None, userId=None, **kwargs):
        if userId == None:
            result = kwargs['connection'].getTotalWallet(user.id)
        else:
            result = kwargs['connection'].getTotalWallet(userId)
        return dict(result)
        
       
    

        
    

