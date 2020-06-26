import discord
import random

class Player():
    
    def __init__(self, nick: str, elo: int):
        self.nick = nick
        self.elo = elo

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
        self.start(teams, mode)
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
                    team_lineup.append(player.nick)
                else:
                    team_empty.append(player)
            all_teams += f"Team {team_count} [{len(team_lineup)}/{len(team)}] Players: ({'), ('.join(team_lineup + team_empty)}"
            all_teams += ") "
        return all_teams

    def add(self, player: Player, team: int = None) -> None:
        if self.game_on is False:
            raise GameNotOnError("No game on.")

        if any(player in x for x in self.teams):
            raise PlayerAddedError("Player already added.")

        eligible_teams = []
        for index, value in enumerate(self.teams):
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
        
        for index, value in enumerate(self.teams):
            if player in self.teams[index]:
                self.teams[index] = [self.empty_slot if x == player else x for x in self.teams[index]]
        return

    def transform(self, teams: int = 2, mode="6v6") -> None:
        if self.game_on is False:
            raise GameNotOnError("No game on")

        players = []
        for index, value in enumerate(self.teams):
            for slot, player in enumerate(self.teams[index]):
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

def main():
    if __name__ == "__main__":
        game = Game()
        russ = Player("Russ", 1500)
        skiba = Player("skiba", 1500)
        biltong = Player("biltong", 1500)
        ployful = Player("ployful", 1500)
        auto = Player("auto", 1500)
        wanderer = Player("wanderer", 1500)
        fluff = Player("fluff", 1500)
        spoon = Player("spoon", 1500)
        gimlief = Player("gimlief", 1500)
        beetle = Player("beetle", 1500)
        jan = Player("jan", 1500)
        chrome = Player("chrome", 1500)
        skye = Player("skye", 1500)
        cod = Player("cod", 1500)
        try:
            game.start(2, 6)
        except GameOnError as e:
            print(f"Error: {e}")
        # game.add(russ)
        # print(game.status())
        # game.stop()
        # game.start(2, 6)
        # print(game.status())

        try:
            game.add(russ, 1)
            game.add(biltong, 1)
            game.add(ployful, 1)
            game.add(auto, 1)
            game.add(wanderer, 1)
            game.add(skiba, 1)
            game.add(fluff)
            game.add(spoon)
            game.add(gimlief)
            game.add(beetle)
            game.add(jan)
            game.add(chrome)
            # game.add(skye)
            # game.add(cod)
            # game.add(russ)
            # game.add(biltong)
            # game.add(ployful)
            # game.add(auto)
            # game.add(wanderer)
            # game.add(skiba)
            # game.add(fluff)
        except (InvalidTeamError, TeamFullError, PlayerAddedError, GameFullError)as e:
            print(f'Error: {e}')
        # print(game.status())
        # game.remove(russ)
        print(game.status())
        try:
            game.transform(1, 12)
        except CannotTransformError as e:
            print(f'Error: {e}')
        print(game.status())

main()