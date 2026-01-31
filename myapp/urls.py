from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('upload/', views.upload_item, name='upload_item'),
    path('wishlist/toggle/<int:item_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'),
    path('buy/<int:item_id>/', views.start_buy_chat, name='start_buy_chat'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item')
]