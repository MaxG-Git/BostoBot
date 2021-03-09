import discord
from discord.ext import commands
import logging
import BostoBot.controller.Controller as Controller
from BostoBot.model.PointModel import PointModel 
from BostoBot.view.PointView import PointView
import matplotlib.font_manager as font_manager

class BuyController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, PointModel, PointView)


    

    
    @commands.command()
    @commands.dm_only()
    @commands.check(Controller.EnsureBostoBase)
    @commands.check(Controller.EnsureBostoUser)
    async def wallet(self, ctx, *args):
        """
        This command will show you an image of your **current** wallet.

          Optional Arguments:
          ● `v` : FLAG - This flag argument can be added in to see Bosto-Point's Values

        """
        user = ctx.message.author
        path = "/usr/src/app/data/wallet.png"
        image = discord.File(path)
        totalWallet = self.model.getTotalWallet(user=user, convertToDict=True)
        prop = font_manager.FontProperties(fname="/usr/src/app/data/fonts/uni-sans.heavy-caps.ttf")
        args = [arg.lower() for arg in args]


        def marker(ax, textX, textY, name):
            ax.text(textX, textY, "× " + str(totalWallet[name.lower()]), fontsize = 40, color = 'white', fontproperties = prop)
            multidigit = ((len(str(self.model.BostoPoints[name]['value'])) - 1) * 0.005) 
            valX, valY = textX - (0.08 + multidigit), textY - 0.165
            if "v" in args:
                ax.text(valX, valY, str(self.model.BostoPoints[name]['value']), fontsize = 25, color = '#AD6556')
                ax.text(textX - 0.0738 + (multidigit * 0.1), textY - 0.2, "BP", fontsize = 15, color = '#AD6556')
           

        if not self.model.GraphPoints(path, marker=marker): return await self.view.error(ctx)
      
        
        
        try:
            await self.view.sendWallet(user, image=image, tip=self.model.addTip(user=user, require_list=('wallet')))
        except Exception as err:
            logging.error("Error while creating/saving wallet graphic")
            logging.error(str(err))
            await user.send(content="Somethings gone wrong") #TODO BETTER MESSAGE
    
    
                
               


    @commands.command()
    @commands.dm_only()
    @commands.check(Controller.EnsureBostoBase)
    @commands.check(Controller.EnsureBostoUser)
    async def value(self, ctx, *args):
        """
        This command will show you an image of Bosto-Point **Values**.
        Bosto-Point values is what Bosto-Bot uses to determine what to trade you when using the `trade` command
        """
        user = ctx.message.author
        path = "/usr/src/app/data/value.png"
        image = discord.File(path)
        prop = font_manager.FontProperties(fname="/usr/src/app/data/fonts/uni-sans.heavy-caps.ttf")

        if not self.model.GraphPoints(path, 
            marker = lambda ax, textX, textY, name: ax.text(
                textX,
                textY,
                str(self.model.BostoPoints[name]['value']),
                fontsize = 35,
                color = '#AD6556',
                )
            ): return await self.view.error(ctx)
        try: # #AD6556
            
            await user.send(file=image, content="BostoPoint Values:")
        except Exception as err:
            logging.error("Error while creating/saving wallet graphic")
            logging.error(str(err))
            await user.send(content="Somethings gone wrong") #TODO BETTER MESSAGE
        
    
    
    
    
    @commands.command()
    @commands.dm_only()
    @commands.check(Controller.EnsureBostoBase)
    @commands.check(Controller.EnsureBostoUser)
    async def trade(self, ctx, *args):
        """
        Using this command you can trade your Bosto-Points for other types of points!

        To get started just type `trade` and follow the prompts that follow. When trading Bosto-Points, Bosto-Bot
        will only trade based on the value the particular Bosto-Point. To see the different values of Bosto-Points you can use the `value` command
        
        """
        user = ctx.message.author
        import asyncio
        

        allEmojis = self.model.BostoPoints
        emojiCode = {key: emoji['code'] for key, emoji in allEmojis.items()}
        emojiValue = {key: emoji['value'] for key, emoji in allEmojis.items()}
        emojiCode['cancel'] = "❌"
        tradeOptions = list(emojiCode.values())[1:]
      
        emojiSelection, payload = await self.view.tradeGetSelected(ctx, tradeOptions
        )

        await emojiSelection.delete()
       

        if payload == False or str(payload.emoji) == "❌":
            cancel = await ctx.send(content="👋")
            await cancel.delete(delay=1.5)
            return
        
            
        # Desired Emoji Captured 
        selected = str(payload.emoji)
        selectedName = payload.emoji.name
        selectedVal = emojiValue[selectedName]
        selectedUrl = str(payload.emoji.url)
        graphic = await ctx.send(selected)
        
        # Calculate Available Spending Options
        totalWallet = self.model.getTotalWallet(user=user, convertToDict=True)
        availPayment = []
        for emj in allEmojis.keys():
            if emj != selectedName:
                if emojiValue[emj] * totalWallet[emj] >= selectedVal:
                    availPayment.append(emojiCode[emj])
        
        if len(availPayment) == 0:
            cantBuy = await graphic.edit(content=f"Looks like you don't have enough points or proper change for a {selected} right now.\n*You can check your points with the `wallet` command or make change by dividing up other Bosto-Emojis*")
            return await graphic.delete(delay=7)
        
        availPayment.append("❌")

        emojiSelection, payload = await self.view.tradeGetCost(ctx, selected, selectedVal, availPayment, selectedUrl)
        '''
        emojiSelection, payload = await self.view.getResponce(ctx, 
            replyFilter=lambda payload: payload.user_id == ctx.message.author.id, 
            question= f"*Trading for {selected} (value: {selectedVal})*\nPlease Choose what you want to **offer me** for {selected}(s) - *(or ❌ to cancel)*",
            reactionOptions= availPayment,
            clearReactions=False,
            action='raw_reaction_add'
            )
        '''

        await emojiSelection.delete()
        
        if payload == False or str(payload.emoji) == "❌":
            await graphic.delete()
            cancel = await ctx.send(content="👋")
            await cancel.delete(delay=1.5)
            return
            
        

        costEmoji = payload.emoji.name
        costEmojiCode = str(payload.emoji)
        costEmojiVal = emojiValue[costEmoji]
        costEmojiTotal = totalWallet[costEmoji]
        await graphic.edit(content=f"{costEmojiCode} ➡️ {selected}")
        costEmojiTotalValue = costEmojiVal * costEmojiTotal
        availMax = costEmojiTotalValue // selectedVal
        availOptions = []
        availOptionsString = "" 
        for i in range(1, availMax+1):
            if  (i * selectedVal) % costEmojiVal == 0: 
                availOptions.append(str(i))
                if len(availOptions) < 70:
                    availOptionsString += "**`"+str(i)+"`**, " if i != availMax else "or **`"+str(i)+"`**"
                elif len(availOptions) == 70:
                    availOptionsString+="..."
        if availMax == 0:
            needed = (selectedVal-costEmojiTotalValue) // costEmojiVal
            cantBuy = await ctx.send(f"Meow\nLooks like you don't have enough points for a {selected} right now.\nYou have {costEmojiTotal} {costEmojiCode}'s you need **{needed}** more for a {selected}")
            return await cantBuy.delete(delay=5)
        '''
        #await textGraphic.edit(content=f"Trading with {costEmojiCode} *(value: {costEmojiTotalValue})*  ➡  Trading for {selected} *(value: {selectedVal})*")
        msg1 = await ctx.send(f"*Trading with {costEmojiCode} (value: {costEmojiVal})*  ➡  *Trading for {selected} (value: {selectedVal})*\nYou have {costEmojiTotal} {costEmojiCode}\nYou can create a total of {availOptionsString} {selected}")
        
        msg2, quantityResponce = await self.view.getResponce(ctx, 
            replyFilter=lambda msg: msg.author.id == ctx.message.author.id and (str(msg.content) in availOptions or str(msg.content).lower() == "cancel"),
            question= f"Please respond with how many {selected} to create *(or `cancel` to cancel)*",
            timeout=30.0,
            clearReactions=False,
            )
        '''
        quantityMessage, quantityResponce = await self.view.tradeGetQuant(ctx, selected, selectedVal, costEmojiCode, costEmojiVal, costEmojiTotal, availOptions, availOptionsString, selectedUrl)
        
        
        #await textGraphic.delete(delay=0.5)

            
        if quantityResponce == False:
            await graphic.delete()
            await quantityMessage.delete(delay=4)
            return

      
        await quantityMessage.delete(delay=0.2)    
            
            
        if isinstance(quantityResponce, discord.RawReactionActionEvent) and str(quantityResponce.emoji) == "❌":
            await graphic.delete()
            cancel = await ctx.send(content="👋")
            await cancel.delete(delay=1.5)
            return

        quant = int(quantityResponce.content)
        totalPriceVal = quant * selectedVal
        costPrice = totalPriceVal // costEmojiVal
             
        loadString = ""
        for i in range(0, 3):
            loadString+= "🔄 "
            await graphic.edit(content=loadString)
            await asyncio.sleep(1)
            
        try:
            logging.info(f"Attempting removing {costPrice} {costEmoji} and adding {quant} {selectedName}")
            self.model.decrementWallet(costEmoji, user.id, int(costPrice))
            self.model.incrementWallet(selectedName, user.id, int(quant))
        except Exception as err:
            await graphic.edit(content="❌") #TODO Better message here
            logging.error(str(err))
        else:
            await self.view.tradeReceipt(graphic, selected, quant, costEmojiCode, costPrice, self.model.addTip(user=user))


def setup(client):
    client.add_cog(BuyController(client))