from autofill.models import DocumentTemplate
from django.contrib import admin


class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_file")
    fields = ("id", "name", "template_file")
    readonly_fields = ("id",)


admin.site.register(DocumentTemplate, DocumentTemplateAdmin)
