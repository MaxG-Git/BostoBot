import discord
from discord.ext import commands
import logging
from BostoBot.controller.Controller import Controller
from BostoBot.model.ScoreBoardModel import ScoreBoardModel
import BostoBot.toolbox.SuperPy.iterable as IsPy
import json

class ScoreBoardController(Controller):
    
    def __init__(self, client):
        super().__init__(client, ScoreBoardModel)


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def sbSet(self, ctx, *args):
        
        settings = ScoreBoardModel.getSettings()

        settings['score_board']['channel'] = ctx.message.channel.id
        if any(arg.isdigit() for arg in args):
            settings['score_board']['message'] = IsPy.first(args, settings['score_board']['message'], lambda arg: arg.isdigit(), int)  
        else:
            sbMessage = await ctx.send("Score Board")
            settings['score_board']['message'] = sbMessage.id 

        ScoreBoardModel.setSettings(settings)

        
        await ctx.message.delete()


    
    
    @commands.command()
    @sbSet.after_invoke
    async def sbUpdate(self, ctx=None, *args):
        sbMessage = await self.model.getLocalScoreBoard("/usr/src/app/data/settings.json")
        data = self.model.getScoreBoard()
        table = self.model.generateTable(data)
        await sbMessage.edit(content="`" +table +"`")

    
def setup(client):
    client.add_cog(ScoreBoardController(client))