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
A1,I1 ='Audit','Issue'
from tqdm import tqdm
from django.http import Http404
from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
import shutil
from apps.rag_model.views import convert_word_to_pdf
import datetime
#****************************** using rag_model library *****************************************************************************************************************************
from apps.rag_model.views import handle_uploaded_file,unzip_files,create_document_entries,get_latest_audit_and_documents



from django.db import IntegrityError
# Create your views here.



def audit_attached_folder(audit, entityname, extracted_folder_path, flag):
    """
    Create or update an AttachedFolder instance based on a flag.

    :return: A tuple containing the AttachedFolder instance and a boolean indicating creation status.
    """
    # attached_folder = AttachedFolder.objects.create(folder_name=entityname, audit_id=audit,is_issue=flag)
    try:

        attached_folder = None
        attached_folder_created = False
        if extracted_folder_path:
            defaults = {'folder_name': entityname}  # Set the folder_name in defaults
            if flag == A1:  # Use quotes around A1
                defaults['is_audit'] = flag
            elif flag == I1:  # Use quotes around I1
                defaults['is_issue'] = flag

            attached_folder, attached_folder_created = AttachedFolder.objects.update_or_create(
                audit_id=audit,  # Use audit.id to filter by the audit's primary key
                defaults=defaults
            )

    except IntegrityError:
        # Handle the exception if there is a uniqueness constraint violation
        raise  # Re-raise the exception after logging or handling it as needed

    return attached_folder, attached_folder_created

# **********************************************************************************************************************************************************************************
def dashboard_committee(request):
    # Get the current time in America/New_York timezon
    return render(request, 'usecase_two/dashboard.html')


def createaudit(request):
    feature = None
    if request.method == 'POST':
        audit_name = request.POST.get('audit_name')
        audit_year = request.POST.get('audit_year')
        feature = request.POST.get('feature', None)
        flag = request.POST.get('fileType', None)
        files = request.FILES.getlist('file')
        
        print(f"Flag respnse:{flag}")
        # files = request.FILES.getlist('folder')
        # print(f"Feature Requested >>>>>>>>>>>>>>>>> : {feature}")
        # print("GET LENGTH >>>>>>>>>>>>>>>>>>>>>>>>.",len(request.POST))  # Add this line to debug
        # print("FILES Data:", request.FILES)
        # print("FILES :", files)
        request_user = str(request.user)
        # Create folder path
        # 
        folder_name = f"{audit_name}-{audit_year}"
        folder_path = os.path.join('static','media','project_files','audit_check_files',request_user ,feature, folder_name)
        preprocess_path = os.path.join('static','media','project_files','audit_check_files',request_user ,feature, folder_name,'Pre_Process')
        final_output_path = os.path.join('static','media','project_files','audit_check_files',request_user ,feature, folder_name,'Process_Output')
        # output_path = audit.out_putpath 

        os.makedirs(folder_path, exist_ok=True)
        os.makedirs(preprocess_path, exist_ok=True)
        os.makedirs(final_output_path, exist_ok=True)


        try:
            audit, created = Audit.objects.get_or_create(
                audit_name=audit_name,
                audit_year=audit_year,
                feature_request=feature,

                defaults={
                    'created_by': request.user,
                    'audit_status': 'Committee Report Generated',
                    'pre_process': preprocess_path,
                    'out_putpath': final_output_path
                }
            )
            if not created:
                # The audit already exists, so update it
                audit.audit_status = 'Committee Report Generated' #'Audit Updated'  # Assuming you want to change the status on update
                audit.pre_process = preprocess_path
                audit.out_putpath = final_output_path
                audit.feature_request = feature
                # uploaded_at =datetime.datetime.now(),
                audit.save(update_fields=['audit_status', 'pre_process', 'out_putpath', 'feature_request'])
        except IntegrityError:

            pass

        """ zip level """
        get_audit_name = audit.audit_name 
        get_audit_year = audit.audit_year
        for file in files:
            entityname = file.name
            handle_uploaded_file(file, entityname, audit,flag,feature)
            extracted_folder_path = unzip_files(entityname, audit,flag,feature)
            
            if extracted_folder_path: 
                attached_folder, attached_folder_created = audit_attached_folder(audit,entityname, extracted_folder_path, flag)
                create_document_entries(extracted_folder_path, audit,preprocess_path,flag,control_name=None) 
                time.sleep(10)
        page = request.GET.get('page', 1)
        if feature == None:
            feature = request.GET.get('feature', None)
        else:
            pass
        
        audits = Audit.objects.filter(created_by = request.user,feature_request=feature,is_active=True).order_by('-id') 

            
        isaudit,isissue,first_attached_folder,latest_audit, documents_obj = get_latest_audit_and_documents(request,feature)

        # if documents_obj !=[]: #first_attached_folder.folder_name
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
        get_base_path = os.getcwd() + file_path
        absolute_file_path = os.path.abspath(get_base_path)
        
        if file_type in ['.xls', '.xlsx']:
            print('Extracting data from Excel file...')
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

        if isaudit:
            isaudit =True
        else:
            isaudit =False
        if isissue:
            isissue =True
        else:
             isissue =False
            
        print(f"Context data :is_audit':{isaudit} ,'is_issue':{isissue},'folder_name':{first_attached_folder.folder_name}")

        context = {
        'audits': audits,
        'current_document': current_document,
        'data_list': data_list,
        'final_report': None,
        'is_audit':isaudit,
        'is_issue':isissue,
        'folder_name':first_attached_folder.folder_name,
        'get_audit_name':get_audit_name,
        'get_audit_year':get_audit_year,
        }
        if request.headers.get('HX-Request'):
            #
            success_message = f"File Uploaded Successfully"
            args1 = dict(title=success_message, icon='info', timer=9000,timerProgressBar='true', button="OK")
            sweetify.multiple(request, args1)
            print(f" HX REQUEST >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Accepted")
            return render(request, 'usecase_two/horizonbody.html', context)
        else:
            return render(request, 'usecase_two/dashboard.html',context)
    


    page = request.GET.get('page', 1)

    if feature == None:
        feature = request.GET.get('feature', None)
    else:
        pass

    print(f">>>>>>>>>>>>>>>>>FEATURE REQUEST >>>>>>>>>>>>>>>>>>>>{feature}")
    audits = Audit.objects.filter(created_by = request.user,feature_request=feature,is_active=True).order_by('-id') 

    isaudit,isissue,first_attached_folder,latest_audit, documents_obj = get_latest_audit_and_documents(request,feature)
    get_audit_name = latest_audit.audit_name 
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
    get_base_path = os.getcwd() + file_path
    absolute_file_path = os.path.abspath(get_base_path)
    
    if file_type in ['.xls', '.xlsx']:
        print('Extracting data from Excel file...')
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
    if isaudit:
        isaudit =True
    else:
        isaudit =False
    if isissue:
        isissue =True
    else:
        isissue =False
    context = {
    'audits': audits,
    'current_document': current_document,
    'data_list': data_list,
    'final_report': None,
    'is_audit':isaudit,
    'is_issue':isissue,
    'folder_name':first_attached_folder.folder_name,
    'get_audit_name':get_audit_name,
    }
    
    # 'dashboard.html'
    return render(request, 'usecase_two/iframe.html',context)




from django.views.decorators.csrf import csrf_exempt
import sweetify
import time
from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage



import os
from comtypes.client import CreateObject
import pythoncom 



def convert_pptx_to_pdf(pptx_path, output_pdf_path):
    # Check if the file extension is .pptx
    if not pptx_path.lower().endswith('.pptx'):
        raise ValueError("The file provided is not a .pptx file.")
    
    # Ensure the PowerPoint file exists
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"The file {pptx_path} does not exist.")
    
    # Initialize COM library
    pythoncom.CoInitialize()
    
    try:
        # Initialize PowerPoint application
        powerpoint = CreateObject("Powerpoint.Application")
        
        # Open the PowerPoint file
        presentation = powerpoint.Presentations.Open(pptx_path)
        
        # Convert to PDF
        presentation.SaveAs(output_pdf_path, FileFormat=32)  # 32 corresponds to the PDF format in PowerPoint
        print(f"Converted '{pptx_path}' to '{output_pdf_path}' successfully.")
    except Exception as e:
        raise RuntimeError(f"Failed to convert {pptx_path} to PDF. Error: {e}")
    finally:
        # Close the presentation and quit PowerPoint
        if 'presentation' in locals():
            presentation.Close()
        if 'powerpoint' in locals():
            powerpoint.Quit()
        
        # Uninitialize COM library
        pythoncom.CoUninitialize()


@csrf_exempt
def approval_committee(request):
    cust = request.user
    if request.method == 'POST':
        audit_id = request.POST.getlist('check[]')

        audit_id = audit_id[0]
        org_audit = Audit.objects.get(id=audit_id)
        outputpath = org_audit.out_putpath

        final_outputpath =  '/' + outputpath.replace('\\', '/')
        is_external_client = False
        print(f" collection of id of {cust} {audit_id}")
        s1 = 'Audit Report'
        feature = 'Audit Committee Summary Report Drafter'
        
        is_audit,is_issue,meeting_type,control_name,first_attached_folder,latest_audit, documents = get_latest_audit_and_documents(request,feature)
        
        if documents:
            # Set up pagination for documents
            page = request.GET.get('page', 1)
            # if feature == None:
            #     feature = request.GET.get('feature', None)
            # else:
            #     pass
            paginator = Paginator(documents, 1)  # Show 1 document per page

            try:
                page_number = int(page)
                if page_number < 1:
                    raise Http404("Page number is less than 1")
                current_document = paginator.page(page_number)
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
                # Aditya_birla\TXT
                different_client = 'static\\media\\Test\\Aditya_birla\\Internal_Audit_Report.docx'
                """ Orginal """
                
                # get_base_path = os.getcwd() + different_client
                # print(">>>> path ",different_client)
                absolute_file_path = os.path.abspath(different_client)
                absolute_pdf_file_path = os.path.abspath(outputpath)

                converted = convert_word_to_pdf(absolute_file_path, absolute_pdf_file_path +'\\'+'Internal_Audit_Report.pdf') 
                if converted == True:
                    shutil.copy(absolute_file_path, absolute_pdf_file_path)
                    print(f"File {file_path} copied to {absolute_pdf_file_path}")
                else:
                    pass
                
            sweetify.multiple(request, args1)
            
            # c:\Users\WH966TA\Downloads\Sample AC report.pptx
            if documents[0].file_type == '.txt':
                use_case_2 = 'static\\media\\Test\\USE_CASE2\\TXT\\Internal_Audit_Report.pptx'
            else:
                use_case_2 = 'static\\media\\Test\\USE_CASE2\\Internal_Audit_Report.pptx'
            # use_case_2 = 'static\\media\\Test\\Orignal\\Use_Case2\\Internal_Audit_Report.pptx'
            # use_case_2 = 'static\\media\\Test\\USE_CASE2\\Internal_Audit_Report.pptx'

            try:
                # Get absolute file paths
                absolute_file_path = os.path.abspath(use_case_2)
                absolute_pdf_file_path = os.path.abspath(outputpath)
                
                # Convert PPTX to PDF
                convert_pptx_to_pdf(absolute_file_path, absolute_pdf_file_path+'\\'+'Internal_Audit_Report.pdf')

            except Exception as e:
                print(f"An error occurred: {e}")
            absolute_file_path = os.path.abspath(use_case_2)
            absolute_pdf_file_path = os.path.abspath(outputpath)
            print(f"Output_path >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{absolute_pdf_file_path}")

            if org_audit.progress != 100:
                with transaction.atomic():
                    org_audit.progress = 100
                    org_audit.audit_status = 'Committee Report Completed'
                    org_audit.out_putpath = final_outputpath + '/'+'Internal_Audit_Report.pdf'
                    org_audit.uploaded_at =datetime.datetime.now()
                    org_audit.save()
            else:
                pass
            time.sleep(90)
            audits = Audit.objects.filter(created_by = request.user,feature_request=feature,is_active=True).order_by('-id') 
            context = {
                'audits': audits,
                'current_document': current_document,#current_document.object_list[0].input_path,
                'data_list': data_list,
                'final_report': final_outputpath + '/'+'Internal_Audit_Report.pdf'
            }
            
        
            return render(request, 'usecase_two/horizonbody.html',context)
            # return redirect('HomeView')
        else:
            messages.success(request, ("You aren't authorized to view this page!"))
            # return redirect('HomeView')
            context ={
                'pdf_viewer':'sorted_outpath',

                'Regulator':audits.audit_status if audits.audit_status else None
            }
            return render(request, 'usecase_two/horizonbody.html',context)
