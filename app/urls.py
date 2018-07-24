from django.urls import path, include
from . import views
from app.views import *

urlpatterns = [
	# path('', views.base, name='base'),
	path('login/', Login.as_view()),
	path('logout/', Logout.as_view()),
	path('register/', Register.as_view()),
	path('', Home.as_view()),
	path('profile/', Profile.as_view()),
	# user
	path('browse-ads/', BrowseAds.as_view()),
	path('post-ad/', PostAd.as_view()),
	path('my-ads/', MyPostAd.as_view()),
	path('my-ads/<int:pk>/', MyPostAdDetail.as_view()),
	# manager
	path('managers/all-post-ads/', ManagerAllPostAd.as_view()),
	path('managers/post-ad-accept/', ManagerPostAdAccept.as_view()),
	path('managers/post-ad-accept/<int:pk>/', ManagerPostAdDetail.as_view()),
	path('managers/post-ad-create/', ManagerPostAdCreate.as_view()),
]