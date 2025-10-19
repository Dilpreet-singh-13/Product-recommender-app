import ast
import re

import pandas as pd

DATASET_PATH = "../data/product_data.csv"  # original dataset path
OUTPUT_CSV_PATH = "../data/cleaned_data.csv"  # path where the pre-processed data will be stored


def parse_price(price_str):
    """Convert price like '$59.99' or '$1,299' -> float or None"""
    if not isinstance(price_str, str):
        return None
    price_str = price_str.strip()
    match = re.search(r"[\d,.]+", price_str)
    if match:
        try:
            return float(match.group(0).replace(",", ""))
        except ValueError:
            return None
    return None


def parse_list_column(value):
    """Convert stringified lists like "['a', 'b']" into actual Python lists"""
    if isinstance(value, list):
        return [str(v).strip() for v in value]
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed]
            else:
                return [value.strip()]
        except (ValueError, SyntaxError):
            return [value.strip()]
    return []


def combine_text(row):
    text = f"""
    Title: {row.get("title", "")}
    Description: {row.get("description", "")}
    Price: {row.get("price", "")}
    Brand: {row.get("brand", "")}
    Categories: {" ".join(row.get("categories", []))}
    Manufacturer: {row.get("manufacturer", "")}
    Material: {row.get("material", "")}
    Color: {row.get("color", "")}
    Country of origin: {row.get("country_of_origin", "")}
    """
    return text


def main():
    print(f"Loading data from dataset ...")
    df = pd.read_csv(DATASET_PATH)

    print("Cleaning and normalizing columns...")

    # Fill nulls and normalize text columns
    text_cols = [
        "title", "brand", "description", "manufacturer",
        "package_dimensions", "country_of_origin", "material", "color"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    # Non text columns
    df["price"] = df["price"].apply(parse_price)
    df["categories"] = df["categories"].apply(parse_list_column)
    df["images"] = df["images"].apply(parse_list_column)
    # To be used to generate embeddings
    df["combined_text"] = df.apply(combine_text, axis=1)

    # save to CSV
    df.to_csv(OUTPUT_CSV_PATH, index=False)


if __name__ == "__main__":
    main()
