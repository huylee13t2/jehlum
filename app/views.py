from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from app.models import Account, Categories, Location, SellerInformation, AdPost, Ads_Image, BlackList
from django.db.models import Q
import random


def base(request):
    # if not request.user.is_authenticated:
    # 	return HttpResponsePermanentRedirect('login/')
    return render(request, "index.html", {})


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/')

        msg_error = ""
        return render(request, 'user/login/index.html', {'msg_error': msg_error})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        try:
            obj_account = Account.objects.get(user__username=username)

            if obj_account.is_email_active:

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponsePermanentRedirect('/')
                else:
                    msg_error = "Please check username or password again!"
            else:
                msg_error = "The account has not been activated. Please check your email and activate your account."

            return render(request, 'user/login/index.html', {'msg_error': msg_error})
        except:
            msg_error = "Account does not exist. Please check again or register another account"
            return render(request, 'user/login/index.html', {'msg_error': msg_error})


class Logout(View):
    def get(self, request):
        print('********** logout')
        logout(request)
        return HttpResponsePermanentRedirect('/login/')


class Register(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/')

        msg_error = ""
        return render(request, 'user/register/index.html', {'msg_error': msg_error})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        re_password = request.POST['re_password']

        msg_error = ""

        if re_password != password:
            msg_error = "Passwords are not the same"

            return render(request, 'user/register/index.html', {'msg_error': msg_error})

        else:
            new_user = User(username=username, email=username)
            new_user.set_password(password)
            # try:
            new_user.save()

            otp_number = random.randint(100000, 999999)
            new_account = Account(user=new_user, role='user', otp=otp_number)
            new_account.save()

            email_url_active = str(settings.URL_LOCAL) + 'active-email/?email=' + str(username) + '&otp=' + str(
                otp_number)
            email_msg = "Please active account register. Click link " + email_url_active
            email = EmailMessage('Active Email', email_msg, to=[username])
            email.send()

            return HttpResponsePermanentRedirect('/register/success/')

        # except:
        # 	msg_error = 'Email already exists. Please select another email.'
        # 	return render(request, 'user/register/index.html', {'msg_error': msg_error})


class RegisterSuccess(View):
    def get(self, request):
        return render(request, 'user/register/success.html')


class ActiveEmail(View):
    def get(self, request):
        msg_error = ""
        email = request.GET['email']
        opt = request.GET['otp']

        obj_account = Account.objects.get(user__username=email)
        if opt == str(obj_account.otp):
            obj_account.is_email_active = True
            obj_account.save()

            context = {
                'msg_error': msg_error
            }

            return render(request, 'user/active-email-success.html', context)
        else:
            msg_error = 'OTP code is incorrect. Please check again.'

            context = {
                'msg_error': msg_error
            }

            return render(request, 'user/active-email-error.html', context)


class ReSendEmail(View):
    def get(self, request):
        return render(request, 'user/re-send-mail.html')

    def post(self, request):
        email = request.POST['email']

        obj_account = Account.objects.get(user__username=email)

        otp_number = random.randint(100000, 999999)

        email_url_active = str(settings.URL_LOCAL) + 'active-email/?email=' + str(email) + '&otp=' + str(otp_number)
        email_msg = "Please active account register. Click link " + email_url_active
        email = EmailMessage('Active Email', email_msg, to=[email])
        email.send()

        obj_account.otp = otp_number
        obj_account.save()

        return render(request, 'user/re-send-mail-done.html')


class Home(View):
    def get(self, request):
        msg_error = ""

        try:
            obj_account = Account.objects.get(user=request.user)
            role = obj_account.role

            if (role == 'user'):
                context = {
                    'msg_error': msg_error,
                    'role': role,
                }

                return render(request, 'home/index.html', context)
            elif role == 'admin':
                context = {
                    'msg_error': msg_error,
                    'role': role,
                }

                # return render(request, 'pages/admin/home.html', context)
                return HttpResponsePermanentRedirect('/admin/all-post-ads/')
            else:
                context = {
                    'msg_error': msg_error,
                    'role': role,
                }

                # return render(request, 'pages/admin/home.html', context)
                return HttpResponsePermanentRedirect('/managers/create-ad/')

        except:
            context = {
                'msg_error': msg_error,
            }

            return render(request, 'home/index.html', context)


class Profile(View):
    def get(self, request):
        msg_error = ""
        if request.user.is_authenticated:
            profile = Account.objects.get(user=request.user)
        else:
            return HttpResponsePermanentRedirect("/login/")

        context = {
            'msg_error': msg_error,
            'profile': profile,
        }

        return render(request, 'user/profile.html', context)

    def post(self, request):
        msg_error = ""

        full_name = request.POST['full_name']
        email = request.POST['email']
        address = request.POST['address']
        phone_number = request.POST['phone_number']

        try:
            account = Account.objects.get(user=request.user)
            account.full_name = full_name
            account.address = address
            account.phone_number = phone_number

            account.save()

        except:
            msg_error = "Can't updated profile!"

        context = {
            'msg_error': phone_number,
            'profile': account,
        }

        return render(request, 'user/profile.html', context)


# *****************************************
# *****************  User *****************
class MyPostAd(View):
    def get(self, request):
        msg_error = ""
        message = ""
        categories = Categories.objects.all()
        locations = Location.objects.all()

        list_ad_accept = AdPost.objects.filter(Q(created_by=request.user) & Q(is_active=True))

        context = {
            'categories': categories,
            'locations': locations,
            'msg_error': msg_error,
            'message': message,
            'list_ad_accept': list_ad_accept,
        }

        return render(request, 'pages/my-post-ad.html', context)


class MyPostAdDetail(View):
    def get(self, request, pk):
        msg_error = ""
        message = ""
        categories = Categories.objects.all()
        locations = Location.objects.all()

        obj_ad = AdPost.objects.get(id=pk)

        context = {
            'message': message,
            'msg_error': msg_error,
            'categories': categories,
            'locations': locations,
            'item': obj_ad,
        }

        return render(request, 'pages/my-post-ad-detail.html', context)


class PostAd(View):
    def get(self, request):
        try:
            obj_account = Account.objects.get(user=request.user)
            role = obj_account.role
            msg_error = ""
            message = ""
            categories = Categories.objects.all()
            locations = Location.objects.all()

            if role == 'user':
                context = {
                    'categories': categories,
                    'locations': locations,
                    'msg_error': msg_error,
                    'message': message,
                }

                return render(request, 'pages/post-ad.html', context)
            else:
                return HttpResponsePermanentRedirect('/admin/post-ad-create/')
            # list_ad_accept = AdPost.objects.filter(is_active=False)

            # context= {
            # 	'categories': categories,
            # 	'locations': locations,
            # 	'msg_error': msg_error,
            # 	'message' : message,
            # 	'list_ad_accept': list_ad_accept,
            # }

            # return render(request, 'admin/post-ad.html', context)
        except:
            return HttpResponsePermanentRedirect('/login/')

    def post(self, request):
        try:
            category = request.POST['category']
            location = request.POST['location']
            # ad_type = request.POST['type']

            title = request.POST.get('title')
            description = request.POST.get('description')
            price_salary = request.POST.get('price_salary')
            negotiable_price = request.POST.get('negotiable_price')
            sell_name = request.POST.get('sell_name')
            sell_email = request.POST.get('sell_email')
            sel_phone_number = request.POST.get('sel_phone_number')
            sell_hide_phone = request.POST.get('sell_hide_phone')
            sell_terms = request.POST.get('sell_terms')

            featured_image = request.FILES.getlist('featured_image')[0]
            other_image = request.FILES.getlist('other_image')

            category = Categories.objects.get(id=category)
            location = Location.objects.get(id=location)

            sell_info = SellerInformation(name=sell_name, email=sell_email, phone_number=sel_phone_number,
                                          location=location, created_by=request.user, updated_by=request.user)

            if sell_hide_phone == 'on':
                sell_info.hide_phone_number = True
            else:
                sell_info.hide_phone_number = False

            if sell_terms == 'on':
                sell_info.terms = True
            else:
                sell_info.terms = False

            sell_info.save()

            obj_ad = AdPost(title=title, category=category, location=location, description=description,
                            price_salary=price_salary, seller=sell_info, featured_image=featured_image,
                            created_by=request.user, updated_by=request.user)

            if negotiable_price == 'on':
                obj_ad.negotiable_price = True
            else:
                obj_ad.negotiable_price = False

            obj_ad.save()

            if len(other_image) != 0:
                for img in other_image:
                    ads_img = Ads_Image(image=img)
                    ads_img.save()

            message = "Created Ad successfully!"
            msg_error = ""

        except:
            message = ""
            msg_error = "Created ad failed!"

        categories = Categories.objects.all()
        locations = Location.objects.all()

        context = {
            'message': message,
            'msg_error': msg_error,
            'locations': locations,
            'categories': categories,
        }

        return render(request, 'pages/post-ad.html', context)


class BrowseAds(View):
    def get(self, request):
        msg_error = ""

        all_categories = Categories.objects.all()
        all_locations = Location.objects.all()

        context = {
            'msg_error': msg_error,
            'all_categories': all_categories,
            'all_locations': all_locations,
        }

        return render(request, 'pages/browse-ads.html', context)


# *****************************************************
# **************** manager post ad ********************
class AdminPostAdAccept(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'admin':
                return HttpResponsePermanentRedirect('/logout/')

        msg_error = ""
        message = ""
        categories = Categories.objects.all()
        locations = Location.objects.all()

        list_ad_accept = AdPost.objects.filter(is_active=False)

        context = {
            'categories': categories,
            'locations': locations,
            'msg_error': msg_error,
            'message': message,
            'list_ad_accept': list_ad_accept,
            'role': obj_account.role
        }

        return render(request, 'admin/post-ad.html', context)


class AdminPostAdDetail(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'admin':
                return HttpResponsePermanentRedirect('/logout/')

        try:
            msg_error = ""
            msg_success = ""

            action = request.GET.get('action', None)
            obj_post_ad = AdPost.objects.get(id=pk)

            if action is not None:
                if action == 'accept':
                    # accept post ads
                    obj_post_ad.is_active = True
                    email_msg = "Your ad has been accepted"
                    obj_post_ad.save()
                    msg_success = "Accept ad was successful!"
                else:
                    # delete post ad
                    email_msg = "Your ad was disapproved. Please create another ad"
                    obj_post_ad.delete()
                    msg_success = "Delete ad was successful!"

                email = EmailMessage('Accept PostAd', email_msg, to=[obj_post_ad.created_by.username])
                email.send()

            context = {
                'msg_error': msg_error,
                'item': obj_post_ad,
                'msg_success': msg_success,
                'role': obj_account.role,
            }
            return render(request, 'admin/post-ad-detail.html', context)

        except:
            return HttpResponsePermanentRedirect('/post-ad/')


class AdminAllPostAd(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'admin':
                return HttpResponsePermanentRedirect('/logout/')

        action = request.GET.get('action', None)
        pk = request.GET.get('id', None)
        msg_error = ""
        message = ""
        print(obj_account.role)
        if action is not None:
            if pk is not None:
                print('yes')
                try:
                    obj_post_ad = AdPost.objects.get(id=pk)
                    obj_post_ad.delete()
                    message = "Delete As successfully!"
                except:
                    msg_error = "Delete Ad error!"

        all_post_ads = AdPost.objects.filter(is_active=True)

        context = {
            'all_post_ads': all_post_ads,
            'msg_error': msg_error,
            'message': message,
            'role': obj_account.role,
        }

        return render(request, 'admin/list-post-ads.html', context)


class AdminPostByUser(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'admin':
                return HttpResponsePermanentRedirect('/logout/')

        action = request.GET.get('action', None)
        pk = request.GET.get('id', None)
        msg_error = ""
        message = ""
        print(obj_account.role)
        if action is not None:
            if pk is not None:
                print('yes')
                try:
                    obj_post_ad = AdPost.objects.get(id=pk)
                    obj_post_ad.delete()
                    message = "Delete As successfully!"
                except:
                    msg_error = "Delete Ad error!"

        list_ads_active = AdPost.objects.filter(is_active=True)

        list_ads_user = []
        for item in list_ads_active:
            obj_account = Account.objects.get(user=item.created_by)
            if obj_account.role == 'user':
                list_ads_user.append(item)

        print("******************")
        print(list_ads_user)
        print("******************")
        context = {
            'all_post_ads': list_ads_user,
            'msg_error': msg_error,
            'message': message,
        }
        return render(request, 'admin/list-post-by-user.html', context)


class AdminPostByManager(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'admin':
                return HttpResponsePermanentRedirect('/logout/')

        action = request.GET.get('action', None)
        pk = request.GET.get('id', None)
        msg_error = ""
        message = ""
        print(obj_account.role)
        if action is not None:
            if pk is not None:
                print('yes')
                try:
                    obj_post_ad = AdPost.objects.get(id=pk)
                    obj_post_ad.delete()
                    message = "Delete As successfully!"
                except:
                    msg_error = "Delete Ad error!"

        list_ads_active = AdPost.objects.filter(is_active=True)

        list_ads_manager = []
        for item in list_ads_active:
            obj_account = Account.objects.get(user=item.created_by)
            if obj_account.role == 'manager':
                list_ads_manager.append(item)

        print("******************")
        print(list_ads_manager)
        print("******************")
        context = {
            'all_post_ads': list_ads_manager,
            'msg_error': msg_error,
            'message': message,
        }
        return render(request, 'admin/list-post-by-manager.html', context)


class AdminPostAdCreate(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'admin':
                return HttpResponsePermanentRedirect('/logout/')

        msg_error = ""
        message = ""
        categories = Categories.objects.all()
        locations = Location.objects.all()

        context = {
            'categories': categories,
            'locations': locations,
            'msg_error': msg_error,
            'message': message,
            'role': obj_account.role,
        }

        return render(request, 'admin/post-ad-create.html', context)

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'admin':
                return HttpResponsePermanentRedirect('/logout/')
        # try:
        category = request.POST['category']
        location = request.POST['location']

        title = request.POST.get('title')
        description = request.POST.get('description')
        price_salary = request.POST.get('price_salary')
        negotiable_price = request.POST.get('negotiable_price')
        sell_name = request.POST.get('sell_name')
        sell_email = request.POST.get('sell_email')
        sel_phone_number = request.POST.get('sel_phone_number')
        sell_hide_phone = request.POST.get('sell_hide_phone')
        sell_terms = request.POST.get('sell_terms')

        featured_image = request.FILES.getlist('featured_image')[0]
        other_image = request.FILES.getlist('other_image')

        category = Categories.objects.get(id=category)
        location = Location.objects.get(id=location)

        sell_info = SellerInformation(name=sell_name, email=sell_email, phone_number=sel_phone_number,
                                      location=location, created_by=request.user, updated_by=request.user)

        if sell_hide_phone == 'on':
            sell_info.hide_phone_number = True
        else:
            sell_info.hide_phone_number = False

        if sell_terms == 'on':
            sell_info.terms = True
        else:
            sell_info.terms = False

        sell_info.save()

        obj_ad = AdPost(title=title, category=category, location=location, description=description,
                        price_salary=price_salary, seller=sell_info, featured_image=featured_image,
                        created_by=request.user, updated_by=request.user)

        if negotiable_price == 'on':
            obj_ad.negotiable_price = True
        else:
            obj_ad.negotiable_price = False

        obj_ad.is_active = True
        obj_ad.save()

        if len(other_image) != 0:
            for img in other_image:
                ads_img = Ads_Image(image=img)
                ads_img.save()

        message = "Created Ad successfully!"
        msg_error = ""

        # except:
        # 	message = ""
        # 	msg_error = "Created ad failed!"

        categories = Categories.objects.all()
        locations = Location.objects.all()

        context = {
            'message': message,
            'msg_error': msg_error,
            'locations': locations,
            'categories': categories,
            'role': obj_account.role,
        }

        return render(request, 'admin/post-ad-create.html', context)


class ManagerCreateAd(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'manager':
                return HttpResponsePermanentRedirect('/logout/')

        msg_error = ""
        message = ""
        categories = Categories.objects.all()
        locations = Location.objects.all()

        context = {
            'categories': categories,
            'locations': locations,
            'msg_error': msg_error,
            'message': message,
            'role': obj_account.role,
        }

        return render(request, 'managers/create-ad.html', context)

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponsePermanentRedirect('/logout/')
        else:
            obj_account = Account.objects.get(user=request.user)
            if obj_account.role != 'manager':
                return HttpResponsePermanentRedirect('/logout/')
        # try:
        category = request.POST['category']
        location = request.POST['location']

        title = request.POST.get('title')
        description = request.POST.get('description')
        price_salary = request.POST.get('price_salary')
        negotiable_price = request.POST.get('negotiable_price')
        sell_name = request.POST.get('sell_name')
        sell_email = request.POST.get('sell_email')
        sel_phone_number = request.POST.get('sel_phone_number')
        sell_hide_phone = request.POST.get('sell_hide_phone')
        sell_terms = request.POST.get('sell_terms')

        featured_image = request.FILES.getlist('featured_image')[0]
        other_image = request.FILES.getlist('other_image')

        category = Categories.objects.get(id=category)
        location = Location.objects.get(id=location)

        sell_info = SellerInformation(name=sell_name, email=sell_email, phone_number=sel_phone_number,
                                      location=location, created_by=request.user, updated_by=request.user)

        if sell_hide_phone == 'on':
            sell_info.hide_phone_number = True
        else:
            sell_info.hide_phone_number = False

        if sell_terms == 'on':
            sell_info.terms = True
        else:
            sell_info.terms = False

        sell_info.save()

        obj_ad = AdPost(title=title, category=category, location=location, description=description,
                        price_salary=price_salary, seller=sell_info, featured_image=featured_image,
                        created_by=request.user, updated_by=request.user)

        if negotiable_price == 'on':
            obj_ad.negotiable_price = True
        else:
            obj_ad.negotiable_price = False

        # obj_ad.is_active = True
        obj_ad.save()

        if len(other_image) != 0:
            for img in other_image:
                ads_img = Ads_Image(image=img)
                ads_img.save()

        message = "Created Ad successfully!"
        msg_error = ""

        # except:
        # 	message = ""
        # 	msg_error = "Created ad failed!"

        categories = Categories.objects.all()
        locations = Location.objects.all()

        context = {
            'message': message,
            'msg_error': msg_error,
            'locations': locations,
            'categories': categories,
            'role': obj_account.role,
        }

        return render(request, 'managers/create-ad.html', context)


class ManagerMyAds(View):
    def get(self, request):
        msg_error = ""
        message = ""
        categories = Categories.objects.all()
        locations = Location.objects.all()

        list_ad_accept = AdPost.objects.filter(Q(created_by=request.user))

        context = {
            'categories': categories,
            'locations': locations,
            'msg_error': msg_error,
            'message': message,
            'list_ad_accept': list_ad_accept,
        }

        return render(request, 'managers/my-ads.html', context)
