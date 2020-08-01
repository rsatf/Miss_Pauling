import discord
import json
from json import JSONEncoder

# class Player():

#     def __init__(self, player, rating: int): 
#         self.player = player
#         self.rating = rating

class Player():
 
    def __init__(self, player: discord.Member, rating: int, steamid):
        self.player = player
        self.id = id
        self.mention = player.mention
        self.display_name = player.display_name
        self.rating = rating
        self.steamid = steamid

    def __str__(self):
        return str(self.display_name)

    __repr__ = __str__