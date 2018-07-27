from django.urls import path, include
from . import views
from app.views import *

urlpatterns = [
    # path('', views.base, name='base'),
    path('login/', Login.as_view()),
    path('logout/', Logout.as_view()),
    path('register/', Register.as_view()),
    path('register/success/', RegisterSuccess.as_view()),
    path('', Home.as_view()),
    path('profile/', Profile.as_view()),
    path('active-email/', ActiveEmail.as_view()),
    path('re-send-email/', ReSendEmail.as_view()),
    # user
    path('browse-ads/', BrowseAds.as_view()),
    path('post-ad/', PostAd.as_view()),
    path('my-ads/', MyPostAd.as_view()),
    path('my-ads/<int:pk>/', MyPostAdDetail.as_view()),
    # admin
    path('admin/all-post-ads/', AdminAllPostAd.as_view()),
    path('admin/post-ad-accept/', AdminPostAdAccept.as_view()),
    path('admin/post-ad-accept/<int:pk>/', AdminPostAdDetail.as_view()),
    path('admin/post-ad-create/', AdminPostAdCreate.as_view()),
    path('admin/post-by-user/', AdminPostByUser.as_view()),
    path('admin/post-by-user/<int:pk>/', AdminPostByUser.as_view()),
    path('admin/post-by-manager/', AdminPostByManager.as_view()),
    path('admin/post-by-manager/<int:pk>/', AdminPostByManager.as_view()),
    # managers
    path('managers/create-ad/', ManagerCreateAd.as_view()),
    path('managers/my-ads/', ManagerMyAds.as_view()),
]
