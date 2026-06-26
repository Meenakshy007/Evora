from django.db import models

class HaircareProducts(models.Model):
    name=models.CharField(max_length=200)
    category=models.CharField(max_length=200)
    suitable=models.BooleanField(default=True)
    hair_type=models.CharField(max_length=200)
    hair_pattern=models.CharField(max_length=200)
    scalp_condition=models.CharField(max_length=200)
    product_link=models.URLField(max_length=200)
    image=models.ImageField(upload_to='haircare-products')
    def __str__(self):
        return self.name


class SkincareProducts(models.Model):
    name = models.CharField(max_length=200)
    skin_type = models.CharField(max_length=200)
    primary_concern = models.CharField(max_length=200)
    secondary_concern = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    suitable = models.BooleanField(default=True) # <-- Crucial missing field added here
    product_link = models.URLField(max_length=200)
    image = models.ImageField(upload_to='skincare-products', blank=True, null=True)

    def __str__(self):
        return self.name