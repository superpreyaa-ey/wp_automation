import comtypes.client
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import Audit, Document,AttachedFolder
import zipfile
import pandas as pd
from django.http import HttpResponse
A1,I1 ='Audit','Issue'
from tqdm import tqdm
from django.http import Http404
from .tasks import go_to_sleep

from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# Create your views here.
from apps.rag_model.models import Audit ,AttachedFolder,Document #, BackgroundTask
from .models import Token



def get_latest_audit_and_documents(request,feature):
    try:
        # Retrieve the latest active Audit object created by the current user
        latest_audit = Audit.objects.filter(created_by=request.user,feature_request=feature,is_active=True).latest('created_at')
        print(latest_audit)
        # Retrieve all related Document objects for the latest Audit

        attached_folders = AttachedFolder.objects.filter(audit_id=latest_audit)
        
        # Extract the first related Document object (if any)
        if attached_folders.exists():
            first_attached_folder = attached_folders.first()
            # meeting_type = first_attached_folder.meeting_type
            is_issue = first_attached_folder.is_issue
            # is_audit = None
            # is_issue = None
        else:
            # meeting_type = first_attached_folder.meeting_type
            is_audit = None
            is_issue = None
            first_attached_folder = None
        documents = latest_audit.documents.all() 
    except Audit.DoesNotExist:
        # If no Audit object is found, set both to None
        latest_audit = None
        documents = None
        is_audit = None
        is_issue = None
        first_attached_folder = None

    # You can now return these objects, use them to render a template, or pass them to the context
    return is_audit,is_issue,first_attached_folder,latest_audit, documents

    
def handle_uploaded_file(f, filename, audit,flag,feature):
    # Define the destination directory path
    # audit.audit_name + '-' + str(audit.audit_year)
    if flag == None or flag == 1:
        # dest_dir = os.path.join('/static/media/project_files/audit_check_files/'+ str(audit.created_by) +'/' + audit.audit_name + '-' + str(audit.audit_year) + '/')
        dest_dir = os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature, audit.audit_name + '-' + str(audit.audit_year))
        
    elif flag == A1:
        dest_dir = os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature, audit.audit_name + '-' + str(audit.audit_year),flag)
    elif flag == I1:
        dest_dir = os.path.join('static','media','project_files','audit_check_files', str(audit.created_by),feature, audit.audit_name + '-' + str(audit.audit_year),flag)
    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    # Open the file and write its contents
    with open(os.path.join(dest_dir, filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def unzip_files(filename, audit,flag,feature):
    # Final Report Email - Retirement Strategies - Legacy Group Annuity SegmentBlock.zip'\
    extracted_folder_path = None

    if flag == None or flag == 1:
        # extracted_folder_path = os.path.join('/static/media/project_files/audit_check_files/' +str(audit.created_by) +'/'+ audit.audit_name + '-' + str(audit.audit_year) + '/', filename.split('.')[0])
        extracted_folder_path = os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature, audit.audit_name + '-' + str(audit.audit_year),filename.split('.')[0])
        with zipfile.ZipFile(os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature, audit.audit_name + '-' + str(audit.audit_year),filename), 'r') as zip_ref:
            zip_ref.extractall(extracted_folder_path)
            
    elif flag == A1:
        extracted_folder_path = os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature, audit.audit_name + '-' + str(audit.audit_year),A1,filename.split('.')[0])
        with zipfile.ZipFile(os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature,audit.audit_name + '-' + str(audit.audit_year),A1,filename), 'r') as zip_ref:
            zip_ref.extractall(extracted_folder_path)
    elif flag == I1:
        extracted_folder_path = os.path.join('static','media','project_files','audit_check_files', str(audit.created_by),feature,audit.audit_name + '-' + str(audit.audit_year),I1,filename.split('.')[0])
        with zipfile.ZipFile(os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature,audit.audit_name + '-' + str(audit.audit_year),I1,filename), 'r') as zip_ref:
            zip_ref.extractall(extracted_folder_path)
    return extracted_folder_path


import shutil
from django.core.exceptions import ObjectDoesNotExist

# ... other necessary imports ...
from django.db import transaction

def create_document_entries(extracted_folder_path, audit, preprocess_path,flag=None):
    try:
        # Fetch the audit object from the database using the provided audit_id
        # audit = Audit.objects.get(id=audit_id)

        # Get the total number of files for the progress bar
        total_files = sum([len(files) for r, d, files in os.walk(extracted_folder_path)])
        progress_bar = tqdm(total=total_files, desc='Processing files', unit='file')

        # Keep track of the number of processed files
        processed_files = 1

        # Iterate over the extracted files and create a database entry for each
        for root, dirs, files in os.walk(extracted_folder_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_extension = os.path.splitext(file)[1]
                    
                    if file_extension in ['.doc', '.docx']:
                        pdf_file_name = os.path.splitext(file)[0] + '.pdf'
                        pdf_file_path = os.path.join(root, pdf_file_name)

                        # Ensure the file exists before attempting to convert it
                        if os.path.exists(file_path):
                            # Use an absolute path for the conversion
                            absolute_file_path = os.path.abspath(file_path)
                            absolute_pdf_file_path = os.path.abspath(pdf_file_path)

                            converted = convert_word_to_pdf(absolute_file_path, absolute_pdf_file_path)
                            if converted == True:
                                print("Conversion successful.")
                                file_extension = '.pdf'
                                try:
                                    os.remove(absolute_file_path)
                                    print("Original file deleted.")
                                    file_path = pdf_file_path
                                except OSError as e:
                                    print(f"Error deleting the original file: {e}")
                            else:
                                print("Conversion failed.")
                            
                        else:
                            print(f"File does not exist: {file_path}")
                    
                    elif file_extension == '.txt' or file_extension == '.pptx':
                        
                        pdf_file_name = os.path.splitext(file)[0] + '.pdf'
                        pdf_file_path = os.path.join(root, pdf_file_name)

                        if os.path.exists(file_path):
                            absolute_file_path = os.path.abspath(file_path)
                            absolute_pdf_file_path = os.path.abspath(pdf_file_path)

                            converted = convert_text_to_pdf(absolute_file_path, absolute_pdf_file_path)
                            if converted:
                                print("Conversion successful.")
                                try:
                                    os.remove(absolute_file_path)
                                    print("Original file deleted.")
                                    file_path = pdf_file_path
                                except OSError as e:
                                    print(f"Error deleting the original file: {e}")
                            else:
                                print("Conversion failed.")
                        else:
                            print(f"File does not exist: {file_path}")
                    if file_extension.lower() == '.pdf':
                        
                        shutil.copy(file_path, preprocess_path)
                        print(f"File {file_path} copied to {preprocess_path}")
                    # elif file_extension.lower() == '.'
                    else:
                        print(f"File {file_path} does not have a .pdf extension.")
                        
                    document = Document.objects.create(
                        document_name=audit,
                        name=file, # need to changed
                        file_type=file_extension,
                        input_path= '/'+file_path.replace('\\', '/'),
                        # os.path.join(settings.MEDIA_ROOT, file_path)
                        operation_status='COMPLETE'
                    )
                    # Update the progress in the database
                    with transaction.atomic():
                        audit.progress = int((processed_files / total_files) * 50)
                        audit.save()

                    # Update the progress bar after each file is processed
                    processed_files +=1
                    progress_bar.update(1)

                except Exception as e:
                    # Log the error and continue with the next file
                    print(f"Failed to create a database entry for {file}: {e}")
                    progress_bar.update(1)  # Update the progress bar even if there's an error

        # Close the progress bar after all files are processed
        progress_bar.close()

    except Audit.DoesNotExist:
        print(f"Audit object with id {audit} does not exist.")
    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
    except zipfile.BadZipFile as bzf_error:
        print(f"Error: {bzf_error}")
    except ObjectDoesNotExist as odne_error:
        print(f"Error: {odne_error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")