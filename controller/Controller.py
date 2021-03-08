import discord
from discord.ext import commands
import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.model.Model import Model
from BostoBot.view.View import View


def EnsureBostoUser(ctx):
    BaseModel = Model(None)
    return BaseModel.ensureUser(ctx.message.author)

def EnsureBostoBase(ctx):
    BaseModel = Model(None)
    return BaseModel.ensureBostoBase()

def ViewContextAuthor(origin):
    def wrapper(self, ctx, *args, **kwargs):
        self.view.setContext(ctx.author)
        return origin(self, ctx, *args, *kwargs)
    return wrapper



class Controller(commands.Cog) :
    def __init__(self, client, CustomModel = Model, CustomView = View):
        self.client = client
        self.model = CustomModel(client)
        self.view = CustomView(client)


    
    
    async def bostopointsFromFromRawReactionActionEvent(self, payload : discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return None # Reaction is on a private message
        elif payload.emoji.name == 'bostopoint' or payload.user_id == 417803427368796160:
            message = await self.messageFromRawReactionActionEvent(payload) #Grab Message Object
            return self.bostopointsFromMessage(message) # Calculate total messages points
            
        

    async def messageFromRawReactionActionEvent(self, payload : discord.RawReactionActionEvent) -> discord.Message :
        """Gets the discord.message Object from a discord.RawReactionActionEvent. The message the 
        discord.RawReactionActionEvent (the message in which has been reacted too) is the message
        object retrieved.

        Arguments:
            payload {discord.RawReactionActionEvent} -- [description]

        Returns:
            discord.Message -- The message the reaction has been added too
        """
        channel = self.client.get_channel(payload.channel_id) # Get Channel Object From Client with payload's channel ID
        try:
           return await channel.fetch_message(payload.message_id) # Get Message Object From CHannel Object with payload's message ID
        except discord.errors.NotFound as err:
            logging.error(f"Unable to locate message ({payload.message_id}) when trying to detect a reaction.\n{err.text}")
        else:
            logging.error(f"Unknown error when detecting reaction on ({payload.message_id}).")



    async def reacterFromRawReactionActionEvent(self, payload : discord.RawReactionActionEvent) -> discord.Message :
        """Gets the discord.message Object from a discord.RawReactionActionEvent. The message the 
        discord.RawReactionActionEvent (the message in which has been reacted too) is the message
        object retrieved.

        Arguments:
            payload {discord.RawReactionActionEvent} -- [description]

        Returns:
            discord.Message -- The message the reaction has been added too
        """
        try:
           return await self.client.fetch_user(payload.user_id)
        except discord.errors.NotFound as err:
            logging.error(f"Unable to locate user ({payload.message_id}) \n{err.text}")
        



    @staticmethod
    def bostopointsFromMessage(message):
        """Calculates the amount of Bosto-Points are on a given message object

        Arguments:
            message {discord.Message} -- Message Object representing a single discord message

        Returns:
            int -- Integer representing the amount of Bosto-Points are on a given message (returns 0 if none)
        """
        for reaction in message.reactions:
                if str(reaction.emoji).startswith('<:bostopoint:'):
                    return reaction.count
        return 0