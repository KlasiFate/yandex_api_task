from django.urls import include, path

from .views import YandexAPI

ready_view = YandexAPI.as_view()

urlpatterns = [
    path('imports', ready_view),
    path('imports/', ready_view),
    path('delete/<uuid:id>', ready_view),
    path('nodes/<uuid:id>', ready_view),
]