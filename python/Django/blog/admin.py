'''
Module for the admin page of a Django app.
This module defines all contents that can be seen and
modified in the admin page.

For this app the way how entries can be created and edited 
is defined. The admin can modify the comments of each entry
as well as changing the entry properties like title, text and
author. The images of an entry can also be changed in the admin
page.

@author: Christian Breu <cbreu0@icloud.com>
'''

from django.contrib import admin

from .models import Entry, Comment, Imagem

class ImageMInline(admin.TabularInline):
    model = Imagem
    extra = 1
    
class CommentInline(admin.TabularInline):
    model = Comment
    
class EntryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Contents',               {'fields': ['entry_title', 'entry_text', 'author']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    #define which models should be available in the entry page
    inlines = [ImageMInline, CommentInline]
    
    #defines how the entry attributes are displayed in the admin page
    list_display = ('entry_title', 'entry_text', 'pub_date', 'author')
    list_filter = ['pub_date']
    search_fields = ['entry_title']

# register the entry model to the admin page.
admin.site.register(Entry, EntryAdmin)