from django.urls import path
from . import views

urlpatterns = [
    path('/', views.index, name='index'),
    path('add_language', views.add_language, name='add_language'),
    path('add_language_form', views.add_language_form, name='add_language_form'),
    path('add_word', views.add_word, name='add_word'),
    path('add_translation', views.add_translation, name='add_translation'),
    path('get_all_languages', views.get_all_languages, name='get_all_languages'),
    # You can add more paths for other views as needed
]
