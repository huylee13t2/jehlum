from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
import os
import random


def content_file_name(instance, filename):
    now = timezone.now()
    x = str(now).replace("-", "").replace(" ", "").replace(":",
            "").replace("+", "").replace(".", "")
    ext = filename.split('.')[-1]
    name = random.randint(100, 99999)
    filename = "%s%s.%s" % (x, name, ext)
    return os.path.join(filename)


class Account(models.Model):
	roles = (
        ('user', 'User'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )

	user = models.ForeignKey(User, on_delete=models.CASCADE,
	                         related_name='account_user', blank=True, null=True)
	avatar = models.ImageField(upload_to=content_file_name, null=True)
	full_name = models.CharField(max_length=255, blank=True, null=True)
	role = models.CharField(max_length=255, choices=roles)
	address = models.TextField(blank=True, null=True)
	phone_number = models.CharField(max_length=255, blank=True, null=True)
	is_email_active = models.BooleanField(default=False)
	is_lock = models.BooleanField(default=False)
	otp = models.IntegerField(default=0, blank=True, null=True)
	# token = models.CharField(max_length=255, blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return self.user.username


class Categories(models.Model):
	title = models.CharField(max_length=255, blank=True, null=True)
	created = models.DateTimeField(auto_now_add = True, auto_now = False)
	updated = models.DateTimeField(auto_now_add = True, auto_now = False)

	def __str__(self):
		return self.title


class Location(models.Model):
	title = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		return self.title


class SellerInformation(models.Model):
	name = models.CharField(max_length=255, blank=True, null=True)
	email = models.CharField(max_length=255, blank=True, null=True)
	phone_number = models.CharField(max_length=255, blank=True, null=True)
	hide_phone_number = models.BooleanField(default=False)
	location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
	address = models.TextField(blank=True, null=True)
	terms = models.BooleanField(default=False)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_created', blank=True, null=True)
	updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_updated', blank=True, null=True)
	created = models.DateTimeField(auto_now_add = True, auto_now = False, blank=True, null=True)
	updated = models.DateTimeField(auto_now_add = True, auto_now = False, blank=True, null=True)

	def __str__(self):
		return self.location.title


class AdPost(models.Model):
	title = models.CharField(max_length=255, blank=True, null=True)
	category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='post_ad_category', blank=True, null=True)
	location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='post_ad_location', blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	price_salary = models.CharField(max_length=255, null=True, blank=True)
	negotiable_price = models.BooleanField(default=False)
	seller = models.ForeignKey(SellerInformation, on_delete=models.CASCADE, related_name='post_ad_seller', blank=True, null=True)
	featured_image = models.ImageField(upload_to=content_file_name, null=True)
	is_active = models.BooleanField(default=False)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_add_created', blank=True, null=True)
	updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_add_updated', blank=True, null=True)
	created = models.DateTimeField(auto_now_add = True, auto_now = False, blank=True, null=True)
	updated = models.DateTimeField(auto_now_add = True, auto_now = False, blank=True, null=True)

	def __str__(self):
		return self.title


class Ads_Image(models.Model):
	image = models.ImageField(upload_to=content_file_name, null=True)
	post_ad = models.ForeignKey(AdPost, on_delete=models.CASCADE, related_name='ads_image_post_ad', blank=True, null=True)
	created = models.DateTimeField(auto_now_add = True, auto_now = False)
	updated = models.DateTimeField(auto_now_add = True, auto_now = False)

	def __str__(self):
		return self.image.name


class BlackList(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	created = models.DateTimeField(auto_now_add = True, auto_now = False)
	updated = models.DateTimeField(auto_now_add = True, auto_now = False)

	def __str__(self):
		return self.user.username
