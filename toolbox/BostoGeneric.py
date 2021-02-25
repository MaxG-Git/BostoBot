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

def first(iterable, default, condition = lambda x: True, filter_true = None, filter_false = None):
    try:
        if filter_true == None:
            return next(x for x in iterable if condition(x))
        else:
            return filter_true(next(x for x in iterable if condition(x)))
    except StopIteration:
        if filter_false == None:
            return default
        else:
            return filter_false(default)
        
            

EMOJI_LIST = ('bostopoint', 'bostocoin', 'bostoaward')








