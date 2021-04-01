import logging
import os
import requests
import logging
import BostoBot.toolbox.SuperPy as IsPy
import BostoBot.model.Model as Model
from BostoBot.model.Model import BostoResult


class AdminModel(Model.Model):
    
    def __init__(self, client):
        super().__init__(client)
    
    @Model.BostoConnected
    def addBostoType(self, payload, value, **kwargs):
        name, code = payload.emoji.name, str(payload.emoji)
        kwargs['connection'].addBostoType(name, code, value)
        return
    
    
    @Model.BostoConnected
    def removeBostoType(self, payload, **kwargs):
        name = payload.emoji.name
        kwargs['connection'].removeBostoType(name)
        return kwargs['connection'].removeWalletType(name)

    def removeImage(self, name):
        path = "/usr/src/app/data/img/{}.png".format(name)
        logging.info("Attempting to remove {}".format(path))
        try:
            os.remove(path)
            return True
        except Exception as err:
            logging.error("Error while removing emoji image")
            logging.error(err)  # something wrong with url
            return False


    def retrieveImage(self, url, name):
        logging.info("Attempting to request url: {} for image".format(url))
        path = "/usr/src/app/data/img/{}.png".format(name)
        try:
            req = requests.get(url)
            with open(path, 'wb') as outfile:
                outfile.write(req.content)
            return True
        except Exception as err:
            logging.error("Error while retrieving emoji image")
            logging.error(err)  # something wrong with url
            return False

