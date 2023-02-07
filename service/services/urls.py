from rest_framework import routers

from services.views import SubscriptionView

router = routers.DefaultRouter()
router.register(r'api/subscriptions', SubscriptionView)

urlpatterns = []

urlpatterns += router.urls
