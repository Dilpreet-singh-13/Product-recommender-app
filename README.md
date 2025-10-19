### steps to run

- run  `scripts/preprocess_data.py` for pre processing
- run `uv run manage.py load_products` to load products into local database
- run `uv run manage.py upsert_to_pinecone.` to load data & generate embedding from pinecone
- 