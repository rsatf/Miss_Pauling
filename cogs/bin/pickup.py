import random
from cogs.bin.player import Player

class Game():

    def __init__(self, teams: int = 2, mode="6v6") -> None:
        self.empty_slot = "?"
        self.teams_count = teams
        self.mode = None
        self.team_size = None
        self.teams = None
        self.max_players = None
        self.players_added = None
        self.game_on = False

    def start(self, teams: int = 2, mode="6v6") -> None:
        if self.game_on is True:
            raise GameOnError("Game already on.")

        self.teams_count = teams
        self.mode = mode
        if type(mode) == int:
            self.team_size = mode
        elif type(mode) == str:
            if mode == "2v2":
                self.team_size = 2
            elif mode == "6v6":
                self.team_size = 6
            elif mode == "7v7":
                self.team_size = 7
            elif mode == "9v9":
                self.team_size = 9
            else:
                self.team_size = 6
        self.teams = [[self.empty_slot for x in range(self.team_size)] for i in range(self.teams_count)]
        self.max_players = self.team_size * self.teams_count
        self.players_added = 0
        self.game_on = True
        return

    def stop(self):
        if self.game_on is False:
            raise GameOnError("No game on.")

        self.mode = None
        self.team_size = None
        self.teams = None
        self.max_players = None
        self.players_added = None
        self.game_on = False
        return

    def restart(self, teams: int = 2, mode="6v6"):
        self.stop()
        self.start(teams=teams, mode=mode)
        return
    
    def status(self) -> str:
        if self.game_on is False:
            raise GameNotOnError("No game on.")

        team_count = 0
        all_teams = ""
        for team in self.teams:
            team_count += 1
            team_lineup = []
            team_empty = []
            for player in team:
                if player != self.empty_slot:
                    team_lineup.append(player.name)
                else:
                    team_empty.append(player)
            all_teams += f"Team {team_count} [{len(team_lineup)}/{len(team)}] Players: ({'), ('.join(team_lineup + team_empty)}"
            all_teams += ") "
        return all_teams

    # def add(self, player: Player, team: int = None) -> None:
    def add(self, player, team: int = None) -> None:
        if self.game_on is False:
            raise GameNotOnError("No game on.")

        if any(player in x for x in self.teams):
            raise PlayerAddedError("Player already added.")

        eligible_teams = []
        for index, _ in enumerate(self.teams):
            if not self._is_full(self.teams[index]):
                eligible_teams.append(index)

        if len(eligible_teams) == 0:
            raise GameFullError("The game is full.")

        if team is None:
            selected_team = self.teams[random.choice(eligible_teams)]
        elif team > self.teams_count:
            raise InvalidTeamError("Invalid team selected.")
        elif team - 1 not in eligible_teams:
            raise TeamFullError("Team is full.")
        else:    
            selected_team = self.teams[team - 1]

        for index, slot in enumerate(selected_team):
            if slot == self.empty_slot:
                selected_team[index] = player
                break
        self.players_added += 1
        return

    def remove(self, player: Player) -> None:
        if self.game_on is False:
            raise GameNotOnError("No game on")

        if not any(player in x for x in self.teams):
            raise PlayerNotAddedError("Player is not added.")
        
        for index, _ in enumerate(self.teams):
            if player in self.teams[index]:
                self.teams[index] = [self.empty_slot if x == player else x for x in self.teams[index]]
        return

    def transform(self, teams: int = 2, mode="6v6") -> None:
        if self.game_on is False:
            raise GameNotOnError("No game on")

        players = []
        for index, _ in enumerate(self.teams):
            for _, player in enumerate(self.teams[index]):
                if player != self.empty_slot:
                    players.append(player)

        if type(mode) == int:
            self.team_size = mode
        elif type(mode) == str:
            if mode == "2v2":
                self.team_size = 2
            elif mode == "6v6":
                self.team_size = 6
            elif mode == "7v7":
                self.team_size = 7
            elif mode == "9v9":
                self.team_size = 9
            else:
                self.team_size = 6

        if len(players) > teams * self.team_size:
            raise CannotTransformError("Target game size too small.")

        self.stop()
        self.start(teams, mode)
        for player in players:
            self.add(player)
        return

    def balance(self) -> None:
        if self.game_on is False:
            raise GameNotOnError("No game on")

        pool = []
        new_teams = []
        # Adds all players to the pool list
        for team in self.teams:
            for player in team:
                if player != self.empty_slot:
                    pool.append(player)

        # Sorts the pool list, highest rating first
        pool.sort(key=lambda x: x.rating, reverse=True)

        # Adds the right amount of empty lists to new_teams as there are current teams
        for _ in range(len(self.teams)):
            new_teams.append([])

        for player in range(len(pool)):
            # We put the highest rating player in the first team
            new_teams[0].append(pool.pop(0))
            # We sort the teams such that the lowest ranked team becomes new_teams[0]
            # So that we can add the next highest skilled player to that team
            new_teams.sort(key=lambda x: sum(i.rating for i in x), reverse=False)
            # print(new_teams)
        self.teams = new_teams
        return

    def _team_count(self, team: list) -> int:
        player_count = 0
        for player in team:
            if player != self.empty_slot:
                player_count += 1
        return player_count
    
    def _is_full(self, team: list) -> bool:
        if self._team_count(team) == len(team):
            return True
        else:
            return False

# Errors

class InvalidTeamError(ValueError):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        # self.errors = errors

class TeamFullError(ValueError):
    def __init__(self, message):

        super().__init__(message)

class PlayerAddedError(ValueError):
    def __init__(self, message):

        super().__init__(message)

class PlayerNotAddedError(ValueError):
    def __init__(self, message):

        super().__init__(message)

class GameFullError(ValueError):
    def __init__(self, message):

        super().__init__(message)

class GameOnError(ValueError):
    def __init__(self, message):

        super().__init__(message)

class GameNotOnError(ValueError):
    def __init__(self, message):

        super().__init__(message)

class CannotTransformError(ValueError):
    def __init__(self, message):

        super().__init__(message)