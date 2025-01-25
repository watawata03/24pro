from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import register, swapi_character_search

urlpatterns = [
    path('', views.search_view, name='search_view'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/', views.product_list, name='product_list'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('simple-form/', views.simple_text_view, name='simple_text_form'),
    path('register/', register, name='register'),
    path('category/new/', views.category_create, name='category_create'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('swapi/character/', views.swapi_character_search, name='swapi_character_search'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('delete_search_history/<int:history_id>/', views.delete_search_history, name='delete_search_history'),
    path('export_csv/', views.export_search_results_csv, name='export_search_results_csv'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('swapi-character/', swapi_character_search, name='swapi_character_search'),
    path('search/', views.search_results, name='search_results'),
    path('character/<int:pk>/', views.character_detail, name='character_detail'),  
    path('character/<int:pk>/edit/', views.character_edit, name='character_edit'),
    path('character/<int:pk>/update-image/', views.update_character_image, name='update_character_image'),
    path('characters/', views.character_list, name='character_list'),  
    path('character/create/', views.character_create, name='character_create'),
    path("save_color/", views.save_color, name="save_color"),
    
]  

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
