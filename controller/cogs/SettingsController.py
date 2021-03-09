import discord
from discord.ext import commands
import logging
import BostoBot.startup
import BostoBot.toolbox.SuperPy.iterable as IsPy
import BostoBot.controller.Controller as Controller
from BostoBot.model.SettingsModel import SettingsModel 
from BostoBot.view.SettingsView import SettingsView

class SettingsController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, SettingsModel, SettingsView)


    @commands.command()
    @commands.dm_only()
    @commands.check(Controller.EnsureBostoUser)
    async def help(self, ctx, givencommand=None):
        """
        The help command is the command you are currently using. 
        To use this command type `help` and select the command you want to see more information on.

        This command can help you understand all the commands Bosto-Bot has. Some of the information included may contain; How to use the command, What the command does, and different paramters the command accepts

        **ℹ Some useful information**:

        ● Arguments can be a of 2 different types: (VAR, FLAG)\n
        ● FLAG - This type of argument is a binary on/off to use this argument include the flag while running the command\n
        ● VAR - This is a parameter much like a parameter in a function can be any value\n

        Optional Arguments:
        ● `command` : VAR - Bypass the initial help menu by passing a command name to the command
        """
        helpMatrix = self.model.getLocalHelp()
        sortedCommands = dict( sorted([(com.name, com) for com in self.client.commands if not com.hidden], key=lambda x: x[0].lower()))
        optionsDict = {helpMatrix[key]['emoji']: (key,helpMatrix[key]['short']) for key in sortedCommands.keys()}
        
        #options = self.view.optionDict(userCommands, [com[0] for com in userCommands.keys()])

        if givencommand not in sortedCommands.keys():
            question, selectedCommandName = await self.view.getHelpChoice(ctx, optionsDict)
            await question.delete()
            
            if selectedCommandName == False:
                bye = await ctx.send("👋")
                await bye.delete(delay=5)
                return 

        else:
            selectedCommandName = givencommand

       
        await self.view.getHelpSpecific(ctx,  selectedCommandName, helpMatrix[selectedCommandName]['desc'], helpMatrix[selectedCommandName]['args'])
        




        

    
    @commands.command()
    @commands.dm_only()
    @commands.check(Controller.EnsureBostoBase)
    @commands.check(Controller.EnsureBostoUser)
    async def settings(self, ctx, *args):
        """
        This is your personal settings panel!
        To use this command type `settings` to view your settings
        
        You can change your settings use the `change` flag by typing `settings change` and follow the prompts

        This allows you to control some specific user settings like when Bosto-Bot sends you notifications. Make sure to check this periodically as more settings will be added!
        
        Optional Arguments:
        ● `change` : FLAG - Get settings editing menu when this flag is used
        """

        args = [arg.lower() for arg in args]
        settings = self.model.getUserSettings(ctx.message.author)
        settingsLocal = self.model.getLocalUserSettings()
        


        if "change" in args:
            question, newSetting = await self.view.getSettingsChangeOption(ctx.message.author, settings, settingsLocal)
            await question.delete()
            
            if newSetting == False:
                bye = await ctx.send("👋")
                await bye.delete(delay=5)
                return
            
            
            question, newSettingValueResponce = await self.view.getSettingsSpecific(ctx.message.author, newSetting, settings[newSetting], settingsLocal)
            await question.delete()
            

            if newSettingValueResponce == False or str(newSettingValueResponce.emoji) == "↪":
                bye = await ctx.send("👋")
                await bye.delete(delay=5)
                return
            
            newSettingValue = {val['emoji']:key for key, val in settingsLocal[newSetting]['options'].items()}[str(newSettingValueResponce.emoji)]

        
            try: 
                self.model.changeUserSetting(newSetting, newSettingValue, ctx.message.author)
            except Exception as err:
                logging.error("Error Updating user setting:\n" + str(err))
                bye = await ctx.send("Error while updating setting! Please tell a mod!")
                await bye.delete(delay=5)
            else:
                bye = await ctx.send("Setting Updated!")
                await bye.delete(delay=5)

        else:
            await self.view.sendSettings(ctx.message.author, settings, settingsLocal, self.model.addTip(user=ctx.message.author, exclude_list=("settings_command")))
            return

        

    

def setup(client):
    client.add_cog(SettingsController(client))