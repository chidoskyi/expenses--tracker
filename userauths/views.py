from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
# from validate_email import validate_email
from validate_email_address import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes,force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token
import time
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading
# Create your views here.


# def send_email(subject, body, from_email, to_email, retries=3, delay=5):
#     for i in range(retries):
#         try:
#             email = EmailMessage(subject, body, from_email, [to_email])
#             email.send(fail_silently=False)
#             return True
#         except Exception as e:
#             if i < retries - 1:
#                 time.sleep(delay)
#             else:
#                 raise e
#     return False

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
        
    def run(self):
        self.email.send(fail_silently=False)
    
    
    

class emailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        
        if not validate_email(email):
            return JsonResponse({'email_error': 'Invalid email address'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email is in use, choose another one'}, status=409)
        
        return JsonResponse({'email_valid': True})
    
class usernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username is in use choose another one'}, status=409)
        
        return JsonResponse({'username_valid': True})
    
class RegistrationView(View):
    def get(self, request):
        return render(request, ('userauths/register.html'))
    def post(self, request):
        #GET USER DATA
        #VALIDATE
        #create a user account
        
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        context = {
            "field_values": request.POST
        }
        
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short (at least 6 characters required)')
                    return render(request, ('userauths/register.html', context))
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                
                
                # path to view
                # getting domain we are on
                # relative url to verification
                # encode uid
                # token
                
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={'uidb64':uidb64, 'token': account_activation_token.make_token(user)})
                activate_url = 'http://' + domain + link
                
                email_subject = "Activate your account"
                email_body = "Hi there " + user.username + ' please use this link to verify your account\n ' + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    # "Here is the message.",
                    "morrishenry502@gmail.com",
                    [email],
                )
                EmailThread(email).start()
                messages.success(request, 'Account successfully created')
                return redirect('register')  # Redirect to the registration page after successful registration
        
        
        return render(request, ('userauths/register.html'))
    
    
class VerificationView(View):
    def get(self, request, uidb64, token):
        
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            
            if not account_activation_token.check_token(user, token):
                return redirect('login' + '?message=' + 'User already activated')
            
            
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            
            messages.success(request, 'Account activated Successfully')
        except Exception as ex:
            pass
        
        return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request, ('userauths/login.html'))
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        
        if username and password :
            user = authenticate(username=username, password=password)
            
            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome, {username}, you are now logged in')
                    return redirect('expenses')
                messages.error(request, 'Account is not active, Please check your email')        
                return render(request, ('userauths/login.html'))        
            messages.error(request, 'Invalid Credentials Try Again')        
            return render(request, ('userauths/login.html'))        
        
        messages.error(request, 'Please fill all fields')        
        return render(request, ('userauths/login.html'))         
        
    

def signout(request):
    logout(request)
    messages.success(request, 'you are now signed out')
    return redirect('login')
    
    
    
def reset_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return redirect('reset-password')

        try:
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse('reset-user-password', kwargs={'uidb64': uidb64, 'token': PasswordResetTokenGenerator().make_token(user)})
            reset_url = 'http://' + domain + link
            
            email_subject = "Password reset instructions"
            email_body = f"Hi there, please click the link below to reset your password\n{reset_url}"
            email = EmailMessage(
                email_subject,
                email_body,
                "morrishenry502@gmail.com",
                [email],
            )
            EmailThread(email).start()
            messages.success(request, 'We have sent you an email to reset your password')
        except User.DoesNotExist:
            messages.error(request, 'No user is associated with this email')

    context = {
        'values': request.POST
    }
        
    return render(request, 'userauths/reset-password.html', context)


def complete_password_request(request, uidb64, token):
    if request.method == 'POST':
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('reset-user-password', uidb64=uidb64, token=token)
        
        
        if len(password) < 6:
            messages.error(request, 'Password too short')
            return redirect('reset-user-password', uidb64=uidb64, token=token)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            
            if user.check_password(password):
                messages.error(request, 'The new password cannot be the same as the old password')
                return redirect('reset-user-password', uidb64=uidb64, token=token)
            
            user.set_password(password)
            user.save() 
            
            messages.success(request, 'Password changed successfully. You can log in with your new password.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect('reset-user-password', uidb64=uidb64, token=token)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect('reset-user-password', uidb64=uidb64, token=token)
            
        
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.info(request, 'Password link is invalid, Please request a new one')
            return redirect('reset-password')

    except Exception as e:
        pass

    context = {
        'uidb64': uidb64,
        'token': token,
    }
    return render(request, 'userauths/set-newpassword.html', context)
    
 
