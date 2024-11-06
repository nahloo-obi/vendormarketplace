from django.urls import path
from . import views
from accounts import views as AccountViews


urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vendor_profile, name="vendorprofile"),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>', views.items_by_category, name='items_by_category'),

    path('menu-builder/category/add/', views.add_category, name='add_category')

]