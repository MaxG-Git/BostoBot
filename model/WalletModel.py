import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.toolbox.BostoGeneric import BostoResult
import BostoBot.model.Model as Model

#!WalletModel used for wallet AND buy controllers
class WalletModel(Model.Model):
    
    def __init__(self, client):
        super().__init__(client)
 


    @Model.BostoConnected
    def getWallet(self, reactionType, user=None, userId=None, **kwargs):
        if userId == None:
            return kwargs['connection'].getWallet(reactionType, user.id)
        else:
            return kwargs['connection'].getWallet(reactionType, userId)


    @Model.BostoConnected
    def getTotalWallet(self, user=None, userId=None, convertToDict=False, **kwargs):
        if userId == None:
            result = kwargs['connection'].getTotalWallet(user.id)
        else:
            result = kwargs['connection'].getTotalWallet(userId)
        if convertToDict:
            return dict(zip(self.client.BostoDict.keys(), result))
        else:
            return result

    

        
    

