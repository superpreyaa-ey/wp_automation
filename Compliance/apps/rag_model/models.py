from django.db import models
from django.conf import settings
# Create your models here.
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class UserEmailField(models.EmailField):
    description = "A field for storing user emails with @in.ey.com format."

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)  # Allow empty values
        kwargs.setdefault('null', True)   # Allow null values
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        # Custom validation for email format
        if not value.endswith('@in.ey.com'):
            raise ValidationError("Email must be in @in.ey.com format.")

class Audit(models.Model):
    # dragonfly_email = UserEmailField()
    audit_name = models.CharField(max_length=100)
    audit_year = models.PositiveIntegerField()
    audit_status = models.CharField(max_length=50, null=True, blank=True)  # Audit Created, Audit Updated, Vector DB In-progress, Vector DB Created, Analysis In-progress, Analysis Completed,
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
                    settings.AUTH_USER_MODEL, 
                    on_delete=models.CASCADE
                )
    created_at = models.DateTimeField(auto_now_add=True)
    pre_process = models.TextField(default=None,null=True,blank=True)
    out_putpath = models.TextField(default=None,null=True,blank=True)
    progress = models.IntegerField(default=0,null=True,blank=True)
    feature_request = models.CharField(default=None,max_length=80,null=True,blank=True)
    current_docid = models.IntegerField(default=None,null=True,blank=True)
    vertical = models.IntegerField(default=1)  # how many level are there
    # meetingtype = models.CharField(default=None,max_length=100,null=True,blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    
    def __str__(self):
        return self.audit_name

class AttachedFolder(models.Model):
    folder_name = models.CharField(max_length=255, null=True, blank=True)
    audit_id = models.ForeignKey(Audit, on_delete=models.CASCADE, blank=True, null=True)
    is_vector_db_in_progress = models.BooleanField(default=False)
    is_audit = models.CharField(default=None,max_length=50,null=True,blank=True)
    is_issue = models.CharField(default=None,max_length=50,null=True,blank=True)    
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    meeting_type = models.CharField(default=None,max_length=255,null=True,blank=True) 
    control_name = models.CharField(default=None,max_length=255,null=True,blank=True)
    # pre_process = models.TextField(default=None,null=True,blank=True)

    def __str__(self):
        return self.audit_id.audit_name
    
class Document(models.Model):
    document_name = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)

    name = models.CharField(max_length=100,null=True,blank=True)
    input_path = models.TextField(default=None,null=True,blank=True)
    file_type = models.CharField(max_length=10,null=True,blank=True)
    output_path = models.TextField(default=None,null=True,blank=True)
    # request_id = models.CharField(max_length=50,null=True,blank=True)
    operation_status =  models.CharField(max_length=50,null=True,blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    doc_type = models.CharField(max_length=10,null=True,blank=True)

    def _str_(self):
        return self.document_name.name
    
    

# class BackgroundTask(models.Model):
#     task_name = models.CharField(max_length=255)
#     folder_name = models.CharField(max_length=255)
#     audit_name = models.CharField(max_length=255, null=True, blank=True)
#     audit_year = models.PositiveIntegerField(null=True, blank=True)
#     status = models.CharField(max_length=50, null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#     for_user = models.ForeignKey(
#                     settings.AUTH_USER_MODEL, 
#                     on_delete=models.CASCADE
#                 )
#     created_at = models.DateTimeField(auto_now_add=True)