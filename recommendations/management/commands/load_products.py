import csv
import json
from pathlib import Path

from django.core.management import BaseCommand

from recommendations.models import Product

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CLEANED_DATA_PATH = PROJECT_ROOT / "data" / "cleaned_data.csv"


# GEMINI_MODEL = os.getenv("GEMINI_MODEL")
# SYSTEM_PROMPT = """
# You are an AI that excels in making creative descriptions for furniture related products.
# You are given the below information about a product (probably from amazon), based on the info, generate a creative description.
# Given (Some of the below info may be missing):
# - Title
# - Description (provided by the seller)
# - Price
# - Manufacturer
# - Country of origin
# - Color
# - Brand
# - List of Categories
# - Material
# - Package Dimensions
#
# Return: Only return a creative description of the product based on the given info, nothing else.
# """.strip()
#
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#
#
# def generate_description(text: str) -> str:
#     time.sleep(random.uniform(0.2, 0.5))
#     try:
#         response = client.models.generate_content(
#             model=GEMINI_MODEL,
#             config=types.GenerateContentConfig(
#                 thinking_config=types.ThinkingConfig(thinking_budget=0),  # disable thinking
#                 system_instruction=SYSTEM_PROMPT
#             ),
#             contents=text
#         )
#     except Exception as e:
#         print(f"Error occurred while generating description: {e}")
#
#     return response.text.strip() or ""


def safe_json_load(s):
    if not s or s.strip() in ["", "[]", "None", "null"]:
        return []
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # Attempt to fix single quotes or trailing commas
        try:
            s_fixed = s.replace("'", '"')
            return json.loads(s_fixed)
        except Exception:
            return []


class Command(BaseCommand):
    help = 'Loads products from csv file'

    def handle(self, *args, **options):
        with open(CLEANED_DATA_PATH, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                categories = safe_json_load(row.get("categories"))
                image_links = safe_json_load(row.get("images"))

                price_val = row.get('price')
                try:
                    price = float(price_val) if price_val not in (None, '') else None
                except ValueError:
                    price = None

                Product.objects.update_or_create(
                    unique_id=row['uniq_id'],
                    defaults={
                        "title": row.get('title', ''),
                        "description": row.get('description', ''),
                        "generated_description": "",
                        "brand": row.get('brand', ''),
                        "price": price,
                        "categories": categories,
                        "image_links": image_links,
                        "manufacturer": row.get('manufacturer', ''),
                        "package_dimensions": row.get('package_dimensions', ''),
                        "country_of_origin": row.get('country_of_origin', ''),
                        "material": row.get('material', ''),
                        "color": row.get('color', ''),
                        "combined_text": row.get('combined_text', '')
                    },
                )
        self.stdout.write(self.style.SUCCESS("✅ Products loaded successfully!"))
