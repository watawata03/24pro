from django.db import models
from django.contrib.postgres.indexes import GinIndex

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    popularity = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            GinIndex(fields=['name'], opclasses=['gin_trgm_ops'], name='product_name_gin_idx'),
            GinIndex(fields=['description'], opclasses=['gin_trgm_ops'], name='product_description_gin_idx'),
        ]
