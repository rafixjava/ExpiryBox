from django.urls import path

from . import views

urlpatterns = [
    path("impact/", views.record_list, name="record_list"),
    path("impact/add/", views.record_add, name="record_add"),
    path("impact/<int:pk>/edit/", views.record_edit, name="record_edit"),
    path("impact/<int:pk>/delete/", views.record_delete, name="record_delete"),
    path("impact/summary/", views.summary, name="impact_summary"),
]
