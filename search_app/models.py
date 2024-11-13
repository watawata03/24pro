from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.auth.models import User  # ユーザーモデルをインポート

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

    def get_badge(self):
        if self.popularity >= 100:
            return "ベストセラー"  # 人気度が100以上の場合
        elif self.popularity >= 50:
            return "話題の商品"  # 人気度が50以上の場合
        return None  # バッジがない場合

    class Meta:
        indexes = [
            GinIndex(fields=['name'], opclasses=['gin_trgm_ops'], name='product_name_gin_idx'),
            GinIndex(fields=['description'], opclasses=['gin_trgm_ops'], name='product_description_gin_idx'),
        ]

class SearchHistory(models.Model):
    query = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sort_by = models.CharField(max_length=50, blank=True, null=True)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"キーワード: {self.query}, カテゴリ: {self.category}, 最低価格: {self.min_price}, 最高価格: {self.max_price}, 並び替え: {self.sort_by}"
