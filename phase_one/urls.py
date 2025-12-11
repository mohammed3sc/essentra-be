from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
# router.register(r'open-orders-list', OpenOrdersViewSet, basename='openorders')
router.register(r'refresh-open-orders', RefreshOpenOrder, basename='refresh-openorder')
# router.register(r'open_orders-pivot-table', OpenOrderPivotTable, basename='order-pivot-table')
# router.register(r'stock-data-list', StockDataViewSet, basename='stock-data')
# router.register(r'stock_data-pivot-table', StockDataPivotTable, basename='stock-pivot-table')
# router.register(r'bom-list', BomViewSet, basename='bom')
router.register(r'customer-list', CustomerViewSet, basename='customer')
router.register(r'lead-time-list', LeadTimeViewSet, basename='leadtime')
router.register(r'master-supply-code', MasterSupplyViewSet, basename='master_supply_code')
router.register(r'export-pivot', ExportPivotXlsx, basename='export-pivot')

urlpatterns = [ 
   
    path('', include(router.urls)),
    # path('route-list/', RouteViews.as_view(), name="route_list"),
    # path('purchase-sas-list/', PurchaseSasViews.as_view(), name="purchasesas_list"),
    # path('master-data-list/', MasterDataViews.as_view(), name="masterdata_list"),
    # path('work-order-list/', WorkOrderViews.as_view(), name="workorder_list"),
    path('event-list/', EventViews.as_view(), name="event_list"),
    path('file-upload/', FileUploadView.as_view(), name="file_upload"),
    path('export-csv/', ExportCSVView.as_view(), name="export-csv"),
    
    path('open-orders/<int:pk>/', OpenOrdersDetail.as_view(), name='oo-detail'),
    path('bom/<int:pk>/', BomDetail.as_view(), name='oo-detail'),
    path('stock-data/<int:pk>/', StockDataDetail.as_view(), name='oo-detail'),
    path('lead-time/<int:pk>/', EditLeadTime.as_view(), name='edit-leadtime'),
    # path('verbose/',verbose,name='verbose')

    # SQL APIs
    path('bom-list/', BomList.as_view(), name='bom-list'),
    path('bom_edit/<int:pk>/', BomEdit.as_view(), name='bo-edit'),
    path('open-orders-list/', OpenOrdersList.as_view(), name='oo-list'),
    path('stock-data-list/', StockDataList.as_view(), name='stock-list'),
    path('route-list/', RouteList.as_view(), name='route-list'),
    path('work-order-list/', WorkOrderList.as_view(), name='work-list'),
    path('master-data-list/',MasterList.as_view(), name='masterdata_list'),
    path('purchase-sas-list/',PurchaseList.as_view(), name='purchase_list'),
    path('open_orders-pivot-table/', OrderBookPivot.as_view(), name="order-pivot"),
    path('stock_data-pivot-table/', StockPivot.as_view(), name="stock-pivot"),
    path('bomorder-book-list/', BomOrderBookList.as_view(), name="bom-order-book"),
    path('bomorder_book-pivot-table/',BomOrderBookPivot.as_view(),name="bomorderbook-pivot"),
    path('bomorderbook_pivottablo_list/',BomorderbookTabloList.as_view(),name="bomorderbook_pivottablo_list"),
    path('final-list/',FinalList.as_view(),name="final_list"),
    path('side-bar-count/',SidebarCount.as_view(),name="side_bar_count"),



]