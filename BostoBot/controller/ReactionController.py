import discord
from discord.ext import commands
from discord.errors import HTTPException
import logging
import BostoBot.controller.Controller as Controller
from BostoBot.model.ReactionModel import ReactionModel
from BostoBot.view.ReactionView import ReactionView


class ReactionController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, ReactionModel, ReactionView)
        


    @commands.Cog.listener()
    # pylint: disable=not-callable
    async def on_raw_reaction_add(self, payload):
        
        if not self.model.ensureBostoBase: return
        allEmojis = self.model.BostoPoints
        # Cancel If -> (Private message or reaction is not a bostopoint)
        if (payload.guild_id is None) or (payload.emoji.name not in self.model.BostoList): return
        
        # Get message
        message = await self.messageFromRawReactionActionEvent(payload)
        try:
            logging.info("\n\n\nREACTION: {} --> {}".format(payload.member.name, message.author.name))
        except Exception:
            logging.error("\n\n\nUnable to print reaction useres")
       
        # Check if reaction is self give (do not detect self)
        if message.author.id == payload.user_id and payload.user_id != self.client.user.id:
            
            reaction = next(x for x in message.reactions if x.emoji.name == payload.emoji.name)
            try:
                await self.view.selfReactionFailure(payload.member, str(payload.emoji))
            except discord.HTTPException as err:
                logging.error("Failed Notifying user of self reaction possible bot due to bot:\n" + str(err))
            except Exception as err:
                logging.error("Failed Notifying user of self reaction:\n" + str(err))
            
            
            return await reaction.remove(payload.member)
        
        
        # SQL Starts here
        try:
            value = allEmojis[payload.emoji.name]['value']
            
            # Check if reaction already exist (applicable for attempted refund on value points)            
            pointId = self.model.getPointId(message, payload)
            if not pointId == None:
                logging.info("Tried to add value point that already exists. Assuming Double add after attempted refund")
                return

            result = self.model.addReaction(message, payload, value)
            
            if not result.result:
                if result.reason == 'funds':
                    #await self.view.error(payload.member, f"Looks like you are out of {payload.emoji.name.capitalize()}s {str(payload.emoji)}\nUse the `b/wallet` Command to see your {payload.emoji.name.capitalize()}s\nUse the `b/buy` command to get more {str(payload.emoji)}")
                   
                    try:
                        showTip = self.model.getSpecificUserSettings('tool_tips', payload.member.id) == "TRUE"
                    except Exception as err:
                        showTip = True

                    await self.view.fundsFailure(payload.member, payload.emoji.name.capitalize(), str(payload.emoji), showTip)
                    try:
                        return await self.model.removeDiscordReaction(payload, message, "BostoPoint Not Added (Spendable is 0)")
                    except Exception as err:
                        logging.error("Unable to remove discord reaction on failure")
                        logging.error(str(err))
                        return
                elif result.reason == 'user':
                    logging.error("Unable to add user whilst adding reaction")
                    logging.error(str(result.error))
                    return
                else:
                    await self.view.unknownAddFailure(payload.member, payload.emoji.name.capitalize())
                    logging.error("Unknown error whilst adding reaction")
                    logging.error(str(result.error))
                    return

            logging.info("BostoPoint Successfully Added")
                

        except Exception as err:
            logging.error("Unable to add point")
            logging.error(str(err), True)
            return

           
        try:
            self.model.deposit(payload, message, value) # After this line value point has been deposited
            logging.info("Spendable Updated")
        
            
        except Exception as err:
            logging.info("Unable to Updated Spendable")
            return logging.error(str(err))

        try:
            if hasattr(payload.member, 'nick') and payload.member.nick != None:
                fromName = payload.member.nick
            else:
                fromName = payload.member.name
            
            reacterNotify =  self.model.getSpecificUserSettings('point_remove_notification', payload.member ) == "TRUE"
            authorNotify =  self.model.getSpecificUserSettings('point_add_notification', message.author) == "TRUE"

            await self.view.addSuccess(payload.member, message.author, str(payload.emoji), value, fromName, reacterNotify, authorNotify)
        except HTTPException as err:
            logging.error("Failed while sending notifications to user")
            logging.error(str(err))
            
        
        try:
            ctx = await self.client.get_context(message)
            await ctx.invoke(self.client.get_command('sbUpdate'))
            logging.info("Updated Score Board")
        except Exception as err:
            logging.info("Unable to update Score Board")
            logging.info(str(err))

    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
          
        if not self.model.ensureBostoBase: return
          # pylint: disable=not-callable
        if (payload.guild_id is None) or (payload.emoji.name not in self.model.BostoList): return None 
        message = await self.messageFromRawReactionActionEvent(payload)

        
        # If author == reacter it is assumes the bot itself deleted the emoji and does not need to check database
        if message.author.id == payload.user_id  and (payload.user_id != self.client.user.id):
            return logging.info("Author is equal to reactor, Assuming auto deletion.")
        
        # Update BostoPoint Table
        try:
            value = int(self.model.getValue(payload=payload))
        except Exception as err:
            logging.error("Unable to locate value")
            logging.error(str(err))
            return    

    
        reacter = await self.client.fetch_user(payload.user_id)

        try:
            
            # spendable = int(Points.getSpendable(user=reacter))
            pointId = self.model.getPointId(message, payload)
           
            if value != 1: # Emoji Has Value...
                if pointId == None: # Point was never added in the first place
                    logging.info("Un-Tracked Reaction, Assuming auto deletion, (Message handled in reaction_add event)")
                    return
                else: # Point was added and 
                    logging.info("Tracked Point deleted assuming attemtted refund, notifying user....")
                    link = 'https://discordapp.com/channels/{}/{}/{}'.format(message.guild.id, message.channel.id, message.id)
                    return await self.view.attemptedRefundFailure(reacter, message, str(payload.emoji), payload.emoji.name.capitalize(), link)
                
        except Exception as err:
            #logging.error("Unable to remove point")
            logging.error(err, True)
            return


def setup(client):
    client.add_cog(ReactionController(client))