
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login, logout
from django.contrib import messages
from django.conf import settings
# To send mail import 
from django.core.mail import send_mail, EmailMessage
# Importing current site
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token


# Create your views here.

def home(request):
    return render(request, 'app/home.html')


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist try another")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "Email already Exist try another")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request," Username must be less than 10 characters")

        if password1 != password2:
            messages.error(request,"Password did not match")

        if not username.isalnum():
            messages.error(request," Username must be  Aplha-Numeric ")
            return redirect('home')


        # Registering the user in our database we use django User model by importing
        my_user = User.objects.create_user(username, email, password1)
        my_user.first_name = firstname
        my_user.last_name = lastname
        #we will not activate the user . we will Activate the user after toke is generated
        my_user.is_active = False
        # Saving the user into our User database
        my_user.save()  
        # Showing a message to the user upon sucess we import messages
        messages.success(request, "Account Is Succesfully Created \n We have a sent you a confirmation Email \n  Please confirm your email in order to activate" )   

        # A message to welcome new registers
        subject = 'Welcome to Beauty Glory Login' 
        message = (
                    f"Hello {my_user.first_name}!! \n"
                    f"Welcome to Beauty Glory!! \n"
                    f"Thank you for visiting our website. \n"
                    f"We have sent you a confirmation email. Please confirm your email address in order to activate your account.\n\n"
                    f"Thanking you,\nBeauty Glory"
                )
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

  # Email Address confirmation Email
        current_site = get_current_site(request) # taking the current site
        email_subject = "Confirm your Email @ BeautyGlory Login!"
        message2 = render_to_string('app/email_confirmation.html', {
            'name': my_user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generate_token.make_token(my_user)
        })

        # Crearting an email object
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [my_user.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    return render(request, 'app/signup.html')



def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']
        user = authenticate(username = username, password = password1)
        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, 'app/home.html', {'firstname': firstname})
        else:
            messages.error(request, 'Bad Credentials')
            return redirect('home')

    return render(request, 'app/signin.html')


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Succesfully")
    return redirect('home')


def activate(request, uid64, token):
    try: 
        uid = force_str(urlsafe_base64_decode(uid64))
        my_user = User.objects.get(pk=uid)
    
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None
    
    if my_user is not None and generate_token.check_token(my_user, token):
        my_user.is_active = True # activating the user
        my_user.save()
        login(request,my_user)
        messages.success(request, "Your Account has been activated!!")
        return redirect('home')
    else:
        return render(request, 'app/activation_failed.html')