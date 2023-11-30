from django.db import models
from django.db.models import ForeignKey

class Definition(models.Model):
    definition_text = models.TextField()

class Language(models.Model):
    language = models.CharField(max_length=100)
    language_code = models.CharField(max_length=10)
    spacy_corpus = models.CharField(max_length=100)


class Word(models.Model):
    lemmatized_word = models.CharField(max_length=100)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    definition = models.ForeignKey(Definition, on_delete=models.CASCADE)
    translation = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='translations')

class Sentence(models.Model):
    text = models.TextField()
    words = models.ManyToManyField(Word)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    translation = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='translations')

