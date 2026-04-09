from django.urls import path
from .views import MeView, AdminUserListView, AdminUserDetailView

app_name = "users"

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("admin/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/<str:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
]
