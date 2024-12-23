from django.urls import path
from . import views
from accounts import views as AccountViews


urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vendor_profile, name="vendorprofile"),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>', views.items_by_category, name='items_by_category'),

    #menu crud operation
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>', views.delete_category, name='delete_category'),

    #item crud operation
    path('menu-builder/item/add/', views.add_item, name='add_item'),
    path('menu-builder/item/edit/<int:pk>', views.edit_item, name='edit_item'),
    path('menu-builder/item/delete/<int:pk>', views.delete_item, name='delete_store_item'),

    #oepning hour crud
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name="add_opening_hours"),
    path('opening-hours/remove/<int:pk>/', views.remove_opening_hours, name="remove_opening_hours"),


    path('order_detail/<int:order_number>/', views.order_detail, name='vendor_order_detail'),
    path('my-orders/', views.my_orders, name='vendor_my_orders'),


]