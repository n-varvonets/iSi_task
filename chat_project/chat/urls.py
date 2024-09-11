from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThreadViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'threads', ThreadViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
