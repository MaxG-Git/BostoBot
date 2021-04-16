import discord
import asyncio
import logging


class View:
    
    def __init__(self, client):
        self.client = client
        self.regIndicator = {'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
        'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
        'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}', 'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
        'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
        'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
        'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
        'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}', 'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
        'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
        'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
        'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
        'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}', 'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
        'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
        's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
        'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
        'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}', 'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}',
        'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
        'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}',
        '0': '0⃣', '1': '1⃣', '2': '2⃣', '3': '3⃣',
        '4': '4⃣', '5': '5⃣', '6': '6⃣', '7': '7⃣', '8': '8⃣', '9': '9⃣', '!': '\u2757',
        '?': '\u2753'}

    
    def optionDict(self, iterable, set_keys=None):
        if len(iterable) > 26: return

        if set_keys == None:
            return dict(zip(list(map(lambda s: self.regIndicator[chr(s)], range(ord('a'), ord('a')+len(iterable)))), iterable))
        else:
            return dict(zip(list(map(lambda s: self.regIndicator[s], set_keys)), iterable))


    @staticmethod
    def parseChannel(obj):
        return obj.channel_id if isinstance(obj, discord.RawReactionActionEvent) else obj.channel.id

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
        
    @staticmethod
    def sometimes(original, options, percent : float = 0.5):
        import random
        result = random.random()
        if result <= percent:
            if not isinstance(options, list):
                return original + options
            else:
                index = random.randint(0, len(options)-1)
                return original + options[index]
        else:
            return original




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
        
        if isinstance(actions, Action):
            actions = [actions]
        
        
        # Send Questions to get responce
        question = await self.sendEdit(mixedMessable, question, embed=embed, **options)

        for act in actions:
            if len(act.reaction_options) > 0:
                
                # Add reaction Options
                for emoji in act.reaction_options:
                    await question.add_reaction(emoji)          

        try:
            pending_tasks = [self.client.wait_for(act.action, timeout = act.timeout, check = act.check) for act in actions]
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


class Action:

    def __init__(self,
    check : callable = lambda x: True, 
    timeout : float = 20.0, 
    action : str = 'message', 
    reaction_options : tuple = (),
    filter_reaction_options = None,
    filter_channel = None,
    ):
       
        self.timeout = timeout
        self.action = action
        self.reaction_options = reaction_options
        self.filter_channel = filter_channel
        self.checks = [check]
        self.filter_reaction_options = "reaction" in action.lower() if filter_reaction_options == None else filter_reaction_options
        if filter_reaction_options:
            self.checks.append(lambda payload: str(payload.emoji) in self.reaction_options)
        if isinstance(filter_channel, int):
             self.checks.append(lambda payload: View.parseChannel(payload) == filter_channel)
    
    
    def check(self, *args, **kwargs):
        results = []
        for check in self.checks:
            results.append(check(*args, **kwargs))
        return False not in results

    
        
        


    