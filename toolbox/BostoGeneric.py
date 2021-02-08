import logging

async def Err(ctx, msg="Try again or let a server mod know"):
    message = f":crying_cat_face:\nMrrrrrrrrr!\n{msg}"
    await ctx.send(message)

async def Info(ctx, msg=""):
    message = f":cat:\nMeow!\n{msg}"
    await ctx.send(message)

# Log Channel Message
async def send_log_channel(client, message):
    channel = client.get_channel(717429756831990102)
    await channel.send(message)

EMOJI_LIST = ('bostopoint', 'bostocoin', 'bostoaward')








