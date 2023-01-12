from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home),
    path('token/', views.token),
    # path("plot/<string:item_type>/<string:plot_type>/<string:item_id>/<int:days>", views.plot),
]