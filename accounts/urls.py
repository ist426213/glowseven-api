from django.urls import path
from .views import (
    RegisterView,
    UserDetailView,
    DashboardStatsView,
    UserOrderListView,
    UserOrderDetailView,
    ActivateAccountView,
    CustomTokenObtainPairView,
    AddressListCreateView,
    AddressRetrieveUpdateDestroyView,
    AddressSetDefaultView,
    WishlistListView,
    WishlistDetailView,
    CreateUserWithRandomPasswordView,
    AddressFromOrderView,
    WishlistToggleView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    
    # Autenticação
    path('register/', RegisterView.as_view(), name='register'),
    path('register/auto/', CreateUserWithRandomPasswordView.as_view(), name='register-auto'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),

    # Encomendas
    path('orders/', UserOrderListView.as_view(), name='user-orders'),
    path('orders/<int:pk>/', UserOrderDetailView.as_view(), name='user-order-detail'),

    # Ativação
    path('activate/', ActivateAccountView.as_view(), name='activate'),

    # Moradas
    path('addresses/', AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressRetrieveUpdateDestroyView.as_view(), name='address-detail'),
    path('addresses/<int:pk>/set-default/', AddressSetDefaultView.as_view(), name='address-set-default'),

    # Favoritos (Wishlist)
    path('favourites/', WishlistListView.as_view(), name='favourites-list'),
    path('favourites/<int:pk>/', WishlistDetailView.as_view(), name='favourites-detail'),
    path('favourites/toggle/', WishlistToggleView.as_view(), name='favourites-toggle'),

    path('addresses/from-order/', AddressFromOrderView.as_view(), name='address-from-order'),
]