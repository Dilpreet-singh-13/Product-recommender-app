from django.urls import path

from .views import recommend_page_view, recommend_products_view, generate_product_description_view

app_name = 'recommendations'
urlpatterns = [
    path('recommend/', recommend_page_view, name='recommend_page_view'),
    path('recommend/query/', recommend_products_view, name='recommend_products'),
    path('generate-description/<str:unique_id>/', generate_product_description_view,
         name='generate_product_description'),
]
