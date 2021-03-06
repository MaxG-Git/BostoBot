import discord
import asyncio
import logging


class View:
    
    def __init__(self, client):
        self.client = client
        

    @staticmethod
    async def error(sendable, msg="Somethings gone wrong, Try again or let a server mod know" ):
        message = f":crying_cat_face:\nMrrrrrrrrr!\n{msg}"
        return await sendable.send(message)

    @staticmethod
    async def info(sendable, msg=""):
        message = f":cat:\nMeow!\n{msg}"
        return await sendable.send(message)

    @staticmethod
    async def send(sendable, *args, **kwargs):
        return await sendable.send(*args, **kwargs)

    async def sendEdit(self, mixedMessable, message=None, **options):
        options.update({"content": message})
        if issubclass(mixedMessable.__class__, discord.abc.Messageable): 
            return await mixedMessable.send(**options)  
        else:
            await mixedMessable.edit(**options)
            return mixedMessable
    
    #Note Add SometimeSay
    @staticmethod
    def sometimes(percent, original, option=None, options=[]):
        import random

        

    
    def responceAction(self,
    check = lambda x: True, 
    timeout = 20.0, 
    action = 'message', 
    reactionOptions = (),
    filterReactionOptions=True,): 
        return {
        "check" : check, 
        "timeout" : timeout, 
        "action" : action,
        "reactionOptions" : reactionOptions,
        "filterReactionOptions" : filterReactionOptions,
        }



    async def getResponce(self, 
        # Message configurations
        mixedMessable,
        question = None, 
        clearReactions = False,
        actions = [],
        condition=None,
        timeOutMessage="Sorry responce time has expired", 
        options = {},
        editOnFail = True,
        embed = None,
        return_when = asyncio.FIRST_COMPLETED,
        return_pending = False
        ):
        #actions.append(self.responceAction(check=check, timeout=timeout, action=action, reactionOptions=reactionOptions, clearReactions=clearReactions))
        if isinstance(actions, dict):
            actions = [actions]
        
        for act in actions:
            act['used_check'] = lambda payload: act['check'](payload)
        
        # Send Questions to get responce
        question = await self.sendEdit(mixedMessable, question, embed=embed, **options)

        for act in actions:
            if len(act['reactionOptions']) > 0:
                
                
                # Add reaction Options
                for emoji in act['reactionOptions']:
                    await question.add_reaction(emoji)
            
                # Add Filter for reaction responce
                if act["filterReactionOptions"]:
                    act['used_check'] = lambda payload: act['check'](payload) and str(payload.emoji) in act['reactionOptions']
                 

                


        '''
        # Add reaction Options or buttons to post if options are given and flag is True
        if len(reactionOptions) > 0:
            
            # Add reaction Options
            for emoji in reactionOptions:
                await question.add_reaction(emoji)
            



            # Add Filter to check if flag is used
            if filterReactionOptions:
                def new_replyFilter(payload): return str(payload.emoji) in reactionOptions and replyFilter(payload)
                used_replyFilter = new_replyFilter
                
                
                 pending_tasks = [bot.wait_for('reaction_add',check=check),
                 bot.wait_for('reaction_remove',check=check)]
        
        done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
        '''     
                
        

        try:
            
            pending_tasks = [self.client.wait_for(act['action'], timeout=act['timeout'], check=act['check']) for act in actions]
            reponce, pending_tasks = await asyncio.wait(pending_tasks, return_when=return_when)
            
            for task in pending_tasks:
                task.cancel()
            
            if return_when == asyncio.FIRST_COMPLETED:
                reponce = list(reponce).pop().result()
            
                
            if clearReactions :
                await question.clear_reactions()


            if condition == None:
                return question, reponce
            else:
                return question, condition(reponce)
        except asyncio.TimeoutError:
            
            if clearReactions:
                await question.clear_reactions()
            
            if editOnFail:
                question = await self.sendEdit(question, timeOutMessage, embed=None)

            
            return question, False



    