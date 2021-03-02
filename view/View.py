class View:
    
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def error(sendable, msg="Somethings gone wrong, Try again or let a server mod know" ):
        message = f":crying_cat_face:\nMrrrrrrrrr!\n{msg}"
        return await sendable.send(message)

    @staticmethod
    async def info(sendable, msg=""):
        message = f":cat:\nMeow!\n{msg}"
        return await sendable.send(message)

    @staticmethod
    async def send(sendable, *args, **kwargs):
        return await sendable.send(*args, **kwargs)


    



    