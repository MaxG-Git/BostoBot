import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.toolbox.BostoGeneric import BostoResult

def BostoConnected(origin):
    def wrapper(*args, **kwargs):
        try:
            from BostoBot.model.BostoConnect import BostoConnect
            import mysql.connector.errors
            connection = BostoConnect()
            connection.connect()
            kwargs['connection'] = connection
            return origin(*args, **kwargs)
        except mysql.connector.Error as err:
            logging.error("Error while connecting to Database")
            logging.error(str(err))
    return wrapper



def ensureUser(user):
    userId = user.id
    userCheck = int(checkUser(user))
    if userCheck > 1:
         logging.error(f"User: {userId} detected duplicate registrations")
         return True
    elif userCheck < 1:
        try:
            addUser(user)
            return True
        except Exception as err:
            logging.error(f"Unable to add User: {userId}")
            logging.error(str(err))
            return False
    else:
        return True


@BostoConnected
def addReaction(message, payload, value, **kwargs) -> BostoResult:
    author, reacter, emojiName = message.author, payload.member, payload.emoji.name
    if not ensureUser(author) or not ensureUser(reacter): return BostoResult(False, "user")
    
    updateUser(reacter)

    if value > 1 and not hasFunds(payload, 1):
        return BostoResult(False, "funds")

    kwargs['connection'].addReaction(authorId=author.id, reacterId=reacter.id, messageId=message.id, emojiType=emojiName)
    return BostoResult(True)

@BostoConnected
def getWalletValue(user, **kwargs):
    wallet = getTotalWallet(user)
    return sum(wallet)



@BostoConnected
def removeReaction(pointId, message, payload, **kwargs) -> BostoResult:
    if(pointId is None):
         return BostoResult(False, "untracked")
    else:
        kwargs['connection'].removePoint(pointId)
        logging.info("BostoPoint Successfully Deleted")
        return BostoResult(True)


@BostoConnected
def addUser(user, **kwargs):
    bot = "'{}'".format(str(user.bot).upper())
    nick = "'{}'".format(user.nick) if hasattr(user, 'nick') and user.nick != None else "NULL"
    name = "'{}'".format(user.name)
    kwargs['connection'].addUser(user.id, name, user.discriminator, bot, nick) 
    return addWallet(user)

@BostoConnected
def updateUser(user, **kwargs):
    bot = "'{}'".format(str(user.bot).upper())
    nick = "'{}'".format(user.nick) if hasattr(user, 'nick') and user.nick != None else "NULL"
    name = "'{}'".format(user.name)
    return kwargs['connection'].updateUser(user.id, name, user.discriminator, bot, nick)

@BostoConnected
def addWallet(user, **kwargs):
    kwargs['connection'].addWallet(user.id) 
    return True


@BostoConnected
def removeMessage(payload, **kwargs):
    pointNum = int(countReactionByMessageId(messageId=payload.message_id))
    if pointNum > 0:
        deleteReactionByMessageId(messageId=payload.message_id)
        logging.info(f"{pointNum} reaction(s) removed from deleted message: {payload.message_id}")



@BostoConnected
def getPointId(message, payload, **kwargs):
    return kwargs['connection'].getPointId(authorId=message.author.id, reacterId=payload.user_id, messageId=message.id, emojiName=payload.emoji.name)


@BostoConnected
def checkUser(user, **kwargs):
    return kwargs['connection'].checkUser(user.id)


@BostoConnected
def getWallet(reactionType, user=None, userId=None, **kwargs):
    if userId == None:
        return kwargs['connection'].getWallet(reactionType, user.id)
    else:
        return kwargs['connection'].getWallet(reactionType, userId)

@BostoConnected
def getTotalWallet(user=None, userId=None, convertToDict=False, **kwargs):
    if userId == None:
        result = kwargs['connection'].getTotalWallet(user.id)
    else:
        result = kwargs['connection'].getTotalWallet(userId)
    if convertToDict:
        return dict(zip(BostoGeneric.EMOJI_LIST, result))
    else:
        return result

@BostoConnected
def hasFunds(payload, cost=1, **kwargs) -> bool:
    if cost == 0: return True
    else:
        reactionType = payload.emoji.name
        return kwargs['connection'].getWallet(reactionType=reactionType, userId=payload.user_id) >= cost


@BostoConnected
def getValue(payload=None, emojiName=None, **kwargs):
    name = payload.emoji.name if emojiName == None else emojiName
    return kwargs['connection'].getEmojiValue(name)


@BostoConnected
def deposit(payload, message, value, **kwargs):
    reactionType = payload.emoji.name
    if value > 1:
        kwargs['connection'].decrementWallet(reactionType=reactionType, userId=payload.user_id)
    kwargs['connection'].incrementWallet(reactionType=reactionType, userId=message.author.id)
    return

@BostoConnected
def incrementWallet(reactionType, userId, cost, **kwargs):
    kwargs['connection'].incrementWallet(reactionType=reactionType, userId=userId, cost=cost)
    return

@BostoConnected
def decrementWallet(reactionType, userId, cost, **kwargs):
    kwargs['connection'].decrementWallet(reactionType=reactionType, userId=userId, cost=cost)
    return



@BostoConnected
def deleteReactionByMessageId(message=None, messageId=None, **kwargs):
    if messageId != None:
        kwargs['connection'].deleteReactionByMessageId(messageId)
    else:
        kwargs['connection'].deleteReactionByMessageId(message.id)

@BostoConnected
def countReactionByMessageId(message=None, messageId=None, **kwargs):
    if messageId != None:
        return kwargs['connection'].countReactionByMessageId(messageId)
    else:
        return kwargs['connection'].countReactionByMessageId(message.id)

@BostoConnected
def countPoints(user = None, userId = None, **kwargs):
    if userId != None:
        return kwargs['connection'].countPoints(userId)
    else:
        return kwargs['connection'].countPoints(user.id)

@BostoConnected
def getEmojiCode(name, **kwargs):
    return kwargs['connection'].getEmojiCode(name)

@BostoConnected
def getEmojiName(code, **kwargs):
    return kwargs['connection'].getEmojiName(code)

@BostoConnected
def isAdmin(user=None, userId=None, **kwargs):
    try:
        if userId != None:
            return kwargs['connection'].isAdmin(userId) == "TRUE"
        else:
            return kwargs['connection'].isAdmin(user.id) == "TRUE"
    except Exception:
            logging.error("Cannot verify user is admin when checking database")
            return False

@BostoConnected
def getScoreBoard(**kwargs):
    emojiValue = dict(zip(BostoGeneric.EMOJI_LIST, tuple(map(lambda emojiName: int(getValue(emojiName=emojiName)), BostoGeneric.EMOJI_LIST))))
    return kwargs['connection'].getScoreBoard(emojiValue)

@BostoConnected
async def getPointTimeStat(user, imageRef, days, sep=False, **kwargs):
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    import numpy as np
    from matplotlib.cbook import get_sample_data
    import matplotlib.dates as dates
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    import datetime
    emojiCode = getEmojiCode(BostoGeneric.EMOJI_LIST[0])

  
    #Get Data
    received = {dates.date2num(datetime.datetime.now().date() - datetime.timedelta(i)):0 for i in range(days, 0, -1)}
    given = received.copy()
    
    received.update({dates.date2num(d):int(v) for d,v in kwargs['connection'].getPointTimeStatReceived(user.id, days)})
    given.update({dates.date2num(d):int(v) for d,v in kwargs['connection'].getPointTimeStatGiven(user.id, days)})
    
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
    
    #Set Points to Integer
    #ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
    #ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

    #Format axis values
    
    d_format = dates.DateFormatter('%m/%d')
    
    for a in axes:
        a.xaxis.set_major_formatter(d_format)
        a.yaxis.set_major_locator(MaxNLocator(integer=True))
        a.tick_params(colors='white')
        a.patch.set_facecolor('white')
        a.patch.set_alpha(1)
       

    #Chart Lables and Titles
    #ax1.set_title("Points Received", color="white")
    #ax2.set_title("Points Given", color="white")
    #fig.suptitle("Last {} Days".format(str(days)), color='white')
    #fig.text(0.05,0.5, "Bostopoints", ha="center", va="center", rotation=90, color="white")

    if sep:
        ax1.plot(x_received, y_received)
        ax2.plot(x_given, y_given)
        ax1.set_title("Points Received", color="white")
        ax2.set_title("Points Given", color="white")
        
        for x0, y0 in received.items():
            ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/BostoPoint.png'), 0.14/days), (x0, y0), frameon=False)
            ax1.add_artist(ab)
    
        for x0, y0 in given.items():
            ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/BostoPoint.png'), 0.14/days), (x0, y0), frameon=False)
            ax2.add_artist(ab)
    else:
        ax.plot(x_received, y_received)
        ax.plot(x_given, y_given)
        plt.legend(['Points Received', 'Points Given'], loc='upper left')
        for x0, y0 in received.items():
            ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/BostoPoint.png'), 0.14/days), (x0, y0), frameon=False)
            ax.add_artist(ab)

        for x0, y0 in given.items():
            ab = AnnotationBbox(OffsetImage(plt.imread('/usr/src/app/data/BostoPoint.png'), 0.14/days), (x0, y0), frameon=False)
            ax.add_artist(ab)
    
    
    #Set Layout
    #ax1.xaxis.set_ticks(np.arange(*ax1.get_xlim(), 5))
    plt.tight_layout(pad=1.5)
    #plt.subplots_adjust(left=0.12)

    ticks = []
    for a in axes:
        ticks += a.xaxis.get_ticklabels() + a.yaxis.get_ticklabels()

    [t.set_color('white') for t in ticks]
    
    #Save and send
    plt.savefig("/usr/src/app/data/plot.png", facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    await user.send(file=imageRef, content="Your {} statistics for the past {} days:".format(emojiCode, days))


async def removeDiscordReaction(payload, message, reason=""):
    reaction = next(x for x in message.reactions if x.emoji.name == payload.emoji.name)
    logging.info(reason)
    await reaction.remove(payload.member)
    return True

      
async def scoreBoardUpdate(client):
    import json
    from tabulate import tabulate
    abs_file_path = "/usr/src/app/data/settings.json"
   
    with open(abs_file_path) as f:
        settings = json.load(f)

    sbChannel = client.get_channel(settings['score_board']['channel'])
    sbMessage = await sbChannel.fetch_message(settings['score_board']['message'])
   
    
    data = getScoreBoard()
    headers = ["Ranking", "User", "Total Point Value"]
    table = tabulate(data, headers, tablefmt="pretty")
    table = table.replace("\n", "`\n`")
    sbMessage = await sbMessage.edit(content="`" +table +"`")






