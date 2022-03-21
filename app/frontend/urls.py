from django.urls import path
from .views import index

urlpatterns = [
    path('', index, name='wizard_home'),
    path('<int:pk>/', index, name='wizard_edit'),
]