import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.toolbox.BostoGeneric import BostoResult


def BostoConnected(origin):
    def wrapper(*args, **kwargs):
        try:
            from BostoBot.model.connect.BostoConnect import BostoConnect
            import mysql.connector.errors
            connection = BostoConnect()
            connection.connect()
            kwargs['connection'] = connection
            return origin(*args, **kwargs)
        except mysql.connector.Error as err:
            logging.error("Error while connecting to Database")
            logging.error(str(err))
    return wrapper







class Model:
    def __init__(self, client):
        self.client = client
        try:
            from BostoBot.model.connect.BostoConnect import BostoConnect
            import mysql.connector.errors
            connection = BostoConnect()
            connection.connect()
            self.connection = connection
        except mysql.connector.Error as err:
            logging.error("Error while connecting to Database")
            logging.error(str(err))

    # Used Globally
    def ensureUser(self, user):
        userId = user.id
        userCheck = int(self.checkUser(user))
        if userCheck > 1:
             logging.error(f"User: {userId} detected duplicate registrations")
             return True
        elif userCheck < 1:
            try:
                self.addUser(user)
                return True
            except Exception as err:
                logging.error(f"Unable to add User: {userId}")
                logging.error(str(err))
                return False
        else:
            return True

    @staticmethod
    def getSettings(path = "/usr/src/app/data/settings.json"):
        import json
        with open(path) as f:
            settings = json.load(f)
        return settings

    
    @staticmethod
    def setSettings(settings, path = "/usr/src/app/data/settings.json"):
        import json
        with open(path, 'w') as outfile:
            json.dump(settings, outfile)
        return settings

    # Used Bot Initiation
    @staticmethod
    @BostoConnected
    def SetLocalPoints(**kwargs):
        import json
        import BostoBot.toolbox.SuperPy.iterable as IsPy
        allEmojis = {'points' : {key: {"code": code, "value": int(value)} for key, code, value in tuple(kwargs['connection'].getAllEmojis())}}
        settings = Model.getSettings()
        settings.update(allEmojis)
        Model.setSettings(settings)


    @staticmethod
    @BostoConnected
    def GetDbPoints(justNames = False, **kwargs):
        if justNames:
            return tuple(kwargs['connection'].GetPoints().keys())
        else:
            return kwargs['connection'].GetPoints()


    # Used Globally
    @BostoConnected
    def addUser(self, user, **kwargs):
        bot = "'{}'".format(str(user.bot).upper())
        nick = "'{}'".format(user.nick) if hasattr(user, 'nick') and user.nick != None else "NULL"
        name = "'{}'".format(user.name)
        kwargs['connection'].addUser(user.id, name, user.discriminator, bot, nick) 
        return self.addWallet(user)

    # Used Globally
    @BostoConnected
    def updateUser(self, user, **kwargs):
        bot = "'{}'".format(str(user.bot).upper())
        nick = "'{}'".format(user.nick) if hasattr(user, 'nick') and user.nick != None else "NULL"
        name = "'{}'".format(user.name)
        return kwargs['connection'].updateUser(user.id, name, user.discriminator, bot, nick)

   
    # Used Globally
    @BostoConnected
    def addWallet(self, user, **kwargs):
        kwargs['connection'].addWallet(user.id) 
        return True

    # Used Globally
    @BostoConnected
    def checkUser(self, user, **kwargs):
        return kwargs['connection'].checkUser(user.id)


    @BostoConnected
    def getValue(self, payload=None, emojiName=None, **kwargs):
        name = payload.emoji.name if emojiName == None else emojiName
        return kwargs['connection'].getEmojiValue(name)


    @BostoConnected
    def incrementWallet(self, reactionType, userId, cost, **kwargs):
        kwargs['connection'].incrementWallet(reactionType=reactionType, userId=userId, cost=cost)
        return

    @BostoConnected
    def decrementWallet(self, reactionType, userId, cost, **kwargs):
        kwargs['connection'].decrementWallet(reactionType=reactionType, userId=userId, cost=cost)
        return


    @BostoConnected
    def deleteReactionByMessageId(self, message=None, messageId=None, **kwargs):
        if messageId != None:
            kwargs['connection'].deleteReactionByMessageId(messageId)
        else:
            kwargs['connection'].deleteReactionByMessageId(message.id)

    @BostoConnected
    def countReactionByMessageId(self, message=None, messageId=None, **kwargs):
        if messageId != None:
            return kwargs['connection'].countReactionByMessageId(messageId)
        else:
            return kwargs['connection'].countReactionByMessageId(message.id)

    @BostoConnected
    def countPoints(self, user = None, userId = None, **kwargs):
        if userId != None:
            return kwargs['connection'].countPoints(userId)
        else:
            return kwargs['connection'].countPoints(user.id)

    @BostoConnected
    def getEmojiCode(self, name, **kwargs):
        return kwargs['connection'].getEmojiCode(name)

    @BostoConnected
    def getEmojiName(self, code, **kwargs):
        return kwargs['connection'].getEmojiName(code)

    @BostoConnected
    def isAdmin(self, user=None, userId=None, **kwargs):
        try:
            if userId != None:
                return kwargs['connection'].isAdmin(userId) == "TRUE"
            else:
                return kwargs['connection'].isAdmin(user.id) == "TRUE"
        except Exception:
                logging.error("Cannot verify user is admin when checking database")
                return False



 





