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
import os
A1,I1 ='Audit','Issue'
from tqdm import tqdm
from django.http import Http404
from .tasks import go_to_sleep

# >>>>*************************************************************************** Usermanagement >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from apps.usermanagement.views import get_latest_audit_and_documents


def landing_page(request):
    # Get the current time in America/New_York timezone
    # go_to_sleep.delay(10)
    # time.sleep(10)

    current_time = timezone.now()
    welcome_msg = f"Welcome! The current time is {current_time}. I am EYQ, an application part of EY.ai, EYFabric and EY (for internal use)."
    # go_to_sleep.delay('for.text.py', 'celery is working in python')
    # go_to_sleep()
    # # Pass the welcome message to the template context
    # context = {'welcome_msg': welcome_msg}
    # return render(request, 'tabs.html', context)
    # return HttpResponse("Done")
    
    return render(request, 'tabs.html')

import comtypes.client
import os
    
def convert_word_to_pdf(word_file, pdf_file):
    # Initialize the COM library
    comtypes.CoInitialize()

    try:
        # Load the Word application
        # 'C:\\Prudential\\Code\\PROUD_Automation\\Compliance\\static\\media\\Test\\Aditya_birla\\Internal_Audit_Report.docx'
         
        # 'C:\\Prudential\\Code\\PROUD_Automation\\Compliance\\static\\media\\project_files\\audit_check_files\\shubham\\Audit Report Drafter\\Trial3-2024\\FM_PGIM\\Action Plans.docx'

        word = comtypes.client.CreateObject('Word.Application')
        doc = word.Documents.Open(word_file)
        doc.SaveAs(pdf_file, FileFormat=17)  # 17 represents the wdFormatPDF enumeration value
        doc.Close()
        word.Quit()
        conversion_success = True
    except Exception as e:
        print(f"An error occurred: {e}")
        conversion_success = False
    finally:
        # Uninitialize the COM library
        comtypes.CoUninitialize()
    
    return conversion_success

from fpdf import FPDF


def convert_text_to_pdf(text_file, pdf_file):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Use a default font
    pdf.set_font("Arial", size=12)

    try:
        with open(text_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                # Replace unsupported characters with a placeholder
                safe_line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 10, safe_line, ln=True)

        pdf.output(pdf_file)
        return True
    except Exception as e:
        print(f"An error occurred during Text to PDF conversion: {e}")
        return False




    
def handle_uploaded_file(f, filename, audit,flag,feature,control_name= None,process_name=None):
    # Define the destination directory path
    # audit.audit_name + '-' + str(audit.audit_year)
    if flag == None or flag == 1:
        # dest_dir = os.path.join('/static/media/project_files/audit_check_files/'+ str(audit.created_by) +'/' + audit.audit_name + '-' + str(audit.audit_year) + '/')
        dest_dir = os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature, audit.audit_name + '-' + str(audit.audit_year))    
    elif flag == A1:
        dest_dir = os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature, audit.audit_name + '-' + str(audit.audit_year),flag)
    elif flag == I1:
        dest_dir = os.path.join('static','media','project_files','audit_check_files', str(audit.created_by),feature, audit.audit_name + '-' + str(audit.audit_year),flag)
    elif control_name !=None or process_name !=None:
        dest_dir = os.path.join('static','media','project_files','audit_check_files', str(audit.created_by),feature,process_name, audit.audit_name + '-' + str(audit.audit_year),flag,control_name)
    else:
        dest_dir = os.path.join('static','media','project_files','audit_check_files', str(audit.created_by),feature, audit.audit_name + '-' + str(audit.audit_year),flag)

    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    # Open the file and write its contents
    with open(os.path.join(dest_dir, filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def unzip_files(filename, audit,flag,feature,control_name=None,process_name=None):
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
    elif control_name != None or process_name != None:
        extracted_folder_path = os.path.join('static','media','project_files','audit_check_files', str(audit.created_by),feature,process_name,audit.audit_name + '-' + str(audit.audit_year),flag,control_name,filename.split('.')[0])
        with zipfile.ZipFile(os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature,process_name,audit.audit_name + '-' + str(audit.audit_year),flag,control_name,filename), 'r') as zip_ref:
            zip_ref.extractall(extracted_folder_path)
    else:
        extracted_folder_path = os.path.join('static','media','project_files','audit_check_files', str(audit.created_by),feature,audit.audit_name + '-' + str(audit.audit_year),flag,filename.split('.')[0])
        with zipfile.ZipFile(os.path.join('static','media','project_files','audit_check_files',str(audit.created_by) ,feature,audit.audit_name + '-' + str(audit.audit_year),flag,filename), 'r') as zip_ref:
            zip_ref.extractall(extracted_folder_path)        
    return extracted_folder_path

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import glob
import pandas as pd
# Your script or views.py


from .models import Document  # Import the Document model

def categorize_excel_files(directory,audit):
    # Define the patterns for 'is' and 'wp'
    is_sheets = ['Issues', 'Action Plans', 'Defination']
    wp_sheets = ['Audit Sections', 'Workpapers', 'Defination']

    # Use glob to find all Excel files with .xlsx and .xls extensions in the specified directory
    excel_files = glob.glob(f'{directory}/*.xlsx') + glob.glob(f'{directory}/*.xls')

    for excel_file in excel_files:
        try:
            # Open the Excel file
            xls = pd.ExcelFile(excel_file)
            # Get the list of sheet names
            sheet_names = xls.sheet_names
            # Determine the category based on the sheet names
            if any(sheet in sheet_names for sheet in is_sheets):
                category = 'is'
            elif any(sheet in sheet_names for sheet in wp_sheets):
                category = 'wp'
            else:
                category = 'No matching sheet names found'
            # Update the document in the database
            doc_name = excel_file.split('\\')[-1]  # Extract the file name
            
            try:
                doc_obj = Document.objects.get(document_name=audit,name=doc_name)
                doc_obj.doc_type = category
                doc_obj.save()
                # print(f"Updated {doc_name} to category: {category}")
            except Document.DoesNotExist:
                print(f"Document with name {doc_name} does not exist in the database.")
        except Exception as e:
            # Handle any exceptions that occur
            print(f"Error processing {excel_file}: {e}")
    return True



# >>>>>>>>>>>>.. Save >>>>>>>>>>>>>>>>>>
import shutil
from django.core.exceptions import ObjectDoesNotExist

# ... other necessary imports ...
from django.db import transaction

def create_document_entries(extracted_folder_path, audit, preprocess_path,flag,control_name):
    try:
        print("inside create_document_entries======================1=================",extracted_folder_path,audit,preprocess_path,flag,control_name)

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
                    
                    elif file_extension.lower()  == '.txt' or file_extension.lower()  == '.pptx':
                        
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
   
                    if file_extension.lower() == '.pdf' or file_extension.lower()  == '.wav' or file_extension.lower()  == '.mp3' or file_extension.lower()  == '.wma':
                        
                        shutil.copy(file_path, preprocess_path)
                        print(f"File {file_path} copied to {preprocess_path}")
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


# from django.http import JsonResponse

def all_audit(request):

    audits = Audit.objects.get(created_by = request.user,is_active=True)
    progress = audit.progress
    
    audit_data = []
    for audit in audits:
        folders = AttachedFolder.objects.filter(audit_id=audit)
        print(folders)
        folder_list = []
        folder_dict = {}
        for folder in folders:
            folder_list.append({
                'id': folder.id,
                'folder_name': folder.folder_name,
                'is_vector_db_in_progress' : folder.is_vector_db_in_progress
            })
            # folder_list.append(folder.folder_name)
        
        audit_dict = {
            'id': audit.id,
            'audit_status': audit.audit_status,
            'uploaded_files':folder_list,
            # Add other fields you need
        }
        audit_data.append(audit_dict)

    return JsonResponse({'audits': audit_data})


        
from apps.rag_model.STRUCTURE_OUTPUT.data_preprocessing import vaidate_wp_is_main      
  
def create_audit(request):
    feature = None
    sheet_names =None
    if request.method == 'POST':
        audit_name = request.POST.get('audit_name')
        audit_year = request.POST.get('audit_year')
        feature = request.POST.get('feature', None)
        flag = request.POST.get('meeting_type', None)
        control_name = request.POST.get('control_name',None)
        print(f"Feature Requested >>>>>>>>>>>>>>>>> : {feature}")
        files = request.FILES.getlist('file')

        # for excel
        print(files)
        
        request_user = str(request.user)
        if Audit.objects.filter(audit_name=audit_name,created_by = request.user).exists():
            messages.success(request, 'Audit of name : '+audit_name+' already created.')
            audits = Audit.objects.filter(is_active=True)
            context = {
                'audits': audits
            }
            return redirect('index')

        # Create folder path
        folder_name = f"{audit_name}-{audit_year}"
        folder_path = os.path.join('static','media','project_files','audit_check_files',request_user ,feature, folder_name)
        preprocess_path = os.path.join('static','media','project_files','audit_check_files',request_user ,feature,folder_name,'Pre_Process')
        final_output_path = os.path.join('static','media','project_files','audit_check_files',request_user ,feature, folder_name,'Process_Output')
        # output_path = audit.out_putpath 
        print(f"Folder path: {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        os.makedirs(preprocess_path, exist_ok=True)
        os.makedirs(final_output_path, exist_ok=True)
        print("Folder created successfully")
        audit = Audit.objects.create(audit_name = audit_name,audit_year = audit_year,\
            created_by = request.user,audit_status = 'Audit Report Generated',pre_process=preprocess_path,out_putpath=final_output_path,feature_request=feature) #,uploaded_at =datetime.datetime.now())
        """ zip level """
        
        for file in files:
            entityname = file.name
            handle_uploaded_file(file, entityname, audit,flag,feature)
            extracted_folder_path = unzip_files(entityname, audit,flag,feature)
            # Save the filename to the database
            
            if extracted_folder_path:    

                attached_folder = AttachedFolder.objects.create(folder_name=entityname, audit_id=audit)
                
                create_document_entries(extracted_folder_path, audit,preprocess_path,flag,control_name) 
                """ need to update progress"""
                try:
                    results = categorize_excel_files(extracted_folder_path,audit)
                    """ validate call preprocessing """
                    
                    if results == True:
                        documents_obj = audit.documents.all()
                        workpaper_pth = documents_obj.filter(doc_type='wp').values_list('input_path', flat=True)
                        issue_doc_pth = documents_obj.filter(doc_type='is').values_list('input_path', flat=True)
                        workpaper = list(workpaper_pth)
                        issue_draft = list(issue_doc_pth)
                        """ need to update progress"""
                        ret_val = vaidate_wp_is_main(issue_draft,workpaper,preprocess_path)
                except:
                    pass
            print("File saved successfully")

        page = request.GET.get('page', 1)
        if feature == None:
            feature = request.GET.get('feature', None)
        else:
            pass
        audits = Audit.objects.filter(created_by = request.user,feature_request=feature,is_active=True).order_by('-id') 
        paginator = Paginator(documents_obj, 1)  # Show 1 document per page

        try:
            page_number = int(page)
            if page_number < 1:
                raise Http404("Page number is less than 1")
            current_document = paginator.page(page_number)

            # print(current_document[0].input_path)
        except (ValueError, TypeError):
            current_document = paginator.page(1)
        except PageNotAnInteger:
            current_document = paginator.page(1)
        except EmptyPage:
            current_document = paginator.page(paginator.num_pages)


        file_type = current_document.object_list[0].file_type
        file_path = current_document.object_list[0].input_path
        doc_id  = current_document.object_list[0].id
        get_base_path = os.getcwd() + file_path
        absolute_file_path = os.path.abspath(get_base_path)
        
        if file_type in ['.xls', '.xlsx']:
            print('Extracting data from Excel file...')
            latest_audit.current_docid = doc_id
            latest_audit.save()
            excel_file = pd.ExcelFile(absolute_file_path)

            # # Get the sheet names
            sheet_names = excel_file.sheet_names
            df = pd.read_excel(absolute_file_path)
            data_list = df.to_dict(orient='records')
        elif file_type == '.csv' or file_type == '.CSV':
            print('Extracting data from CSV file...')
            df = pd.read_csv(absolute_file_path)
            data_list = df.to_dict(orient='records')
        else:
            df = None
            data_list = None
            pass
        
        context = {
        'audits': audits,
        'current_document': current_document,
        'data_list': data_list,
        'sheet':sheet_names if sheet_names else None,
        'final_report': None
        }
            # if documents_obj is None:
        #     documents_obj = ['sample/path']

        # 'dashboard.html'
        return render(request, 'dashboard.html',context)

    page = request.GET.get('page', 1)
    
    feature = request.GET.get('feature', None)
    audits = Audit.objects.filter(created_by = request.user,feature_request=feature,is_active=True).order_by('-id') 
    # latest_audit, documents_obj = get_latest_audit_and_documents(request,feature)
    isaudit,isissue,first_attached_folder,latest_audit, documents_obj = get_latest_audit_and_documents(request,feature)
    paginator = Paginator(documents_obj, 1)  # Show 1 document per page
    
    try:
        page_number = int(page)
        if page_number < 1:
            raise Http404("Page number is less than 1")
        current_document = paginator.page(page_number)

        # print(current_document[0].input_path)
    except (ValueError, TypeError):
        current_document = paginator.page(1)
    except PageNotAnInteger:
        current_document = paginator.page(1)
    except EmptyPage:
        current_document = paginator.page(paginator.num_pages)

    file_type = current_document.object_list[0].file_type
    print(f"file path {file_type}")
    file_path = current_document.object_list[0].input_path
    doc_id = current_document.object_list[0].id
    get_base_path = os.getcwd() + file_path
    absolute_file_path = os.path.abspath(get_base_path)
    
    if file_type in ['.xls', '.xlsx']:
        print('Extracting data from Excel file...')
        
        latest_audit.current_docid = doc_id
        latest_audit.save()
        excel_file = pd.ExcelFile(absolute_file_path)

        # # Get the sheet names
        sheet_names = excel_file.sheet_names
        df = pd.read_excel(absolute_file_path)
        
        data_list = df.to_dict(orient='records')
    elif file_type == '.csv' or file_type == '.CSV':
        print('Extracting data from CSV file...')
        df = pd.read_csv(absolute_file_path)
        data_list = df.to_dict(orient='records')
    else:
        df = None
        data_list = None
        pass

    context = {
    'audits': audits,
    'current_document': current_document,
    'data_list': data_list,
    'sheet':sheet_names if sheet_names else None,
    'final_report': None
    
    }
    return render(request, 'usecase_one/iframe.html',context)




# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Process >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from django.views.decorators.csrf import csrf_exempt
import sweetify
import time
from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import datetime

def is_pdf(file_path):
    # Check if the file has a '.pdf' extension
    return file_path.lower().endswith('.pdf')

# import pdb; pdb.set_trace()

def handle_sheet_request(request):
    if request.method == 'GET':
        print(f"Full GET request: {request.GET}")

        # Extract parameters from the query string
        feature = request.GET.get('feature')
        doc_name = request.GET.get('doc_name')
        sheet = request.GET.get('sheet')
        
        print(f"Sheet: {sheet}, Document: {doc_name}, Feature: {feature}")        
        # Assuming `get_latest_audit_and_documents` is a function you have defined
        isaudit, isissue, first_attached_folder, latest_audit, documents = get_latest_audit_and_documents(request, feature)
        try:
            if doc_name.endswith('.docx') or doc_name.endswith('.pdf'):
                doc_name = ''
        except:
            pass
        if documents:
            if doc_name == '' or doc_name == ' ':
               doc_id =  latest_audit.current_docid
               filtered_byid = documents.filter(id=doc_id)
               doc_name = filtered_byid[0].name
               print(f" Document NAME >>>>>>>>>>: {doc_name}")
            else:
                pass
            
            filtered_documents = documents.filter(name=doc_name)
            if filtered_documents !=[]:
                doc_obj = filtered_documents[0]
                file_path = doc_obj.input_path
                # Read the specified sheet from the Excel file
                get_base_path = os.getcwd() + file_path
                absolute_file_path = os.path.abspath(get_base_path)
                xls = pd.ExcelFile(absolute_file_path)
                sheet_df = pd.read_excel(xls, sheet_name=sheet)
                data_list = sheet_df.to_dict(orient='records')
                sheet_names = xls.sheet_names
            

            # Determine if this is an HTMX request
            if 'HX-Request' in request.headers:
                # Render only the partial content for HTMX request
                template_name = 'usecase_one/dattable.html'
            else:
                # Render the full page for a normal request
                # current_document = None  # Update as necessary
                template_name = 'usecase_one/iframe.html'

            # Add necessary context for rendering
            context = {
                # 'current_document': current_document,
                'audits': latest_audit,  # or other relevant variable
                'data_list': data_list,
                'final_report': None,  # Update as necessary
                'get_audit_name': None,  # Update as necessary
                'sheet': sheet_names if sheet_names else None,
                'current_sheet': sheet, 
            }

            # Render the appropriate template
            return render(request, template_name, context)
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
@csrf_exempt
def approval(request):
    cust = request.user
    sheet_names = None
    if request.method == 'POST':
        audit_id = request.POST.getlist('check[]')
        
        audit_id = audit_id[0]
        org_audit = Audit.objects.get(id=audit_id)
        outputpath = org_audit.out_putpath

        final_outputpath =  '/'+ outputpath.replace('\\', '/')
        is_external_client = True
        print(f" collection of id of {cust} {audit_id}")
        s1 = 'Audit Report'
        feature = 'Audit Report Drafter'

        is_audit,is_issue,meeting_type,control_name,first_attached_folder,latest_audit, documents = get_latest_audit_and_documents(request,feature)
        if documents:
            # Set up pagination for documents
            page = request.GET.get('page', 1)
            paginator = Paginator(documents, 1)  # Show 1 document per page

            try:
                page_number = int(page)
                if page_number < 1:
                    raise Http404("Page number is less than 1")
                current_document = paginator.page(page_number)

                # print(current_document[0].input_path)
            except (ValueError, TypeError):
                current_document = paginator.page(1)
            except PageNotAnInteger:
                current_document = paginator.page(1)
            except EmptyPage:
                current_document = paginator.page(paginator.num_pages)


            file_type = current_document.object_list[0].file_type
            file_path = current_document.object_list[0].input_path
            get_base_path = os.getcwd() + file_path
            absolute_file_path = os.path.abspath(get_base_path)
            
            if file_type in ['.xls', '.xlsx']:
                print('Extracting data from Excel file...')

                df = pd.read_excel(absolute_file_path)
                excel_file = pd.ExcelFile(absolute_file_path)
                # # Get the sheet names
                sheet_names = excel_file.sheet_names
                data_list = df.to_dict(orient='records')
            elif file_type == '.csv' or file_type == '.CSV':
                print('Extracting data from CSV file...')
                df = pd.read_csv(absolute_file_path)
                data_list = df.to_dict(orient='records')
            else:
                df = None
                data_list = None
                pass
            
           
            msg = f"Report Generated Successfully" 
            args1 = dict(title=msg, icon='success', timer=9000,timerProgressBar='true', button="OK")
            
            if is_external_client == True:
                """ demo """
                # different_client = 'static\\media\\Test\\Aditya_birla\\Internal_Audit_Report.docx'
                different_client = 'static\\media\\Test\\SMA_DEMO\\SMA.docx' 
                # different_client = 'static\\media\\Test\\SMA_DEMO\\Internal_Audit_Report.pdf'
                # different_client = 'static\\media\\Test\\SMA_DEMO\\SMA.pdf'
                # different_client = 'static\\media\\Test\\Aditya_birla\\Internal_Audit_Report.pdf'
                """ orginal"""
                # different_client = 'static\\media\\Test\\FM.docx'
                # get_base_path = os.getcwd() + different_client
                # print(">>>> path ",different_client)
                
                absolute_pdf_file_path = os.path.abspath(outputpath)
                if is_pdf(different_client):
                    print("The file is a PDF based on the extension.")
                    converted = True
                    absolute_file_path = os.path.abspath(different_client)
                    
                else:
                    print("The file is not a PDF based on the extension.")
                    absolute_file_path = os.path.abspath(different_client)
                    converted = convert_word_to_pdf(absolute_file_path, absolute_pdf_file_path +'\\'+'Internal_Audit_Report.pdf') 
                

                
                if converted == True:
                    shutil.copy(absolute_file_path, absolute_pdf_file_path)
                    print(f"File {file_path} copied to {absolute_pdf_file_path}")

                    
                    if org_audit.progress != 100:
                        with transaction.atomic():
                            org_audit.progress = 100
                            org_audit.audit_status = 'Audit Completed'
                            org_audit.out_putpath = final_outputpath + '/'+'Internal_Audit_Report.pdf'
                            org_audit.uploaded_at =datetime.datetime.now()
                            org_audit.save()
                else:
                    pass
                
            time.sleep(23)
            sweetify.multiple(request, args1)
            
            audits = Audit.objects.filter(created_by = request.user,feature_request=feature,is_active=True).order_by('-id') 
            print(">>>",final_outputpath + '/'+'Internal_Audit_Report.pdf')
            context = {
                'audits': audits,
                'current_document': current_document,#current_document.object_list[0].input_path,
                'data_list': data_list,
                'sheet':sheet_names if sheet_names else None,
                'final_report': final_outputpath + '/'+'Internal_Audit_Report.pdf'
            }
            
            return render(request, 'usecase_one/horizonbody.html',context)
            # return redirect('HomeView')
        else:
            messages.success(request, ("You aren't authorized to view this page!"))
            # return redirect('HomeView')
            context ={
                'pdf_viewer':'sorted_outpath',

                'Regulator': None
            }
            return render(request, 'usecase_one/horizonbody.html',context)







def download_excel(request, pk_test):
    audit = Audit.objects.get(id=pk_test)
    # Path to your Word file
    # file_path = 'project_files/audit_result_files/' + audit.audit_name + '-' + str(audit.audit_year) + '/' + 'audit_output_file.docx'
    file_path = 'C:/Prudential/Code/PROUD_Automation/Compliance/static/media/Test/FM.docx'
    # 'Internal_Audit_Report.docx'
    # file_path = os.path.join(settings.BASE_DIR, 'audit_output_file.docx')
    
    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file in binary mode for serving
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    else:
        # Handle file not found scenario
        return HttpResponse("The requested file does not exist.", status=404)

def process(request):
    # go_to_sleep.delay(5)
    
    audit = Audit.objects.get(id=audit_id)
    user = request.user
    print("printing user-----------------------------------",user)
    # is_audit = request.GET.get('is_audit')
    # is_issue = request.GET.get('is_issue')
    obj = AttachedFolder.objects.filter(audit_id=audit.id, folder_name=folder_name)
    is_audit = obj[0].is_audit
    is_issue = obj[0].is_issue

    print(f"Audit {is_audit}")
    print(f"Audit {is_issue}")
    
    
    if is_audit != 0:
        flg = is_audit
    elif is_issue != 0:
        flg = is_issue
    else:
        flg = None

    # Create a new thread to run the background task
    # flg = 0 #

    # task_queue.put((create_vector_db_background, (audit, folder_name, user,flg)))
    msg = 'Vector DB creation is in progress, you can check notification for more information.'
    messages.success(request, msg)
    return redirect('index')
































def upload_view(request, audit_id):
    if request.method == 'POST':
        # Get the list of files from the request; 'folder[]' is the name attribute of your file input
        files = request.FILES.getlist('folder')
        print(files)
        
        flag = request.POST.get('fileType')
        flag = int(flag)
        print(f"Flag respnse:{flag}")
        
        # Iterate over each file and handle them
        for file in files:

            audit = Audit.objects.get(id=audit_id)
            filename = file.name
            if flag == None or flag == 1:
                uploaded_folders = list(AttachedFolder.objects.filter(audit_id=audit_id).values_list('folder_name', flat=True))
                if filename in uploaded_folders:
                    msg = 'File with name ' + filename + ' already present.'
                    messages.error(request, msg)
                    return redirect('index')

            # Save the filename to the database
            
            if flag == None or flag == 1:       
                attached_folder = AttachedFolder.objects.create(folder_name=filename, audit_id=audit)
            elif flag == 2:
                # 
                attached_folder = AttachedFolder.objects.create(folder_name=filename, audit_id=audit,is_audit=flag)
            elif flag == 3:
                attached_folder = AttachedFolder.objects.create(folder_name=filename, audit_id=audit,is_issue=flag)
            # You can further process the files here if needed
            messages.success(request, 'File uploaded successfully.')
    return redirect('index')