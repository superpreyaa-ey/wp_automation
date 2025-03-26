from django.shortcuts import render

from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from apps.rag_model.models import Audit, Document,AttachedFolder
import zipfile
import pandas as pd
from django.http import HttpResponse
import os

from tqdm import tqdm
from django.http import Http404
from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
import shutil
from apps.rag_model.views import convert_word_to_pdf
import datetime
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import sweetify
import time
#****************************** using rag_model library *****************************************************************************************************************************
from apps.rag_model.views import handle_uploaded_file,unzip_files,create_document_entries,get_latest_audit_and_documents,categorize_excel_files

def dashboard_committee(request):
    # Get the current time in America/New_York timezon
    return render(request, 'usecase_three/dashboard.html')


# from apps.rag_model.STRUCTURE_OUTPUT.data_preprocessing import vaidate_wp_is_main        
def create_qa_audit(request):
    feature = None
    sheet_names =None
    if request.method == 'POST':
        audit_name = request.POST.get('audit_name')
        audit_year = request.POST.get('audit_year')
        feature = request.POST.get('feature', None)

        print(f"Feature Requested >>>>>>>>>>>>>>>>> : {feature}")
        
        files = request.FILES.getlist('file')
        # flag = request.POST.get('fileType')
        flag = None
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
                
                create_document_entries(extracted_folder_path, audit,preprocess_path,flag,control_name=None) 
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
                        # ret_val = vaidate_wp_is_main(issue_draft,workpaper,preprocess_path)
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

        return render(request, 'usecase_three/dashboard.html',context)

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

    # import pdb; pdb.set_trace()
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
    return render(request, 'usecase_three/iframe.html',context)


def is_pdf(file_path):
    # Check if the file has a '.pdf' extension
    return file_path.lower().endswith('.pdf')

import os
import pandas as pd

def process_excel_file(different_client, outputpath):
    if os.path.splitext(different_client)[1].lower() == '.xlsx':
        is_excel = True
        
        # Get the absolute paths
        absolute_pdf_file_path = os.path.abspath(outputpath)
        absolute_file_path = os.path.abspath(different_client)

        try:
            # Use a context manager to handle the Excel file
            with pd.ExcelFile(absolute_file_path) as excel_file:
                sht_names = excel_file.sheet_names  # Get the sheet names
                df = pd.read_excel(excel_file, sheet_name=sht_names[0])  # Read the first sheet
                d_lst = df.to_dict(orient='records')  # Convert to dictionary
        except FileNotFoundError:
            print(f"Error: The file '{different_client}' was not found.")
        except PermissionError:
            print(f"Error: Permission denied when trying to access '{different_client}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    return is_excel,absolute_pdf_file_path,absolute_file_path,d_lst,sht_names



@csrf_exempt
def qa_approval(request):
    cust = request.user
    sheet_names = None
    print(f" usecase3 {request}")
    if request.method == 'POST':
        # audit_id = request.POST.getlist('check[]')
        audit_id = request.POST.getlist('check')
        audit_id = audit_id[0]
        org_audit = Audit.objects.get(id=audit_id)
        outputpath = org_audit.out_putpath

        final_outputpath =  '/'+ outputpath.replace('\\', '/')
        is_external_client = True
        print(f" collection of id of {cust} {audit_id}")
        s1 = 'Audit Report'
        feature = 'QA of Audit'

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
 
            is_excel = False
            if is_external_client == True:
                """ demo """
            #    static\media\Test\USE_CASE3
                different_client = 'static\\media\\Test\\USE_CASE3\\QA Checklist.xlsx' 

                """ orginal"""
                d_lst = None
                
                
                if os.path.splitext(different_client)[1].lower() == '.xlsx':
                    is_excel,absolute_pdf_file_path,absolute_file_path,d_lst,sht_names=process_excel_file(different_client, outputpath)
                   
                    # absolute_pdf_file_path = os.path.abspath(outputpath)
                    
                    # absolute_file_path = os.path.abspath(different_client)
                    # df = pd.read_excel(absolute_file_path)
                    # excel_file = pd.ExcelFile(absolute_file_path)
                    # # # Get the sheet name
                    # sht_names = excel_file.sheet_names
                    # d_lst = df.to_dict(orient='records')
                    
                    converted = True
                
                else:
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
                            if is_excel == False:
                                file_item = '/'+'Internal_Audit_Report.pdf'
                                org_audit.out_putpath = final_outputpath + file_item
                            else:
                                file_item = '/'+'QA Checklist.xlsx'
                                org_audit.out_putpath = final_outputpath + file_item
                            org_audit.uploaded_at =datetime.datetime.now()
                            org_audit.save()
                else:
                    pass
                
            time.sleep(60)
            sweetify.multiple(request, args1)
            
            audits = Audit.objects.filter(created_by = request.user,feature_request=feature,is_active=True).order_by('-id') 

            crt_doc = Audit.objects.get(id=audit_id)

            context = {
                'audits': audits,
                'current_document': current_document,#current_document.object_list[0].input_path,
                'data_list': data_list,
                'sheet':sheet_names if sheet_names else None,
                'final_report': final_outputpath + file_item,
                'Sheet':sht_names if sht_names else None,
                'd_lst': d_lst,
                'currentdocument': crt_doc
                
            }
            
            return render(request, 'usecase_three/horizonbody.html',context)
            # return redirect('HomeView')
        else:
            messages.success(request, ("You aren't authorized to view this page!"))
            # return redirect('HomeView')
            context ={
                'pdf_viewer':'sorted_outpath',

                'Regulator': None
            }
            return render(request, 'usecase_three/horizonbody.html',context)



def sheet_request(request):
    if request.method == 'GET':
        print(f"Full GET request: {request.GET}")

        # Extract parameters from the query string
        feature = request.GET.get('feature')
        doc_name = request.GET.get('doc_name')
        sheet = request.GET.get('Sheet')

        print(f"Sheet: {sheet}, Document: {doc_name}, Feature: {feature}")        
        
        is_audit,is_issue,meeting_type,control_name,first_attached_folder,latest_audit, documents = get_latest_audit_and_documents(request, feature)

       
        if documents:
            rt_doc = Audit.objects.get(out_putpath=doc_name)
            doc_path = rt_doc.out_putpath
            file_path = doc_path
            # Read the specified sheet from the Excel file
            get_base_path = os.getcwd() + file_path

            absolute_file_path = os.path.abspath(get_base_path)
            try:
                with pd.ExcelFile(absolute_file_path) as xls:
                    sheet_df = pd.read_excel(xls, sheet_name=sheet)
                    data_list = sheet_df.to_dict(orient='records')
                    sheet_names = xls.sheet_names
            except PermissionError as e:
                print(f"Permission error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
            
            # Determine if this is an HTMX request
            if 'HX-Request' in request.headers:
                # Render only the partial content for HTMX request
                template_name = 'usecase_three/qa_dattable.html'
            else:
                # Render the full page for a normal request
                # current_document = None  # Update as necessary
                template_name = 'usecase_three/iframe.html'

            # Add necessary context for rendering
            context = {
                # 'current_document': current_document,
                'audits': latest_audit,  # or other relevant variable
                'd_lst': data_list,
                'final_report': None,  # Update as necessary
                'get_audit_name': None,  # Update as necessary
                'Sheet': sheet_names if sheet_names else None,
                'currentdocument': rt_doc,
                'currentsheet': sheet
                
            }

            # Render the appropriate template
            return render(request, template_name, context)
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def downloadexcel(request, pk_test):

    audit = Audit.objects.get(id=pk_test)

    # Define the path to the Excel file
    different_client = 'static\\media\\Test\\USE_CASE3\\QA Checklist.xlsx'  # Replace with actual file path
    file_path = os.path.abspath(different_client)
    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file in binary mode for serving
        with open(file_path, 'rb') as file:
            # Create an HttpResponse with the correct MIME type for Excel files
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            # Set the content-disposition header to prompt the user to download the file
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    else:
        # If the file is not found, return an error response
        return HttpResponse("The requested file does not exist.", status=404)