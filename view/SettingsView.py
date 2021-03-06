from BostoBot.view.View import View
import asyncio
import logging

class SettingsView(View):

    def __init__(self, client):
        super().__init__(client)

    

    async def getNewBostoType(self, sendable, author, currentList):
        
        return await self.getResponce(sendable, 
            actions = self.responceAction(
                reactionOptions=("❌"),
                filterReactionOptions=False,
                check=lambda payload: payload.user_id == author.id,  
                action="raw_reaction_add"
            ),
            question="Please react to this message with the new BostoType or click ❌ to cancel",      
        )
    

    async def getNewBostoTypeValue(self, editable, author, emojiCode):
        await editable.clear_reactions()
        editable, message = await self.getResponce(editable, 
            actions = self.responceAction(check=lambda message: message.author.id == author.id and (message.content.isdigit() or message.content.lower() == 'cancel' )),  
            question="Please enter the value of the new BostoType " + emojiCode + " or cancel to cancel", \
        )
        if message.content.lower() == 'cancel':
            return False
        else:
            return int(message.content)
    '''
    async def getNewBostoTypeImage(self, editable, author, emojiCode):
        editable, repsonce = await self.getResponce(editable, \
            actions = self.responceAction(check=lambda message: message.author.id == author.id and any(at.filename.lower().endswith("png") for at in message.attachments)),  \
            question="Please respond with an image of the new BostoType " + emojiCode + " or cancel to cancel", \
        )
        return logging.info(repsonce)
    '''  
    
    async def getRemoveBostoType(self, sendable, author, currentList):
        return await self.getResponce(sendable, 
            actions = self.responceAction(
            check=lambda payload: payload.user_id == author.id,  
            reactionOptions=tuple(list(currentList) + ["❌"]), 
            action="raw_reaction_add", 
            ),
            question="Please react with the point you would like to remove ❌ to cancel"
        )

    async def getRemoveBostoTypeConfirmation(self, sendable, author, emojiCode):
        return await self.getResponce(sendable, 
            actions = self.responceAction(
            check=lambda message: message.author.id == author.id,  
            ),
            question="Are you sure you want to remove {} from **ALL WALLETS** This cannot be un-done!\nType `yes` to confirm".format(emojiCode), 
            condition=lambda message: message.content.lower() == 'yes'
        )
        
    async def addBostoTypeSuccess(self, editable):
        await editable.edit(content="BostoType Added! Reloading Cogs...")
        await editable.delete(delay=6)
    
    async def removeBostoTypeSuccess(self, editable):
        await editable.edit(content="BostoType Removed! Reloading Cogs...")
        await editable.delete(delay=6)
        

    async def cancelNewBostoType(self, editable, event = "Add"):
        await editable.edit(content="Cancled {} Event!".format(event))
        await editable.delete(delay=6)
