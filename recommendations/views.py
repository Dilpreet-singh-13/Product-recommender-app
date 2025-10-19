import os
import random
import time

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_GET
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pinecone import Pinecone

from .models import Product

load_dotenv()
NAMESPACE = os.getenv("PINECONE_NAMESPACE")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
SYSTEM_PROMPT = """
You are an AI that excels in making creative descriptions for furniture related products.
You are given the below information about a product (probably from amazon), based on the info, generate a creative description.
Given (Some of the below info may be missing):
- Title
- Description (provided by the seller)
- Price
- Manufacturer
- Country of origin
- Color
- Brand
- List of Categories
- Material
- Package Dimensions

The generated descriptions shouldn't be more than a small paragraph.
Return: Only return a creative description of the product based on the given info, nothing else.
""".strip()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_description(text: str) -> str:
    time.sleep(random.uniform(0.2, 0.6))
    response = None
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # disable thinking
                system_instruction=SYSTEM_PROMPT
            ),
            contents=text
        )
    except Exception as e:
        print(f"Error occurred while generating description: {e}")

    return response.text.strip() or ""


def recommend_page_view(request):
    return render(request, 'recommendations/recommend_page.html')


@require_POST
def recommend_products_view(request):
    query_text = request.POST.get('user-prompt', '').strip()
    if not query_text:
        html = render_to_string("recommendations/partial_suggested_products.html",
                                {"products": [], "query": query_text})
        return HttpResponse(html)

    response = index.search(
        namespace=NAMESPACE,
        query={
            "inputs": {"text": query_text},
            "top_k": 5
        },
        fields=["id"]
    )

    product_id_list = [p["_id"] for p in response["result"]["hits"]]
    products_qs = Product.objects.filter(unique_id__in=product_id_list)
    products_map = {p.unique_id: p for p in products_qs}
    ordered_products = [products_map.get(pid) for pid in product_id_list if products_map.get(pid)]

    html = render_to_string("recommendations/partial_suggested_products.html",
                            {"products": ordered_products, "query": query_text})
    return HttpResponse(html)


@require_GET
def generate_product_description_view(request, unique_id: str):
    product = get_object_or_404(Product, unique_id=unique_id)
    # Creative description already generated, so return the same
    if product.generated_description:
        html = render_to_string("recommendations/partial_product_card.html", {"product": product})
        return HttpResponse(html)

    product.generated_description = generate_description(product.combined_text)
    product.save()

    html = render_to_string("recommendations/partial_product_card.html", {"product": product})
    return HttpResponse(html)
