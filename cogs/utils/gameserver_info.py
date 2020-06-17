import valve.source.a2s
from . import db

servers = [('jhb1.rsa.tf', 27035), ('jhb1.rsa.tf', 27025)]

# def check_servers(self):
#     for address in servers:
#         with valve.source.a2s.ServerQuerier(address) as server:
#             try:
#                 info = server.get_info()
#                 if info['player_count'] < 1:
#                     open_server = (server.host, server.port)
#         return open_server
# active_server = check_servers()
# if active_server == None:
#     return f'No empty server to use, perhaps wait for a game to finish or organise another server.'
# active_password = "games"
# connect_string = f'password {active_password}; connect {active_server[0]}:{active_server[1]}'