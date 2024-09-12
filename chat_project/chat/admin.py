from django.contrib import admin
from .models import Thread, Message


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'updated')
    filter_horizontal = ('participants',)
    search_fields = ['participants__email']
    list_filter = ['created', 'updated']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'sender', 'created', 'is_read')
    search_fields = ['sender__email', 'thread__id']
    list_filter = ['created', 'is_read']

