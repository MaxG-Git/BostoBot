import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.toolbox.BostoGeneric import BostoResult, BostoResult
import BostoBot.model.Model as Model


class StatsModel(Model.Model):
    
    def __init__(self, client):
        super().__init__(client)
    
    @Model.BostoConnected
    def getPointTimeStatReceived(self, user, days, **kwargs):
        return kwargs['connection'].getPointTimeStatReceived(user.id, days)

    @Model.BostoConnected
    def getPointTimeStatGiven(self, user, days, **kwargs):
        return kwargs['connection'].getPointTimeStatGiven(user.id, days)

