from BostoBot.view.View import *
import discord

class SettingsView(View):

    def __init__(self, client):
        super().__init__(client)


    async def getHelpChoice(self, ctx, options : dict):
        optList = ["● {} {}".format(key, val) for key, val in options.items()]
        embed = discord.Embed(
            title="Help",
            description="Below is a list of all commands.\nYou **click on the reaction that corresponds with a command** to get more info on the command\n",
            color = 0x738ADD
        )
        embed.set_thumbnail(url="https://emoji.gg/assets/emoji/3224_info.png")
        embed.set_footer(text="Please select an option from the list above or ❌ to cancel")
        embed.add_field(name="Commands", value="\n".join(optList), inline=True)
        action = Action(
            check=lambda payload: payload.user_id == ctx.message.author.id,
            action='raw_reaction_add',
            reaction_options=options.keys(),
            )
        options['❌'] = False
        return await self.getResponce(ctx, 
        actions=action,
        embed=embed,
        condition= lambda result: options[str(result.emoji)]
        )

    async def getHelpSpecific(self, ctx, name, desc):
        embed = discord.Embed(
            title= name.capitalize() +  " Command",
            description= desc,
            color = 0x738ADD
        )
        embed.set_thumbnail(url="https://emoji.gg/assets/emoji/3224_info.png")
       
        return await ctx.send(embed=embed)

        

    
    async def sendSettings(self, user, settings, settingsLocal):
        embed = discord.Embed(
            title="Your Settings",
            description="The following are your personal Bosto-Bot settings\nChange any of your settings by typing: `settings change`",
            color=0xFF5733
        )
        embed.set_thumbnail(url="https://emoji.gg/assets/emoji/5053_Gears.png")
        for key, val in settingsLocal.items():
            embed.add_field(name=val['name'], value = self.onOffLabel(settings[key]))
        await user.send(embed=embed)

    
    async def getSettingsChangeOption(self, user, settings, settingsLocal):
       
        
        #small_letters = dict(zip(list(map(chr, range(ord('a'), ord('a')+len(settings.keys())))), settings.keys()))
        settingList = self.optionDict(settingsLocal.keys())
    
        optList = ["● {} {}".format(key, settingsLocal[val]['name']) for key, val in settingList.items()]
        settingList["❌"] = False

        embed = discord.Embed(
            title="Which setting would you like to change?",
            description="\n".join(optList),
            color=0xFF5733
        )
        embed.set_thumbnail(url="https://emoji.gg/assets/emoji/5053_Gears.png")
        embed.set_footer(text="Please respond with the letter that coressponds to the setting you want to change\nClick ❌ to cancel")
        action = Action(
            check= lambda payload: payload.user_id == user.id,
            reaction_options=settingList.keys(),
            action='raw_reaction_add',
        )
        return await self.getResponce(user, embed=embed, actions=action, condition=lambda payload: settingList[str(payload.emoji)])

    async def getSettingsSpecific(self, user, setting, currentValue, settingsLocal):
        currentValue = settingsLocal[setting]['options'][currentValue]['value']
        embed = discord.Embed(
            title = settingsLocal[setting]['name'],
            description=settingsLocal[setting]['desc'] + "\nThis setting is currently set to:\n**{}**".format(currentValue),
            color=0xFF5733
        )
        optList = ["> {}: {}".format(val['emoji'], val['value']) for val in settingsLocal[setting]['options'].values()]
        embed.add_field(name="Please Choose an option", value="\n".join(optList))
        embed.set_thumbnail(url="https://emoji.gg/assets/emoji/5053_Gears.png")
        embed.set_footer(text="Click ↪ to cancel")
        action = Action(
            check= lambda payload: payload.user_id == user.id,
            reaction_options = [val['emoji'] for val in settingsLocal[setting]['options'].values()]+["↪"],
            action='raw_reaction_add',
            
        )
        return await self.getResponce(user, embed=embed, actions=action)

 

    

   
    @staticmethod
    def onOffLabel(value):
        return ":white_check_mark:" if value == "TRUE" else "❌"