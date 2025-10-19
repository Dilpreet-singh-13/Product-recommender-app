from django.db import models


class Product(models.Model):
    unique_id = models.CharField(max_length=100, unique=True, primary_key=True)
    title = models.TextField(blank=False)
    description = models.TextField(blank=True, null=True)
    # AI generated creative description
    generated_description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    price = models.FloatField(null=True, blank=True)

    categories = models.JSONField(default=list, blank=True)
    image_links = models.JSONField(default=list)

    manufacturer = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    package_dimensions = models.CharField(max_length=255, blank=True, null=True)
    country_of_origin = models.CharField(max_length=255, blank=True, null=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)

    # Text used for generating embeddings
    combined_text = models.TextField()

    def __str__(self):
        return self.title
