import itertools
import os

from django.core.management import BaseCommand
from dotenv import load_dotenv
from pinecone import Pinecone, CloudProvider, AwsRegion, IndexEmbed

from recommendations.models import Product

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
EMBEDDING_MODEL = "llama-text-embed-v2"
MAX_BATCH_SIZE = 90
NAMESPACE = os.getenv("PINECONE_NAMESPACE")

load_dotenv()


def chunked(iterable, size):
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, size))


class Command(BaseCommand):
    help = "Upsert records to pinecone, automatically generating embedding for them"

    def handle(self, *args, **options):
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        if not pc.has_index(INDEX_NAME):
            print(f"Creating index: {INDEX_NAME}")
            index_model = pc.create_index_for_model(
                name=INDEX_NAME,
                cloud=CloudProvider.AWS,
                region=AwsRegion.US_EAST_1,
                embed=IndexEmbed(
                    model=EMBEDDING_MODEL,
                    field_map={"text": "combined_text"},
                    metric='cosine'
                )
            )
            print(f"Successfully created index: {INDEX_NAME}")

        print("Collecting all records...")
        index = pc.Index(INDEX_NAME)
        all_products = Product.objects.all().only("unique_id", "combined_text")

        records_list = []
        for product in all_products:
            records_list.append({
                "id": product.unique_id,
                "combined_text": product.combined_text
            })

        print(f"Beginning to upsert {len(records_list)} records...")

        count = 0
        for batch in chunked(records_list, MAX_BATCH_SIZE):
            index.upsert_records(NAMESPACE, list(batch))
            count += len(batch)
            print(f"Upserted {count}/{len(records_list)}")

        print("Successfully upserted all records.")
