import discord

class Player():
    
    def __init__(self, player: discord.Member, rating: int):
        self.player = player
        self.id = player.id
        self.nick = player.nick
        self.name = player.name
        self.mention = player.mention
        self.display_name = player.display_name
        # self.descriminator = player.descriminator
        # self.dm_channel = player.dm_channel
        self.rating = rating
        self.steamid = None