import discord
from discord.ext import commands
import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
import BostoBot.controller.Points as Points



class BostoPoints(commands.Cog) :
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    # pylint: disable=not-callable
    async def on_raw_reaction_add(self, payload):
        
        # Cancel If -> (Private message or reaction is not a bostopoint)
        if (payload.guild_id is None) or (payload.emoji.name not in BostoGeneric.EMOJI_LIST): return
        message = await self.messageFromRawReactionActionEvent(payload)
       
        # Check if reaction is self give 
        if message.author.id == payload.user_id and payload.user_id != self.client.user.id:
            reaction = next(x for x in message.reactions if x.emoji.name == payload.emoji.name)
            await BostoGeneric.Info(payload.member, f"You cant give yourself a {str(payload.emoji)}!")
            return await reaction.remove(payload.member)
        
        # SQL Starts here
        try:
            value = int(Points.getValue(payload=payload))
            

            # Check if reaction already exist (applicable for attempted refund on value points)
            
            pointId = Points.getPointId(message, payload)
            if not pointId == None:
                logging.info("Tried to add value point that already exists. Assuming Double add after attempted refund")
                return

            result = Points.addReaction(message, payload, value)
            
            if not result.result:
                if result.reason == 'funds':
                    await BostoGeneric.Err(payload.member, f"Looks like you are out of {payload.emoji.name.capitalize()}s {str(payload.emoji)}\nUse the `b/wallet` Command to see your {payload.emoji.name.capitalize()}s")
                    try:
                        return await Points.removeDiscordReaction(payload, message, "BostoPoint Not Added (Spendable is 0)")
                    except Exception as err:
                        logging.error("Unable to remove discord reaction on failure")
                        logging.error(str(err))
                        return
                elif result.reason == 'user':
                    logging.error("Unable to add user whilst adding reaction")
                    logging.error(str(result.error))
                    return
                else:
                    await BostoGeneric.Err(payload.member, f"Looks like you something went wrong when adding a {payload.emoji.name.capitalize()}")
                    logging.error("Unknown error whilst adding reaction")
                    logging.error(str(result.error))
                    return

            logging.info("BostoPoint Successfully Added")
        except Exception as err:
            logging.error("Unable to add point")
            logging.error(str(err), True)
            return

           
        try:
            Points.deposit(payload, message, value) # After this line value point has been deposited
            logging.info("Spendable Updated")
            
           
            if hasattr(payload.member, 'nick') and payload.member.nick != None:
                fromName = payload.member.nick
            else:
                fromName = payload.member.name
            '''
            if hasattr(message.author, 'nick') and message.author.nick != None:
                toName = message.author.nick
            else:
                toName = message.author.name
            '''
            if value > 1:
                await payload.member.send(f"A {str(payload.emoji)} has been removed from your wallet")
            await message.author.send(f"A Wild {str(payload.emoji)} has appeared in your wallet *from {fromName}*")
            
        except Exception as err:
            logging.info("Unable to Updated Spendable")
            return logging.error(str(err))
            
        

        
        

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
          # pylint: disable=not-callable
        if (payload.guild_id is None) or (payload.emoji.name not in BostoGeneric.EMOJI_LIST): return None 
        message = await self.messageFromRawReactionActionEvent(payload)

        
        # If author == reacter it is assumes the bot itself deleted the emoji and does not need to check database
        if message.author.id == payload.user_id  and (payload.user_id != self.client.user.id):
            return logging.info("Author is equal to reactor, Assuming auto deletion.")
        
        # Update BostoPoint Table
        try:
            value = int(Points.getValue(payload=payload))
        except Exception as err:
            logging.error("Unable to locate value")
            logging.error(str(err))
            return    

    
        reacter = await self.client.fetch_user(payload.user_id)

        try:
            
            # spendable = int(Points.getSpendable(user=reacter))
            pointId = Points.getPointId(message, payload)
           

            if value != 1: # Emoji Has Value...
                if pointId == None: # Point was never added in the first place
                    logging.info("Un-Tracked Reaction, Assuming auto deletion, (Message handled in reaction_add event)")
                    return
                else: # Point was added and 
                    logging.info("Tracked Point deleted assuming attemtted refund, notifying user....")
                    return await BostoGeneric.Info(reacter, f"You tried to remove a {str(payload.emoji)} from *{message.author.name}'s* message!\n{payload.emoji.name.capitalize()}'s are **not** refundable!\n*(you can add the {payload.emoji.name.capitalize()} emoji back to {message.author.name}'s **original message** if you would like for free)*") # await message.add_reaction(str(payload.emoji))
                
            '''
            logging.info("Attempting to remove point from database....")
            result =  Points.removeReaction(pointId, message, payload)
            if not result.result:
                logging.error("Unable to remove point")  
                if result.reason == 'untracked':
                    logging.error("Point seems to be un-tracked") 
            else:
                logging.info("Point removed")
            
            return    
            '''
        except Exception as err:
            #logging.error("Unable to remove point")
            logging.error(err, True)
            return

    '''
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        Points.removeMessage(payload)
        
    '''


#	id	name	discriminator	bot	nick	bostopoints	

           
        

    @commands.command()
    async def updateNick(self, ctx, *args):
        # pylint: disable=not-callable
        from BostoBot.toolbox.BostoConnect import BostoConnect
        connection = BostoConnect()
        try:
            connection.connect()
            connection.editUser(field='nick', value=args[0], authorId=ctx.author.id)
        except Exception:
            await BostoGeneric.Err(ctx)
            return

    
    @commands.command()
    async def addMe(self, ctx):
        # pylint: disable=not-callable
        from BostoBot.toolbox.BostoConnect import BostoConnect
        connection = BostoConnect()
        try:
            connection.connect()
            #connection.addUser(author=ctx.author)
        except Exception as err:
            await BostoGeneric.Err(ctx)
            logging.error(str(err))
            return


    
    @commands.command()
    async def buy(self, ctx):
        import asyncio
        if ctx.guild is not None: return
        emojiSelection = await ctx.send("Select The Bosto-Emoji You would like to create:")
        user = ctx.message.author
        emojiCode = dict(zip(BostoGeneric.EMOJI_LIST, tuple(map(Points.getEmojiCode, BostoGeneric.EMOJI_LIST))))
        emojiValue = dict(zip(BostoGeneric.EMOJI_LIST, tuple(map(lambda emojiName: int(Points.getValue(emojiName=emojiName)), BostoGeneric.EMOJI_LIST))))
        

        def check(payload):
            return payload.user_id == ctx.message.author.id and str(payload.emoji) in emojiCode.values()

        # Get Desired Emoji
        emojiSelectionOptions = [await emojiSelection.add_reaction(e) for e in emojiCode.values()]
        

        try:
            payload = await self.client.wait_for('raw_reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Time Out")
        else:
            await emojiSelection.delete()
            
            
            # Desired Emoji Captured 
            selected = str(payload.emoji)
            selectedName = payload.emoji.name
            selectedVal = emojiValue[selectedName]
            graphic = await ctx.send(selected)

            
            # Calculate Available Spending Options
            totalWallet = Points.getTotalWallet(user=user, convertToDict=True)


            availPayment = []
            for emj in BostoGeneric.EMOJI_LIST:
                if emj != selectedName:
                    if emojiValue[emj] * totalWallet[emj] >= selectedVal:
                        availPayment.append(emojiCode[emj])
            
            if len(availPayment) == 0:
                await graphic.edit(content=f"Looks like you don't have enough points for a {selected} right now.\n*You can check your points with the `wallet` command*")
                return

            
            emojiSelection = await ctx.send(f"Please Choose what you want to convert into a {selected}")
            emojiSelectionOptions = [await emojiSelection.add_reaction(e) for e in availPayment]
            try:
                payload = await self.client.wait_for('raw_reaction_add', timeout=20.0, check=lambda payload: payload.user_id == ctx.message.author.id and str(payload.emoji) in availPayment)
            except asyncio.TimeoutError:
                await ctx.send("Time Out")
            else:
                await emojiSelection.delete()
                costEmoji = payload.emoji.name
                costEmojiCode = str(payload.emoji)
                costEmojiVal = emojiValue[costEmoji]
                costEmojiTotal = totalWallet[costEmoji]
                await graphic.edit(content=f"{costEmojiCode} ➡️ {selected}")


                costEmojiTotalValue = costEmojiVal * costEmojiTotal

                availMax = costEmojiTotalValue // selectedVal

                availOptionsDivisor = []
                for i in range(1, availMax+1):
                    if i % costEmojiVal == 0:
                        availOptionsDivisor.append("**`"+str(i)+"`**")

                if len(availOptionsDivisor) > 1:
                    availOptionsDivisor.insert(len(availOptionsDivisor) -1, "or")

                availOptionsDivisorString = ", ".join(availOptionsDivisor)
                


                if availMax == 0:
                    needed = (selectedVal-costEmojiTotalValue) // costEmojiVal
                    await ctx.send(f"Meow\nLooks like you don't have enough points for a {selected} right now.\nYou have **{costEmojiTotal}** {costEmojiCode}'s you need **{needed}** more for a {selected}")
                    return

                msg1 = await ctx.send(f"You Currently have **`{costEmojiTotal}`** {costEmojiCode}\nYou can create a total of {availOptionsDivisorString} {selected}")
                msg2 =  await ctx.send(f"Please respond with how many {selected} to create:")
                try:
                    quantityResponce = await self.client.wait_for('message', timeout=20.0, check=lambda msg: msg.author.id == ctx.message.author.id and str(msg.content).isdigit())
                except asyncio.TimeoutError:
                    await ctx.send("Time Out")
                else:
                    quant = int(quantityResponce.content)
                    totalPriceVal = quant * selectedVal
                    costPrice = totalPriceVal // costEmojiVal
                    logging.info(f"Remove {costPrice} {costEmoji}")




                    priceValue = (quant * costEmojiVal) // selectedVal
                    logging.info(priceValue)
                   
                    
                    
                    
                    await msg1.delete()
                    await msg2.delete()
                    loadString = ""
                    for i in range(0, 3):
                        loadString+= "🔄 "
                        await graphic.edit(content=loadString)
                        await asyncio.sleep(1)
                    await graphic.edit(content="✅")

                   
                    

                

        
                
            


    @commands.command()
    async def wallet(self, ctx):
     
        try:
            
            pointNum = Points.getWallet('bostopoint', user=ctx.author)
            coinNum = Points.getWallet('bostocoin', user=ctx.author)
            # trophyNum = Points.getWallet('bostotrophie', user=ctx.author)

            pointEmoji = Points.getEmojiCode(BostoGeneric.EMOJI_LIST[0])
            coinEmoji = Points.getEmojiCode(BostoGeneric.EMOJI_LIST[1])

            plurals = ['', '']

            if pointNum > 1:
                plurals[0] = "'s"
            if coinNum > 1:
                plurals[1] = "'s"

        except Exception as err:
            await BostoGeneric.Err(ctx)
            logging.error(str(err))
            return
        if coinNum is None:
            coinNum = 0
        await ctx.author.send(pointEmoji)
        await ctx.author.send(f"You Have Received **{pointNum}** {BostoGeneric.EMOJI_LIST[0].capitalize()}{plurals[0]} and have *`unlimited`* to give out.")
        await ctx.author.send(coinEmoji)
        await ctx.author.send(f"You Have **{coinNum}** {BostoGeneric.EMOJI_LIST[1].capitalize()}{plurals[1]} *(You can only give out as much as you have)*")

        
         
     


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
        



    
        
      
def setup(client):
    client.add_cog(BostoPoints(client))
