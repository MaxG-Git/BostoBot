import discord
from discord.ext import commands
import logging
import BostoBot.controller.Controller as Controller
from BostoBot.model.WalletModel import WalletModel #!Notice Buy is using wallet model

class BuyController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, WalletModel)

    @commands.command()
    @commands.dm_only()
    @commands.check(Controller.EnsureBostoUser)
    async def buy(self, ctx, *args):
        user = ctx.message.author
        import asyncio
        emojiSelection = await ctx.send("Select The Bosto-Emoji You would like to create - *(or ❌ to cancel)*")

        allEmojis = self.client.BostoDict
        emojiCode = {key: emoji['code'] for key, emoji in allEmojis.items()}
        emojiValue = {key: emoji['value'] for key, emoji in allEmojis.items()}
        emojiCode['cancel'] = "❌"
    
        [await emojiSelection.add_reaction(e) for e in emojiCode.values()]
      
        try:
            payload = await self.client.wait_for('raw_reaction_add', timeout=20.0, \
            check=lambda payload: payload.user_id == ctx.message.author.id and str(payload.emoji) in emojiCode.values())
        except asyncio.TimeoutError:
            await ctx.send("Time Out")
        else:
            await emojiSelection.delete()
            if str(payload.emoji) == "❌":
                cancled = await ctx.send(content="👋")
                await asyncio.sleep(1)
                await cancled.delete()
                return
            
            
            # Desired Emoji Captured 
            selected = str(payload.emoji)
            selectedName = payload.emoji.name
            selectedVal = emojiValue[selectedName]
            graphic = await ctx.send(selected)

            
            # Calculate Available Spending Options
            totalWallet = self.model.getTotalWallet(user=user, convertToDict=True)


            availPayment = []
            for emj in allEmojis.keys():
                if emj != selectedName:
                    if emojiValue[emj] * totalWallet[emj] >= selectedVal:
                        availPayment.append(emojiCode[emj])
            
            if len(availPayment) == 0:
                await graphic.edit(content=f"Looks like you don't have enough points or proper change for a {selected} right now.\n*You can check your points with the `wallet` command or make change by dividing up other Bosto-Emojis*")
                return

            availPayment.append("❌")
            emojiSelection = await ctx.send(f"Please Choose what you want to convert into a {selected} - *(or ❌ to cancel)*")
            emojiSelectionOptions = [await emojiSelection.add_reaction(e) for e in availPayment]
            try:
                payload = await self.client.wait_for('raw_reaction_add', timeout=20.0, check=lambda payload: payload.user_id == ctx.message.author.id and str(payload.emoji) in availPayment)
            except asyncio.TimeoutError:
                await ctx.send("Time Out") #TODO Better message here
            else:
                await emojiSelection.delete()
                if str(payload.emoji) == "❌":
                    await graphic.delete()
                    cancled = await ctx.send(content="👋")
                    await asyncio.sleep(1)
                    await cancled.delete()
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
                    await ctx.send(f"Meow\nLooks like you don't have enough points for a {selected} right now.\nYou have **{costEmojiTotal}** {costEmojiCode}'s you need **{needed}** more for a {selected}")
                    return

                
                msg1 = await ctx.send(f"You Currently have **`{costEmojiTotal}`** {costEmojiCode}\nYou can create a total of {availOptionsString} {selected}")
                msg2 =  await ctx.send(f"Please respond with how many {selected} to create *(or `cancel` to cancel)*")
                try:
                    quantityResponce = await self.client.wait_for('message', timeout=20.0, \
                    check=lambda msg: msg.author.id == ctx.message.author.id and (str(msg.content) in availOptions or str(msg.content).lower() == "cancel"))
                except asyncio.TimeoutError:
                    await ctx.send("Time Out") #TODO Better message here
                else:
                    await msg1.delete()
                    await msg2.delete()
                    if str(quantityResponce.content).lower() == "cancel":
                        await graphic.delete()
                        cancled = await ctx.send(content="👋")
                        await asyncio.sleep(1)
                        await cancled.delete()
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
                        await graphic.edit(content="✅")
    

def setup(client):
    client.add_cog(BuyController(client))