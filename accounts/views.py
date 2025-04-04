from urllib import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import auth
from .models import UserProfile
from products.models import Product
import re

# Создайте ваши представления здесь.

def signin(request):
    if request.method == 'POST' and  'btnlogin' in request.POST:

        username = request.POST['user']
        password = request.POST['pass']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if 'rememberme' not in request.POST:
                request.session.set_expiry(0)
            auth.login(request, user)
            #messages.success(request, 'You are now logged in')
        else:
            messages.error(request, 'Username or password invalid')


   

       
        return redirect('signin')
    else:
        return render( request , 'accounts/signin.html' )
    
def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect('index')


def signup(request):
    if request.method == 'POST' and 'btnsignup' in request.POST:

        fname = None
        lname = None
        address = None
        address2 = None
        city = None
        state = None
        zip_number = None
        email = None
        username = None
        password = None
        terms = None
        is_added = None

        if 'fname' in request.POST: fname = request.POST['fname']
        else: messages.error(request, 'Ошибка в имени')

        if 'lname' in request.POST: lname = request.POST['lname']
        else: messages.error(request, 'Ошибка в фамилии')

        if 'address' in request.POST: address = request.POST['address']
        else: messages.error(request, 'Ошибка в адресе')

        if 'address2' in request.POST: address2 = request.POST['address2']
        else: messages.error(request, 'Ошибка в адресе 2')

        if 'city' in request.POST: city = request.POST['city']
        else: messages.error(request, 'Ошибка в городе')

        if 'state' in request.POST: state = request.POST['state']
        else: messages.error(request, 'Ошибка в штате')

        if 'zip' in request.POST: zip_number = request.POST['zip']
        else: messages.error(request, 'Ошибка в почтовом индексе')

        if 'email' in request.POST: email = request.POST['email']
        else: messages.error(request, 'Ошибка в электронной почте')

        if 'user' in request.POST: username = request.POST['user']
        else: messages.error(request, 'Ошибка в имени пользователя')

        if 'pass' in request.POST: password = request.POST['pass']
        else: messages.error(request, 'Ошибка в пароле')

        if 'terms' in request.POST: terms = request.POST['terms']

        if fname and lname and address and address2 and city and state and zip_number and email and username and password:
            if terms == 'on':
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Это имя пользователя уже занято')
                else:
                    if User.objects.filter(email=email).exists():
                        messages.error(request, 'Этот email уже занят')
                    else:
                        patt = r"^[\w\.-]+@[\w\.-]+\.\w+$"
                        if re.match(patt, email):

                            user = User.objects.create_user(
                                first_name=fname,
                                last_name=lname,
                                email=email, username=username,
                                password=password)
                            user.save()

                            userprofile = UserProfile(user=user,
                                                      address=address, address2=address2,
                                                      city=city, state=state,
                                                      zip_number=zip_number)
                            userprofile.save()

                            fname = ''
                            lname = ''
                            address = ''
                            address2 = ''
                            city = ''
                            state = ''
                            zip_number = ''
                            email = ''
                            username = ''
                            password = ''
                            terms = None

                            messages.success(request, 'Ваш аккаунт создан')
                            is_added = True
                        else:
                            messages.error(request, 'Неверный email')
            else:
                messages.error(request, 'Вы должны согласиться с условиями')
        else:
            messages.error(request, 'Проверьте пустые поля')

        return render(request, 'accounts/signup.html', {
            'fname': fname,
            'lname': lname,
            'address': address,
            'address2': address,
            'city': city,
            'state': state,
            'zip': zip_number,
            'email': email,
            'user': username,
            'pass': password,
            'is_added': is_added
        })

    else:
        return render(request, 'accounts/signup.html')


def profile(request):
    if request.method == 'POST' and 'btnsave' in request.POST:

        if request.user is not None and request.user.id != None:
            userprofile = UserProfile.objects.get(user=request.user)

            if request.POST['fname'] and request.POST['lname'] and request.POST['address'] and request.POST['address2'] and request.POST['city'] and request.POST['state'] and request.POST['zip'] and request.POST['email'] and request.POST['user'] and request.POST['pass']:
                request.user.first_name = request.POST['fname']
                request.user.last_name = request.POST['lname']
                userprofile.address = request.POST['address']
                userprofile.address2 = request.POST['address2']
                userprofile.city = request.POST['city']
                userprofile.state = request.POST['state']
                userprofile.zip_number = request.POST['zip']
                if not request.POST['pass'].startswith('pbkdf2_sha256$'):
                    request.user.set_password(request.POST['pass'])
                request.user.save()
                userprofile.save()
                auth.login(request, request.user)
                messages.success(request, 'Ваши данные были сохранены')
            else:
                messages.error(request, 'Проверьте ваши данные')

        return redirect('profile')
    else:
        if request.user is not None:

            context = None

            if not request.user.is_anonymous:
                userprofile = UserProfile.objects.get(user=request.user)

                context = {
                    'fname': request.user.first_name,
                    'lname': request.user.last_name,
                    'address': userprofile.address,
                    'address2': userprofile.address2,
                    'city': userprofile.city,
                    'state': userprofile.state,
                    'zip': userprofile.zip_number,
                    'email': request.user.email,
                    'user': request.user.username,
                    'pass': request.user.password
                }
            return render(request, 'accounts/profile.html', context)
        else:
            return redirect('profile')


def product_favorite(request, pro_id):
    if request.user.is_authenticated and not request.user.is_anonymous:
        pro_fav = Product.objects.get(pk=pro_id)
        if UserProfile.objects.filter(user=request.user, product_favorites=pro_fav).exists():
            messages.success(request, 'Этот продукт уже в списке избранных')
        else:
            userprofile = UserProfile.objects.get(user=request.user)
            userprofile.product_favorites.add(pro_fav)
            messages.success(request, 'Продукт добавлен в избранное')

    else:
        messages.error(request, 'Вы должны быть авторизованы')
    return redirect('/products/' + str(pro_id))


def show_product_favorite(request):
    context = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        userInfo = UserProfile.objects.get(user=request.user)
        pro = userInfo.product_favorites.all()
        context = {'products': pro}
    return render(request, 'products/products.html', context)
