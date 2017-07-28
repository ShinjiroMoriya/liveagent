from django.conf.urls import url
from api.views import *

urlpatterns = [
    url(r'^init$', LiveagentInit.as_view()),
    url(r'^messages$', LiveagentMessages.as_view()),
    url(r'^send$', LiveagentSend.as_view()),
    url(r'^close$', LiveagentClose.as_view()),
]
