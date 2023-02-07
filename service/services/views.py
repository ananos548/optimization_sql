from django.core.cache import cache
from django.db.models import Prefetch, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from django.conf import settings
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',  # фиксим проблему n+1 с планами(создаётся sql запросов сколько и планов, даже если планы одинаковы)
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email')))
    # соединяем Client с User(select_related) и после берём только поле company
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        price_cache = cache.get(settings.PRICE_CACHE_NAME)
        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_price, 50)
        response_data = {'result': response.data, 'total_amount': total_price}
        response.data = response_data
        return response
