from tortoise.models import Model
from tortoise import fields

# class Event(Model):
#     id = fields.IntField(pk=True)
#     name = fields.TextField()
#     datetime = fields.DatetimeField(null=True)

#     class Meta:
#         table = "event"

#     def __str__(self):
#         return self.name


# tournament = fields.ForeignKeyField('models.Tournament', related_name='events')
# tournament: fields.ForeignKeyRelation[Tournament] = fields.ForeignKeyField('models.Tournament', related_name='events')
# participants = fields.ManyToManyField('models.Team', related_name='events', through='event_team')
# participants: fields.ManyToManyRelation["Team"] = fields.ManyToManyField('models.Team', related_name='events', through='event_team')

class PlayersModel(Model):
    steam_id = fields.CharField(pk=True, generated=False, max_length=15)
    nick = fields.TextField()
    creation_date = fields.DatetimeField(null=True)

    class Meta:
        table = "players"
        table_description = "Stores information on all Players"

    def __str__(self):
        return self.nick

class GameModel(Model):
    game_id = fields.IntField(pk=True, generated=False)
    game_map = fields.CharField(max_length=25)
    game_date = fields.DatetimeField()
    game_title = fields.CharField(max_length=255)
    game_data = fields.JSONField()

    class Meta:
        table = "games"
        table_description = "Stores information on all games played"