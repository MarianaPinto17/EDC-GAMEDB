"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('game/<int:game_id>/', views.showGame, name="ShowGame"),
    path('delete_game/<int:game_id>', views.deleteGame, name="DeleteGame"),
    path('search/', views.searchGame_2, name="SearchGame2"),
    path('searchdb/', views.searchdb, name="SearchDB"),
    path('news/', views.news_feed, name="post_feed"),
    path('add_comment/<int:game_id>', views.addComment, name="addComment"),
    path('add_game', views.addGame, name="addGame"),
    path('new_game/', views.newGame, name="newGame"),
    path('advanced_search/',views.adv_search, name="AdvancedSearch"),
    path('apply_filters/', views.apply_filters, name="applyFilters")
]
