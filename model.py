import logging


class Player:
    def __init__(self, playerID, gold, name, alive=True):
        self.playerID = playerID
        self.gold = gold
        self.alive = alive
        self.name = name
        self.minion_kills = 0
        self.player_kills = 0
        self.assists = 0
        self.dragon_kills = 0
        self.turret_destroys = 0

    def to_dict(self):
        return {
            'player_id': self.playerID,
            'gold': self.gold,
            'alive': self.alive,
            'name': self.name,
            'minion_kills': self.minion_kills,
            'player_kills': self.player_kills,
            'assists': self.assists
        }

class Team:
    def __init__(self, teamID, players):
        self.teamID = teamID
        self.players = players
        self.turret_kills = 0
        self.dragon_kills = 0

    def to_dict(self):
        return {
            'teamID': self.teamID,
            'players': [player.to_dict() for player in self.players]
        }


class Game:
    def __init__(self, matchID, fixture, teams):
        self.matchID = matchID
        self.fixture = fixture
        self.teams = teams
        self.winning_team = None
        self._player_cache = {}
        self._team_cache = {}

    def get_team(self, teamID):
        if teamID is None:
            return None

        if teamID in self._team_cache:
            return self._team_cache[teamID]

        for team in self.teams:
            if team.teamID == teamID:
                self._team_cache[teamID] = team
                return team

    def get_player(self, playerID):
        if playerID is None:
            return None

        if playerID in self._player_cache:
            return self._player_cache[playerID]

        for team in self.teams:
            for player in team.players:
                if player.playerID == playerID:
                    self._player_cache[playerID] = player
                    return player

    def to_dict(self):
        return {
            'matchID': self.matchID,
            'fixture': self.fixture,
            'winning_team': self.winning_team.to_dict(),
            'teams': [team.to_dict() for team in self.teams]
        }


class Event:
    def __init__(self, event_type, payload):
        self.type = event_type
        self.payload = payload

    def apply(self, game):
        if self.type == 'MINION_KILL':
            player = game.get_player(self.payload.get("playerID"))
            if player:
                player.minion_kills += 1
                player.gold += self.payload.get("goldGranted", 0)
        elif self.type == 'PLAYER_KILL':
            killer = game.get_player(self.payload.get("killerID"))
            victim = game.get_player(self.payload.get("victimID"))
            assistants = self.payload.get("assistants", [])
            if killer:
                killer.player_kills += 1
                killer.gold += self.payload.get("goldGranted", 0)
            if victim:
                victim.alive = False
            for assistantID in assistants:
                assistant = game.get_player(assistantID)
                if assistant:
                    assistant.assists += 1
                    assistant.gold += self.payload.get("assistGold", 0)
        elif self.type == 'TURRET_DESTROY':
            team = game.get_team(self.payload.get("killerTeamID"))
            killer = game.get_player(self.payload.get("killerID"))
            if team:
                team.turret_kills += 1
                for player in team.players:
                    player.gold += self.payload.get("teamGoldGranted", 0)
            if killer:
                killer.turret_destroys += 1
                killer.gold += self.payload.get("playerGoldGranted", 0)
        elif self.type == 'DRAGON_KILL':
            killer = game.get_player(self.payload.get("killerID"))
            if killer:
                killer.dragon_kills += 1
                killer.gold += self.payload.get("goldGranted", 0)
        elif self.type == 'MATCH_END':
            team = game.get_team(self.payload.get("winningTeamID"))
            if team:
                game.winning_team = team
        else:
            logging.error("Unknown event type")