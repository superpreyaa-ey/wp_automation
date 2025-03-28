# Generated by Django 5.0.7 on 2025-01-24 08:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audit_name', models.CharField(max_length=100)),
                ('audit_year', models.PositiveIntegerField()),
                ('audit_status', models.CharField(blank=True, max_length=50, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pre_process', models.TextField(blank=True, default=None, null=True)),
                ('out_putpath', models.TextField(blank=True, default=None, null=True)),
                ('progress', models.IntegerField(blank=True, default=0, null=True)),
                ('feature_request', models.CharField(blank=True, default=None, max_length=80, null=True)),
                ('current_docid', models.IntegerField(blank=True, default=None, null=True)),
                ('vertical', models.IntegerField(default=1)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AttachedFolder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folder_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_vector_db_in_progress', models.BooleanField(default=False)),
                ('is_audit', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('is_issue', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('meeting_type', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('control_name', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('audit_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rag_model.audit')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('input_path', models.TextField(blank=True, default=None, null=True)),
                ('file_type', models.CharField(blank=True, max_length=10, null=True)),
                ('output_path', models.TextField(blank=True, default=None, null=True)),
                ('operation_status', models.CharField(blank=True, max_length=50, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('doc_type', models.CharField(blank=True, max_length=10, null=True)),
                ('document_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='rag_model.audit')),
            ],
        ),
    ]
