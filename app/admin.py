from django.contrib import admin
from app.models import Account, Categories, SellerInformation, AdPost, Ads_Image, BlackList, Location

admin.site.register(Account)
admin.site.register(Categories)
admin.site.register(SellerInformation)
admin.site.register(Location)
admin.site.register(AdPost)
admin.site.register(BlackList)
admin.site.register(Ads_Image)