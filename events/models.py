from django.db import models 
from django.conf import settings 
from django.urls import reverse 

class Event(models.Model): 

    EVENT_TYPES = [ 
            ('interview', 'Interview'), 
            ('meeting', 'Meeting'),
            ('followup', 'Follow-up'),
            ('networking', 'Networking Event')
        ] 

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    title = models.CharField(max_length=200) 
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES) 
    date = models.DateTimeField() 
    location = models.CharField(max_length=200) 
    # contacts = models.ManyToManyField('contacts.Contact', blank=True)
    job_posting = models.ForeignKey('jobs.JobPosting', null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        ordering = ['date'] 

    def __str__(self):       
        return f"{self.title} - {self.date.strftime('%Y-%m-%d %H:%M')}" 

    def get_absolute_url(self):   
        return reverse('events:detail', kwargs={'pk': self.pk})