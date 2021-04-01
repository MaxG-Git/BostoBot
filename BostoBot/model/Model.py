import logging
import os
from BostoBot.model.connect.BostoConnect import BostoConnect
import mysql.connector.errors

def BostoConnected(origin):
    """Database Injector
    This decorator function will inject an intstantiated BostoBot.model.connect.BostoConnect object into
    a function's parameters to be used as a database connection. This method of parameter injection is designed
    to allow the easy use of BostoConnect objects within a function without attaching the BostoConnect object to
    a controller. This is done because after a controller is instantiated it remains in active memory to be used again. 
    By passing in the BostoConnect object as a parameter we can ensure that the Database connection in the BostoConnect object
    is terminated when the we have completed our Controller's action.

    Arguments:
        origin {Callable} -- Function to inject
    """
    def wrapper(*args, **kwargs):
        try:
            from BostoBot.model.connect.BostoConnect import BostoConnect
            import mysql.connector.errors
            connection = BostoConnect()
            connection.connect()
            kwargs['connection'] = connection
            return origin(*args, **kwargs)
        except mysql.connector.Error as err:
            logging.error("Mysql Error: (un-caught)")
            logging.error(str(err))
    return wrapper



class Model:
    def __init__(self, client):
        self.client = client
        self.resetInstance()
        
    def resetInstance(self):
        self.BostoPoints = dict(self.GetLocalPoints())
        self.BostoList = tuple(self.BostoPoints.keys())
        self.BostoBase = self.BostoPoints[self.BostoList[0]] if len(self.BostoList) > 0 else None
    

    def ensureBostoBase(self):
        return self.BostoBase != None
        
    # Used Globally
    def ensureUser(self, user):
        userId = user.id
        userCheck = int(self.checkUser(user))
        
        if userCheck > 1:
             logging.error(f"User: {userId} detected duplicate registrations")
        elif userCheck < 1:
            try:
                self.addUser(user) # Adds User, User's Wallet, And User's Settings
            except Exception as err:
                logging.error(f"Unable to add User: {userId}")
                logging.error(str(err))
                return False
        
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

    @staticmethod
    def GetLocalPoints(path = "/usr/src/app/data/settings.json"):
        return Model.getSettings(path)['points']

    @staticmethod
    def getLocalUserSettings(path = "/usr/src/app/data/settings.json"):
        return Model.getSettings(path)['userSettings']

    @staticmethod
    def getLocalHelp(path = "/usr/src/app/data/settings.json"):
        return Model.getSettings(path)['help']

    @staticmethod
    def getLocalTips(path = "/usr/src/app/data/settings.json"):
        return Model.getSettings(path)['tips']



    # Used Bot Initiation
    @staticmethod
    @BostoConnected
    def SetLocalPoints(**kwargs):
        import BostoBot.toolbox.SuperPy.iterable as IsPy
        allEmojis = {'points' : {key: {"code": code, "value": int(value), "name":key} for key, code, value in tuple(kwargs['connection'].getAllEmojis())}}
        settings = Model.getSettings()
        settings.update(allEmojis)
        Model.setSettings(settings)

    # Used Bot Initiation and Globally
    @BostoConnected
    def SyncDBWallets(self, **kwargs):
        for reactionType in self.BostoList:
            kwargs['connection'].syncWalletType(reactionType)


    
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
        bot = "{}".format(str(user.bot).upper())
        nick = "{}".format(user.nick) if hasattr(user, 'nick') and user.nick != None else None
        name = "{}".format(user.name)
        kwargs['connection'].addUser(user.id, name, user.discriminator, bot, nick)
        self.SyncDBWallets()
        return 

    # Used Globally
    @BostoConnected
    def updateUser(self, user, **kwargs):
        bot = "'{}'".format(str(user.bot).upper())
        nick = "'{}'".format(user.nick) if hasattr(user, 'nick') and user.nick != None else "NULL"
        name = "'{}'".format(user.name)
        return kwargs['connection'].updateUser(user.id, name, user.discriminator, bot, nick)

    # Used Globally
    @BostoConnected
    def syncWalletType(self, reactionType, **kwargs):
        return kwargs['connection'].syncWalletType(reactionType)



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
        kwargs['connection'].incrementWallet(reactionType=reactionType, userId=userId, BostoList=self.BostoList, cost=cost)
        return

    @BostoConnected
    def decrementWallet(self, reactionType, userId, cost, **kwargs):
        kwargs['connection'].decrementWallet(reactionType=reactionType, userId=userId, BostoList=self.BostoList, cost=cost)
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

    def addTip(self, user=None, origin="", exclude_list=(), require_list=None, userId=None, blank_is_none=True):
        try:
            if self.getSpecificUserSettings('tool_tips', user=user, userId=userId) != "TRUE": return origin if origin != "" and blank_is_none else None
            import random
            tipsDict = self.getLocalTips()
            if require_list == None:
                if len(exclude_list) > 0:
                    tipsDict = dict(filter(lambda value: any(string not in value[0]  for string in exclude_list), tipsDict.items()))
            else:
                tipsDict = dict(filter(lambda value: any(string in value[0] for string in require_list), tipsDict.items()))
            
            return origin + "ℹ\n*" + random.choice(list(tipsDict.values())) +"*"

        except Exception as err:
            logging.info(err)
            return origin if origin != "" and blank_is_none else None
        


    @BostoConnected
    def getSpecificUserSettings(self, setting, user=None, userId=None, **kwargs):
        if userId != None:
            return kwargs['connection'].getSpecificUserSettings(setting, userId)
        else:
            return kwargs['connection'].getSpecificUserSettings(setting, user.id)

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

class BostoResult:
    def __init__(self, result:bool, reason:str = None, error=None, **kwargs):
        self.result = result
        self.reason = reason
        self.error = error


 





