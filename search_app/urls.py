from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path, include
from django.urls import path
from . import views
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
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('swapi/character/', views.swapi_character_search, name='swapi_character_search'),
    path('swapi/all_data/', views.swapi_all_data, name='swapi_all_data'),
]
