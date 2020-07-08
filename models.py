from tortoise.models import Model
from tortoise import fields

# tournament = fields.ForeignKeyField('models.Tournament', related_name='events')
# tournament: fields.ForeignKeyRelation[Tournament] = fields.ForeignKeyField('models.Tournament', related_name='events')
# participants = fields.ManyToManyField('models.Team', related_name='events', through='event_team')
# participants: fields.ManyToManyRelation["Team"] = fields.ManyToManyField('models.Team', related_name='events', through='event_team')

class Players(Model):
    steam_id = fields.CharField(pk=True, generated=False, max_length=15)
    nick = fields.TextField()

    class Meta:
        table = "players"
        table_description = "Stores information on all Players"

    def __str__(self):
        return self.nick

class LogstfData(Model):
    game_id = fields.IntField(pk=True, generated=False)
    uploader_id = fields.IntField()
    game_map = fields.CharField(max_length=25)
    game_date = fields.DatetimeField()
    game_title = fields.CharField(max_length=255)
    game_data = fields.JSONField()

    class Meta:
        table = "games"
        table_description = "Stores information on all games played"

class MatchData(Model):
    match_id = fields.IntField(pk=True, generated=True)
    logstf_id = fields.IntField(unique=True)
    nick = fields.CharField(max_length=255, null=False)
    match_date = fields.DatetimeField()
    winning_team = fields.CharField(max_length=4)
    players = fields.CharField(max_length=255)
    length = fields.IntField()
    red_score = fields.IntField()
    red_kills = fields.IntField()
    red_deaths = fields.IntField()
    red_dmg = fields.IntField()
    red_charges = fields.IntField()
    red_drops = fields.IntField()
    red_firstcaps = fields.IntField()
    red_caps = fields.IntField()
    blue_score = fields.IntField()
    blue_kills = fields.IntField()
    blue_deaths = fields.IntField()
    blue_dmg = fields.IntField()
    blue_charges = fields.IntField()
    blue_drops = fields.IntField()
    blue_firstcaps = fields.IntField()
    blue_caps = fields.IntField()

    class Meta:
        table = "matches"
        table_description = "Stores data on all matches played"

class PlayerStats(Model):
    playerstats_id = fields.IntField(pk=True, generated=True)
    match_id = fields.IntField()
    logstf_id = fields.IntField()
    player_id = fields.CharField(max_length=15)
    team = fields.CharField(max_length=4)
    demoman = fields.BooleanField(default=False)
    engineer = fields.BooleanField(default=False)
    heavyweaponsguy = fields.BooleanField(default=False)
    medic = fields.BooleanField(default=False)
    pyro = fields.BooleanField(default=False)
    scout = fields.BooleanField(default=False)
    sniper = fields.BooleanField(default=False)
    soldier = fields.BooleanField(default=False)
    spy = fields.BooleanField(default=False)
    kills = fields.IntField()
    deaths = fields.IntField()
    assists = fields.IntField()
    suicides = fields.IntField()
    kapd = fields.IntField()
    kpd = fields.IntField()
    damage = fields.IntField()
    damage_real = fields.IntField()
    dt = fields.IntField()
    dt_real = fields.IntField()
    hr = fields.IntField()
    lks = fields.IntField()
    stat_as = fields.IntField()
    dapd = fields.IntField()
    dapm = fields.IntField()
    ubers = fields.IntField()
    drops = fields.IntField()
    medkits = fields.IntField()
    medits_hp = fields.IntField()
    backstabs = fields.IntField()
    headshots = fields.IntField()
    headshots_hit = fields.IntField()
    sentries = fields.IntField()
    heal = fields.IntField()
    cpc = fields.IntField()
    ic = fields.IntField()

    class Meta:
        table = "player_stats"
        table_description = "Contains a players stats for each match"