import logging
import mysql.connector as mysql
import BostoBot.toolbox.creds as creds



def sql_logger(origin):
    def wrapper(*args, **kwargs):
        result = origin(*args, **kwargs)
        logging.info('SQL Request: ' + result.sql%result.vals)
        return result
    return wrapper
    

def commit_completion(origin):
    def wrapper(*args, **kwargs):
        result = origin(*args, **kwargs)
        result.connection.commit()
        result.reset()
        return 
    return wrapper

def first_result_completion(origin):
    def wrapper(*args, **kwargs):
        result = origin(*args, **kwargs)
        fetched = result.cursor.fetchone()

        result.reset()
        return fetched[0] if isinstance(fetched, tuple) and len(fetched) > 0 else None
    return wrapper


def first_row_completion(origin):
    def wrapper(*args, **kwargs):
        result = origin(*args, **kwargs)
        fetched = result.cursor.fetchone()
        result.reset()
        return fetched if isinstance(fetched, tuple) and len(fetched) > 0 else None
    return wrapper

def fetch_all_completion(origin):
    def wrapper(*args, **kwargs):
        result = origin(*args, **kwargs)
        fetched = result.cursor.fetchall()
        result.reset()
        return fetched if isinstance(fetched, list) and len(fetched) > 0 else None
    return wrapper


class BostoConnect():
    def __init__(self):
        self.connected = False
        self.connection = None
        self.connect()
        
    def connect(self):
        self.connection = mysql.connect(
         host = creds.MYSQL_HOST,
         port = creds.MYSQL_PORT,
         user = creds.MYSQL_USER,
         passwd = creds.MYSQL_PASS,
         database = creds.MYSQL_DATABASE
        )
        self.connected = True
        self.sql = ""
        self.vals = ()
        self.cursor = self.connection.cursor(buffered=True)

    def reset(self):
        self.cursor = self.connection.cursor(buffered=True)
        self.sql = ""
        self.vals = ()

    def close(self):
        self.cursor.close()

    def GetPoints(self):
        import json
        abs_file_path = "/usr/src/app/data/settings.json"
        logging.info("Json Request: "+abs_file_path)
        with open(abs_file_path) as f:
            settings = json.load(f)
        return settings['points']

    @fetch_all_completion
    @sql_logger
    def getAllEmojis(self):
        self.sql = "SELECT `name`, `code`, `value` FROM `types` ORDER BY `value` ASC"
        self.cursor.execute(self.sql)
        return self

    @commit_completion
    @sql_logger
    def addUser(self, _id, name, discriminator, bot, nick):
        self.vals = [str(i) for i in [_id, name, discriminator, bot, nick]]
        self.sql = "INSERT INTO users (id, name, discriminator, bot, nick) VALUES ({}, {}, {}, {}, {})".format(*self.vals)
        self.cursor.execute(self.sql)
        return self

    @commit_completion
    @sql_logger
    def updateUser(self, _id, name, discriminator, bot, nick):
        self.vals = [str(i) for i in [name, discriminator, bot, nick, _id]]
        self.sql = "UPDATE `users` SET `name` = {}, `discriminator` = {}, `bot` = {}, `nick` = {} WHERE `id` = {}".format(*self.vals)
        logging.info(self.sql)
        self.cursor.execute(self.sql)
        return self

    @commit_completion
    @sql_logger
    def addWallet(self, userId):
        cols = list(map(lambda emoji: f"`{emoji}s`", tuple(self.GetPoints().keys())))
        allCols = ", ".join(cols)
        self.sql = f"INSERT INTO `wallet` (`id`, {allCols}) VALUES ('{userId}', 0, 0, 0);"
        self.cursor.execute(self.sql)
        return self

    @commit_completion
    @sql_logger
    def editUser(self, field, value, author=None, authorId=None):
        if author is None and authorId is None: return False
        if authorId is None: authorId = author.id
        if isinstance(value, str): value = "'" + value + "'"
        self.vals = (field, value, authorId)
        self.sql = "UPDATE users SET %s = %s WHERE id = %s"
        self.cursor.execute(self.sql, self.vals)
        return self


    @commit_completion
    @sql_logger
    def addReaction(self, authorId, reacterId, messageId, emojiType):
        self.vals = (authorId, reacterId, messageId, emojiType)
        self.sql = "INSERT INTO `reactions` (`id`, `author`, `reacter`, `messageId`, `type`) VALUES (NULL, %s, %s, %s, %s);"
        self.cursor.execute(self.sql, self.vals)
        return self


    @first_result_completion
    @sql_logger
    def getPointId(self, authorId, reacterId, messageId, emojiName):
        self.vals = (authorId, reacterId, messageId, emojiName)
        self.sql = "SELECT `id` FROM `reactions` WHERE `author` = %s AND `reacter` = %s AND `messageId` = %s AND `type` = %s"
        self.cursor.execute(self.sql, self.vals)
        # self.cursor.reset()
        return self

    @first_result_completion
    @sql_logger
    def checkUser(self, userId):
        self.sql = f"SELECT COUNT(`id`) FROM `users` WHERE `id` = {userId}"
        self.cursor.execute(self.sql)
        return self

    @first_result_completion
    @sql_logger
    def isAdmin(self, userId):
        self.sql = f"SELECT `is_admin` FROM `users` WHERE `id` =  {userId}"
        self.cursor.execute(self.sql)
        return self

    @commit_completion
    @sql_logger
    def removePoint(self, pointId):
        self.sql= f"DELETE FROM `reactions` WHERE `reactions`.`id` = {pointId}" 
        self.cursor.execute(self.sql)
        return self


    @first_result_completion
    @sql_logger
    def countPoints(self, userId):
        self.sql= f"SELECT COUNT(*) FROM `reactions` WHERE `author` = '{userId}'" 
        self.cursor.execute(self.sql)
        return self


    @first_result_completion
    @sql_logger
    def getWallet(self, reactionType, userId):
        
        if reactionType not in tuple(self.GetPoints().keys()):
            return logging.error(f"Unknown field type when adding to wallet: {reactionType}")
            
        reactionType = reactionType + "s"
        self.sql= f"SELECT `{reactionType}` FROM `wallet` WHERE `id` = {userId}" 
        self.cursor.execute(self.sql)
        return self
    

    @first_row_completion
    @sql_logger
    def getTotalWallet(self,  userId):
        cols = list(map(lambda emoji: f"`{emoji}s`", tuple(self.GetPoints().keys())))
        allCols = ", ".join(cols)
        self.sql= f"SELECT {allCols} FROM `wallet` WHERE `id` = {userId}" 
        self.cursor.execute(self.sql)
        return self

    

    @commit_completion
    @sql_logger
    def incrementWallet(self, reactionType, userId, cost=1):
        
        if reactionType not in tuple(self.GetPoints().keys()):
            return logging.error(f"Unknown field type when adding to wallet: {reactionType}")
            
        reactionType = reactionType + "s"
        self.sql= f"UPDATE `wallet` SET `{reactionType}` = `{reactionType}` + {cost} WHERE `id` = {userId}" 
        self.cursor.execute(self.sql)
        return self

    @commit_completion
    @sql_logger
    def decrementWallet(self, reactionType, userId, cost=1):
        
        if reactionType not in tuple(self.GetPoints().keys()):
            return logging.error(f"Unknown field type when adding to wallet: {reactionType}")
            
        reactionType = reactionType + "s"
        self.sql= f"UPDATE `wallet` SET `{reactionType}` = `{reactionType}` - {cost} WHERE `id` = {userId}" 
        self.cursor.execute(self.sql)
        return self


    @first_result_completion
    @sql_logger
    def getEmojiCode(self, name):
        self.sql= f"SELECT `code` FROM `types` WHERE `name` = '{name}'" 
        self.cursor.execute(self.sql)
        return self

    @first_result_completion
    @sql_logger
    def getEmojiName(self, code):
        self.sql= f"SELECT `name` FROM `types` WHERE `code` = '{code}'" 
        self.cursor.execute(self.sql)
        return self

    @first_result_completion
    @sql_logger
    def getEmojiValue(self, name):
        self.sql= f"SELECT `value` FROM `types` WHERE `name` = '{name}'" 
        self.cursor.execute(self.sql)
        return self
    

    @commit_completion
    @sql_logger
    def deleteReactionByMessageId(self, messageId):
        self.sql= f"DELETE FROM `reactions` WHERE `messageId` = {messageId}" 
        self.cursor.execute(self.sql)
        return self

    @first_result_completion
    @sql_logger
    def countReactionByMessageId(self, messageId):
        self.sql= f"SELECT COUNT(*) FROM `reactions` WHERE `messageId` = {messageId}" 
        self.cursor.execute(self.sql)
        return self
    
    
    @fetch_all_completion
    @sql_logger
    def getScoreBoard(self, pointValues: dict):
        pvTemp = []
        for key, value in pointValues.items():
            pvTemp.append(f"(`{key}s` * {value})")
        pointValueString = " + ".join(pvTemp)
        self.sql=f'SELECT @rank := @rank +1 AS "Ranking", IFNULL( `users`.`nick`, CONCAT( `users`.`name`, "#", `users`.`discriminator` ) ) AS "User", {pointValueString} AS "Total Bosto-Point Value" FROM `wallet` JOIN `users` ON `users`.`id` = `wallet`.`id` ORDER BY 3 DESC LIMIT 10'
        self.cursor.execute("SET @rank=0;")
        self.cursor.execute(self.sql)
        return self


    @fetch_all_completion
    @sql_logger
    def getPointTimeStatReceived(self, userId, days):
        self.sql="SELECT DATE(`reactions`.`time`) AS \"Date\", SUM(`types`.`value`) AS \"Points Recieved\" FROM `reactions` JOIN `types` ON `types`.`name` = `reactions`.`type` WHERE `reactions`.`author` = {} AND `reactions`.`time` BETWEEN CURRENT_TIMESTAMP() - INTERVAL {} DAY AND CURRENT_TIMESTAMP() GROUP BY 1 ORDER BY 1".format(str(userId), days)
        self.cursor.execute(self.sql)
        return self
    
    @fetch_all_completion
    @sql_logger
    def getPointTimeStatGiven(self, userId, days):
        self.sql="SELECT DATE(`reactions`.`time`) AS \"Date\", SUM(`types`.`value`) AS \"Points Given\" FROM `reactions` JOIN `types` ON `types`.`name` = `reactions`.`type` WHERE `reactions`.`reacter` = {} AND `reactions`.`time` BETWEEN CURRENT_TIMESTAMP() - INTERVAL {} DAY AND CURRENT_TIMESTAMP() GROUP BY 1 ORDER BY 1".format(str(userId), days)
        self.cursor.execute(self.sql)
        return self

    

   








        

