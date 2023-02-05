from django.contrib import admin

from usage.models import Charge, OpenAIModel, Organization

# Register your models here.


@admin.register(Organization)
class OrgAdmin(admin.ModelAdmin):
    list_display = ['openai_id', 'name']


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ['organization', 'tokens_used', 'model', 'created']
    list_filter = ['organization', 'model']
    date_hierarchy = 'created'


@admin.register(OpenAIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_1k']
