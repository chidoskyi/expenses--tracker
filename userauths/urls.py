from django.urls import path
from .views import RegistrationView,usernameValidationView,emailValidationView,VerificationView,LoginView,signout
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('validate-username', csrf_exempt(usernameValidationView.as_view()), name="validate-username"),
    path('validate-email', csrf_exempt(emailValidationView.as_view()), name="validate-email"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate"),
    path('set-new-password/<uidb64>/<token>', views.complete_password_request, name="reset-user-password"),
    path('register', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', signout, name='logout'),
    path('reset-password', views.reset_password, name='reset-password'),
]
