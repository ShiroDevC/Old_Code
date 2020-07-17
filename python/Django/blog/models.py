'''
Module for the models that are used in this Django app.
each model has a class that defines its properties
and relations to other models in the database.

For this app there is an entry model for blog posts and
models for images and comments which have a foreign key
to be referenced to exactly one entry (1:n relationship
between entries and images/comments).

@author: Christian Breu <cbreu0@icloud.com>
'''

from django.db import models


from django.core.files.storage import FileSystemStorage

#specifying a folder for the file storage
fs = FileSystemStorage(location='media/photos/entry')

# Create your models here.

class Entry(models.Model):
    """
    model class for entries.
    Images are handled from the ImageM model with a 1:n relationship.
    """
    entry_title = models.CharField(max_length=200)
    #charfield is for medium to small texts, textfiels is for long texts
    entry_text = models.TextField()
    author = models.CharField(max_length=50)
    pub_date = models.DateField('date published')
    
    def __str__(self):
        return self.entry_title
    
class Imagem(models.Model):
    """
    model class for Images to be used in a one to many relationship with Entries or other models.
    Images are stored on the specified path(not default location)
    """
    picture = models.ImageField(upload_to='media/photos/entry')
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

class Comment(models.Model):
    """
    model class for comments on entries. Each comment belongs to one entry.
    """
    
    comment_text = models.TextField()
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    pub_date = models.DateField('date published')
    
    def __str__(self):
        return self.comment_text