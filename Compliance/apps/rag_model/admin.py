from django.contrib import admin

# Register your models here.
from .models import Audit, AttachedFolder,Document

# Register your models here.

admin.site.register(Audit)
admin.site.register(AttachedFolder)
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
     list_display = (
        'id', 'document_name','name', 'input_path', 'output_path',
        'operation_status', 'uploaded_at','doc_type','file_type')
   


   
