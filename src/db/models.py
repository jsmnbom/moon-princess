from tortoise.models import Model
from tortoise import fields


class GuildOptions(Model):
    id = fields.BigIntField(pk=True)
    guild_id = fields.BigIntField()
    dadbot_enabled_channels = fields.JSONField(default=[])

    def __str__(self):
        return 'GuildOptions[{}]'.format(self.guild_id)
