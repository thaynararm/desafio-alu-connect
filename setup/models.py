import uuid
from django.db import models


class AbstractBaseModel(models.Model):
    id = models.AutoField(primary_key=True, editable=False, unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
