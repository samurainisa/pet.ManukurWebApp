from django.db import models


class Client(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, db_index=True)
    email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name', 'id']
        indexes = [models.Index(fields=['phone'])]

    def __str__(self) -> str:
        return f'{self.full_name} ({self.phone})'
