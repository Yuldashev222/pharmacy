from datetime import datetime

from django.db import models


class Offer(models.Model):
    n = 'new'
    p = 'process'
    a = 'answered'
    STATUS = [
        ['n', n],
        ['p', p],
        ['a', a]
    ]
    title = models.CharField(max_length=150, blank=True)
    text = models.TextField(max_length=1000)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='n')
    answer_text = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.answer_text and self.status != 'a':
            self.status = 'a'
            self.answered_at = datetime.now()
        super().save(*args, **kwargs)
