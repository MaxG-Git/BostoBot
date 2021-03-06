import discord
from discord.ext import commands
import logging
import BostoBot.startup
import BostoBot.controller.Controller as Controller
from BostoBot.model.SettingsModel import SettingsModel 
from BostoBot.view.SettingsView import SettingsView

class SettingsController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, SettingsModel, SettingsView)
    
    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def addpoint(self, ctx, *args):
        await ctx.message.delete()
        
        question, newReaction = await self.view.getNewBostoType(ctx, ctx.message.author, self.model.BostoList)

        if newReaction == False or str(newReaction.emoji) == "❌":
            await self.view.cancelNewBostoType(question)
        else:
            self.model.retrieveImage(str(newReaction.emoji.url), newReaction.emoji.name.lower())
            value = await self.view.getNewBostoTypeValue(question, ctx.message.author, str(newReaction.emoji))
            
            if value == False:
                await self.view.cancelNewBostoType(question)
            else:
                self.model.addBostoType(newReaction, value)
                await self.view.addBostoTypeSuccess(question)
                return await ctx.invoke(self.client.get_command('reloadcogs'))
        
    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def removepoint(self, ctx, *args):

        question, removeReaction = await self.view.getRemoveBostoType(ctx, ctx.message.author, [point['code'] for point in self.model.BostoPoints.values()])

        if removeReaction == False or str(removeReaction.emoji) == "❌":
            await self.view.cancelNewBostoType(question, "BostoType Removal")
        else:
            await question.delete()
            question, confirmed = await self.view.getRemoveBostoTypeConfirmation(ctx, ctx.message.author, str(removeReaction.emoji))
           
            if not confirmed:
                await self.view.cancelNewBostoType(question, "BostoType Removal")
            else:
                self.model.removeBostoType(removeReaction)
                self.model.removeImage(removeReaction.emoji.name)
                await self.view.removeBostoTypeSuccess(question)
                return await ctx.invoke(self.client.get_command('reloadcogs'))
                
    @commands.command()
    async def emb(self, ctx):
        embed=discord.Embed(title="Buy Order", 
        description="Buy Order", 
        color=0xFF5733)
        await ctx.send(embed=embed)   
            



def setup(client):
    client.add_cog(SettingsController(client))