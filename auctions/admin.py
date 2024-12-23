from django.contrib import admin
from .models import User, Listing, Category_name, Comment
# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Category_name)
admin.site.register(Comment)

