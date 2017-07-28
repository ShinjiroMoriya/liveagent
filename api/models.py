from django.db import models


class LineSession(models.Model):
    class Meta:
        db_table = 'line_session'

    line_id = models.CharField(max_length=255)
    liveagent_id = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    affinity_token = models.CharField(max_length=255)
    sequence = models.IntegerField(blank=True, null=True)
    ack = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.line_id

    @classmethod
    def get_by_line(cls, line_id):
        return cls.objects.filter(line_id=line_id).values().first()

    @classmethod
    def save_session(cls, data):
        new_data = cls(
            line_id=data.get('line_id'),
            liveagent_id=data.get('id'),
            key=data.get('key'),
            sequence=data.get('sequence'),
            affinity_token=data.get('affinityToken'),
        )
        new_data.save()
        return cls.get_by_line(line_id=data.get('line_id'))

    @classmethod
    def update_session(cls, data):
        cls.objects.filter(line_id=data.get('line_id')).update(**data)
        return cls.get_by_line(line_id=data.get('line_id'))

    @classmethod
    def delete_session(cls, line_id):
        cls.objects.filter(line_id=line_id).delete()