from django.urls import path
from Mysite.views import home, signup, signin, signout, activate


urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name ='signup'),
    path('signin/', signin, name='signin'),
    path('signout/', signout, name='signout'),
    path('activate/<uid64>/<token>', activate, name= 'activate')
]
