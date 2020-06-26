from itertools import permutations
from itertools import combinations
import random
from operator import itemgetter

class Player():

    def __init__(self, name: str, elo: int):
        self.name = name
        self.elo = elo

sample = []

for i in range(12):
    name = f'Player {i}'
    elo = random.randint(1500, 1600)
    sample.append(Player(name=name, elo=elo))

sample.sort(key=lambda x: x.elo, reverse=True)

team_count = 3
all_teams = []
for i in range(team_count):
    all_teams.append([])

for item in sample:
    all_teams[0].append(sample.pop(0))
    all_teams.sort(key=lambda x: sum(list(x.elo for x in all_teams)), reverse=False)
    print(all_teams)

# WORKED
# for item in sample:
#     all_teams[0].append(sample.pop(0).elo)
#     all_teams.sort(key=lambda x: sum(x), reverse=False)
#     print(all_teams)

# FAILED
# for item in sample:
#     all_teams[0].append(sample.pop(0))
#     all_teams.sort(key=lambda x: sum(x.elo for x in all_teams), reverse=False)
#     print(all_teams)

# totals = []
# for team in all_teams:
#     totals.append(sum(team))

# smol = min(totals)
# bic = max(totals)

# print(f"Difference: {bic - smol}")

# all_teams[0].append(sample[0])
# all_teams[0].append(sample[1])
# all_teams[0].append(sample[2])
# all_teams[0].append(sample[3])
# all_teams[0].append(sample[4])
# all_teams[0].append(sample[5])
# all_teams[1].append(sample[6])
# all_teams[1].append(sample[7])
# all_teams[1].append(sample[8])
# all_teams[1].append(sample[9])
# all_teams[1].append(sample[10])
# all_teams[1].append(sample[11])

# for team in all_teams:
#     print(team)
# print(sum((x.elo for x in all_teams[0])))