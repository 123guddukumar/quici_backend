from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints with 'api/' prefix
    path('api/users/', include('users.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/offers/', include('offers.urls')), 
    path('api/reviews/', include('reviews.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/wishlist/', include('wishlist.urls')),

    # Fallback routes without 'api/' prefix (for reverse proxies like Nginx)
    path('users/', include('users.urls')),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('offers/', include('offers.urls')), 
    path('reviews/', include('reviews.urls')),
    path('cart/', include('cart.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
    path('wishlist/', include('wishlist.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)