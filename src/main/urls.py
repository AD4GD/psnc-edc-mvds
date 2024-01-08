from django.conf.urls import include, url

# all new endpoints that should be visible for end users must start with '/api'
urlpatterns = [
    url(r"^", include("common.urls")),
]
