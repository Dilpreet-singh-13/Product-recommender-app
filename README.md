# Product-recommender-app

A full stack AI powered web app that gives product recommendations based on user query.

## 💻 Run Locally

**Prerequisites:**

- Python installed
- A [Pinecone](https://www.pinecone.io/) account
- A Google AI API key from [Google AI Studio](https://aistudio.google.com/app/api-keys)

1. Clone the project and install dependencies

```bash
git clone https://github.com/Dilpreet-singh-13/Product-recommender-app.git
cd Product-recommender-app
# Install the uv pacaage manger
pip install uv
# Create a virtual environment
uv venv
.venv\Scripts\activate On Unix or MacOS use `source .venv/bin/activate`
# Install dependencies
uv sync
```

2. Initial Setup

```bash
uv run manage.py makemigrations
uv run manage.py migrate
```

3. Setup environment variables

```bash
cp .env.example .env # Edit .env with your API keys
```

4. Data Related scripts

```bash
cd scripts
uv run preprocess_data.py
cd ..

# Populate local and cloud database
uv run manage.py load_products
uv run manage.py upsert_to_pinecone
```

5. Run the local web server

```bash
uv run manage.py runserver
```

Then visit `http://127.0.0.1:8000/recommend/`