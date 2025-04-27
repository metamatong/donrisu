from django.db import models
from django.contrib.auth.models import User

class Character(models.Model):
    SPECIES_CHOICES = [
        ('human', 'Human'),
        ('elf', 'Elf'),
        ('vampire', 'Vampire'),
        # Add more species
    ]
    
    BACKGROUND_CHOICES = [
        ('real_life', 'Real Life'),
        ('fantasy', 'Fantasy'),
        ('school', 'School'),
    ]
    
    RELATIONSHIP_CHOICES = [
        ('bully', 'Bully Girl'),
        ('best_friend', 'Best Friend'),
        ('stepmom', 'Stepmom'),
        # Add more relationships
    ]
    
    DYNAMIC_CHOICES = [
        ('thunder', 'Thunder'),
        ('submissive', 'Submissive'),
        ('dominant', 'Dominant'),
        ('ntr', 'NTR'),
        # Add more dynamics
    ]
    
    APPEARANCE_CHOICES = [
        ('appearance1', 'Classic and elegant'),
        ('appearance2', 'Modern and stylish'),
        ('appearance3', 'Casual and friendly'),
        ('appearance4', 'Mysterious and alluring'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    appearance = models.CharField(max_length=20, choices=APPEARANCE_CHOICES)
    background = models.CharField(max_length=20, choices=BACKGROUND_CHOICES)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    dynamic = models.CharField(max_length=20, choices=DYNAMIC_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"

class ChatRoom(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

class ChatMessage(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']

class ResponseOption(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='response_options')
    content = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']

class PreMadeResponse(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    user_message = models.TextField()
    character_response = models.TextField()
