"""accounts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from integration.urls import integrationRouter
from guide.urls import guideRouter
from request.urls import requestRouter
from prepayment.urls import prepaymentRouter
from payment.urls import paymentRouter
from fact.urls import factRouter
from accountingEntry.urls import accountingEntryRouter
from django.conf import settings
from django.conf.urls.static import static
# from advance_report.urls import advanceReportRouter

admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('integration/', include('integration.urls')),
    path('', include('guide.urls')),
    path('', include('request.urls')),
    path('', include('prepayment.urls')),
    path('', include('fact.urls')),
    path('', include('accountingEntry.urls')),
    path('', include('payment.urls')),
    # path('', include('advance_report.urls')),

    path('api/v1/integration/', include(integrationRouter.urls)),
    path('api/v1/', include(guideRouter.urls)),
    path('api/v1/', include(requestRouter.urls)),
    path('api/v1/', include(prepaymentRouter.urls)),
    path('api/v1/', include(factRouter.urls)),
    path('api/v1/', include(accountingEntryRouter.urls)),
    path('api/v1/', include(paymentRouter.urls)),
    # path('api/v1/', include(advanceReportRouter.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
