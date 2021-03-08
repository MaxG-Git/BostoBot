import logging
import os
import BostoBot.model.Model as Model


class SettingsModel(Model.Model):
    
    def __init__(self, client):
        super().__init__(client)#(self, setting, value, userId)
    
    @Model.BostoConnected
    def changeUserSetting(self, setting, value, user, **kwargs):
        return kwargs['connection'].changeUserSetting(setting, value, user.id)

    @Model.BostoConnected
    def getUserSettings(self, user=None, userId=None, **kwargs):
        if userId != None:
            return kwargs['connection'].getUserSettings(userId) 
        else:
            return kwargs['connection'].getUserSettings(user.id)