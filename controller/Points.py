import logging
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.toolbox.BostoResult import BostoResult as Result

def BostoConnected(origin):
    def wrapper(*args, **kwargs):
        try:
            from BostoBot.toolbox.BostoConnect import BostoConnect
            import mysql.connector.errors
            connection = BostoConnect()
            connection.connect()
            kwargs['connection'] = connection
            return origin(*args, **kwargs)
        except mysql.connector.Error as err:
            logging.error("Error while connecting to Database")
            logging.error(str(err))
    return wrapper


@BostoConnected
def addReaction(message, payload, value, **kwargs) -> Result:
    author, reacter, emojiName = message.author, payload.member, payload.emoji.name


    # Search for message author by id
    author_registered = int(checkUser(author))
    # Search for react-er's by id
    reacter_registered = int(checkUser(reacter))

    # If reacter is not found, add user
    if reacter_registered > 1:
         logging.error(f"User: {reacter.id} detected duplicate registrations")
    elif reacter_registered < 1:
        try:
            addUser(reacter)
        except Exception as err:
            return Result(False, "user", error=err)

     # If author is not found, add user
    if author_registered > 1:
         logging.error(f"User: {author.id} detected duplicate registrations")
    elif author_registered < 1:
        try:
            addUser(author)
        except Exception as err:
            return Result(False, "user", error=err)

    
    if value > 1 and not hasFunds(payload, 1):
        return Result(False, "funds")

    kwargs['connection'].addReaction(authorId=author.id, reacterId=reacter.id, messageId=message.id, emojiType=emojiName)
    return Result(True)

@BostoConnected
def getWalletValue(user, **kwargs):
    wallet = getTotalWallet(user)
    return sum(wallet)


   


@BostoConnected
def removeReaction(pointId, message, payload, **kwargs) -> Result:
    if(pointId is None):
         return Result(False, "untracked")
    else:
        kwargs['connection'].removePoint(pointId)
        logging.info("BostoPoint Successfully Deleted")
        return Result(True)


@BostoConnected
def addUser(user, **kwargs):
    bot = str(user.bot).upper()
    nick = user.nick if hasattr(user, 'nick') else "None"
    kwargs['connection'].addUser(user.id, user.name, user.discriminator, bot, nick) 
    return addWallet(user)

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


async def removeDiscordReaction(payload, message, reason=""):
    reaction = next(x for x in message.reactions if x.emoji.name == payload.emoji.name)
    logging.info(reason)
    await reaction.remove(payload.member)
    return True





