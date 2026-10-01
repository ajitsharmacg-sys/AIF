from django.urls import path, include
import aif.views as views
import aif.api_views as api_views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"aif", api_views.AifView, r"aif")
router.register(r"aif_status", api_views.AifStatusView, r"aif_status")
router.register(r"aif_lines", api_views.AifLineView, r"aif_lines")
router.register(r"aif_line_status", api_views.AifLineStatusView, r"aif_line_status")
router.register(
    r"aif_customer_line", api_views.AifCustomerLineView, r"aif_customer_line"
)
router.register(r"aif_approver", api_views.AifApproverView, r"aif_approver")
router.register(r"exchange_rates", api_views.ExchangeRatesViewSet, r"exchange_rates")
router.register(
    r"master_price_list", api_views.MasterPriceListView, r"master_price_list"
)
router.register(r"cdh_customers", api_views.CDHCustomerViewSet, r"cdh_customers")
router.register(
    r"nso_currency_opunit",
    api_views.NSOCurrencyOpUnitConfigViewSet,
    r"nso_currency_opunit",
)
router.register(r"om_emails", api_views.OMEmailsConfigViewSet, r"om_emails")


urlpatterns = [
    path("", views.aif_index, name="aif_index"),
    path("api/v1/", include(router.urls)),
    path("aif/<str:aif_id>/", views.aif_view),
    path("workflow/", views.workflow),
]
