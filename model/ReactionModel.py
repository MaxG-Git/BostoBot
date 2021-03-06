import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.toolbox.BostoGeneric import BostoResult, BostoResult
import BostoBot.model.Model as Model



class ReactionModel(Model.Model):
    
    def __init__(self, client):
        super().__init__(client)

    @Model.BostoConnected
    def addReaction(self, message, payload, value, **kwargs) -> BostoResult:
        author, reacter, emojiName = message.author, payload.member, payload.emoji.name
        if not self.ensureUser(author) or not self.ensureUser(reacter): return BostoResult(False, "user")

        self.updateUser(reacter)

        if value > 1 and not self.hasFunds(payload, 1):
            return BostoResult(False, "funds")

        kwargs['connection'].addReaction(authorId=author.id, reacterId=reacter.id, messageId=message.id, emojiType=emojiName)
        return BostoResult(True)


    @Model.BostoConnected
    def getPointId(self, message, payload, **kwargs):
        return kwargs['connection'].getPointId(authorId=message.author.id, reacterId=payload.user_id, messageId=message.id, emojiName=payload.emoji.name)
    

    @Model.BostoConnected
    def hasFunds(self, payload, cost=1, **kwargs) -> bool:
        if cost == 0: return True
        else:
            reactionType = payload.emoji.name
            return kwargs['connection'].getWallet(reactionType=reactionType, userId=payload.user_id, BostoList = self.BostoList) >= cost


    @Model.BostoConnected
    def deposit(self, payload, message, value, **kwargs):
        reactionType = payload.emoji.name
        if value > 1:
            kwargs['connection'].decrementWallet(reactionType=reactionType, userId=payload.user_id, BostoList = self.BostoList)
        kwargs['connection'].incrementWallet(reactionType=reactionType, userId=message.author.id, BostoList = self.BostoList)
        return

    
    async def removeDiscordReaction(self, payload, message, reason=""):
        reaction = next(x for x in message.reactions if x.emoji.name == payload.emoji.name)
        logging.info(reason)
        await reaction.remove(payload.member)
        return True

