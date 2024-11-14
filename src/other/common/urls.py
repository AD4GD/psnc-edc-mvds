from django.conf.urls import include, url

# endpoints below will not be visible for end users (endpoints that start with '/api' will be visible),
# probably it's not a place for adding additional endpoints
urlpatterns = [
    url(r"^_health/app/", include("watchman.urls")),
]
