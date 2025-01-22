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


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        # import pdb; pdb.set_trace()
        if user is not None:
            print("Inside login")
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            request.session['token'] = str(token)
            messages.success(request, 'Login successful.')
            return redirect('landing_page')  # Redirect to home page or another page
        else:
            print("invalid username")
            messages.error(request, 'Invalid username or password.')
            return render(request, 'usermanagement/login.html')
    return render(request, 'usermanagement/login.html')

# def logoutUser(request):
#     logout(request)
#     return redirect('login')
@login_required 
def logoutUser(request):
    if request.user.is_authenticated:
        print("inside auth")
        try:
            token = Token.objects.get(user=request.user)
            print('token deleted', token)
            token.delete()
        except Token.DoesNotExist:
            pass  # Token doesn't exist, nothing to delete
        messages.success(request, 'Logout successful.')
        logout(request)
        return redirect('login')
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=400)
    # Redirect to a desired page after logout (e.g., home page)
    return redirect('login')

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> TABLE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# def get_latest_audit_and_documents(request,feature):
#     try:
#         # Retrieve the latest active Audit object created by the current user
        
#         latest_audit = Audit.objects.filter(created_by=request.user,feature_request=feature,is_active=True).latest('created_at')
#         print(latest_audit)
#         # Retrieve all related Document objects for the latest Audit

#         documents = latest_audit.documents.all() 
#     except Audit.DoesNotExist:
#         # If no Audit object is found, set both to None
#         latest_audit = None
#         documents = None

#     # You can now return these objects, use them to render a template, or pass them to the context
#     return latest_audit, documents


def get_latest_audit_and_documents(request,feature):
    try:
        # Retrieve the latest active Audit object created by the current user
        print("feature in get latest audit docs=============================",feature)
        latest_audit = Audit.objects.filter(created_by=request.user,feature_request=feature,is_active=True).latest('created_at')
        print(latest_audit)
        # Retrieve all related Document objects for the latest Audit

        attached_folders = AttachedFolder.objects.filter(audit_id=latest_audit)
        
        # Extract the first related Document object (if any)
        if attached_folders.exists():
            first_attached_folder = attached_folders.first()
            is_audit = None
            is_issue = None
            meeting_type = first_attached_folder.meeting_type
            control_name = first_attached_folder.control_name
        else:
            is_audit = None
            is_issue = None
            first_attached_folder = None
            meeting_type = None
            control_name = None

        documents = latest_audit.documents.all() 
    except Audit.DoesNotExist:
        # If no Audit object is found, set both to None
        latest_audit = None
        documents = None
        is_audit = None
        is_issue = None
        first_attached_folder = None
        meeting_type = None
        control_name = None

    print("control name=============================",control_name)
    # You can now return these objects, use them to render a template, or pass them to the context
    return is_audit,is_issue,meeting_type,control_name,first_attached_folder,latest_audit, documents

import os
import pandas as pd
from django.http import Http404
from django.conf import settings


from django.template import Library

register = Library()

# Example of a custom filter
@register.filter(name='custom_filter')
@login_required
def index(request):
    feature = request.GET.get('feature', None) 
    print(f"Feature Requested : {feature}")
    sheet_names = None
    current_sheet = None
    
    audits = Audit.objects.filter(created_by = request.user,feature_request=feature,is_active=True).order_by('-id') 
    print("audits========",audits)
    for audit in audits:
        folders = AttachedFolder.objects.filter(audit_id=audit)
        print("folders========",folders)
        folder_list = []
        for folder in folders:
            folder_list.append({
                'id': folder.id,
                'folder_name': folder.folder_name,
                'is_vector_db_in_progress': folder.is_vector_db_in_progress,
                'is_issue': folder.is_issue,
                'is_audit': folder.is_audit,
                'meeting_type': folder.meeting_type,
                'control_name': folder.control_name,
            })


    # latest_audit, documents = get_latest_audit_and_documents(request,feature)
    isaudit,isissue,meeting_type,control_name,first_attached_folder,latest_audit, documents = get_latest_audit_and_documents(request,feature)
    # example = documents[0].input_path
    if documents:
        # Set up pagination for documents
        page = request.GET.get('page', 1)
        # feature = request.GET.get('feature', None)
        
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
        doc_id = current_document.object_list[0].id
        get_base_path = os.getcwd() + file_path
        absolute_file_path = os.path.abspath(get_base_path)

        if file_type in ['.xls', '.xlsx']:
            # import pdb; pdb.set_trace()
            latest_audit.current_docid = doc_id
            latest_audit.save()
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
  
    if feature == 'Audit Report Drafter':
        if 'HX-Request' in request.headers:
            # Render only the partial content for htmx request
            template_name = 'usecase_one/iframe.html'

        else:
            # Render the full page for a normal request
            current_document= None
            template_name = 'dashboard.html'

        context = {
            'audits': audits,
            'current_document': current_document,
            'data_list': data_list,
            'final_report': None,
            'get_audit_name':None,
            'current_sheet':current_sheet,
            'sheet':sheet_names if sheet_names else None,
        }

        return render(request, template_name, context)
    elif feature == 'Audit Committee Summary Report Drafter':
        try:
            print(f"File object of feature {feature}*********************** ",current_document.object_list[0].id)
        except:
            pass
        if 'HX-Request' in request.headers:
            # Render only the partial content for htmx request
            template_name = 'usecase_two/iframe.html'

        else:
            # Render the full page for a normal request
            current_document= None
            template_name = 'usecase_two/dashboard.html'

        context = {
            'audits': audits,
            'current_document': current_document,
            'data_list': data_list,
            'final_report': None,
            'get_audit_name':None,
        }

        return render(request, template_name, context)
    
    # Workpaper Automation Start

    elif feature == 'Workpaper Automation':
        print("inside Workpaper Automation if=========1==========")
        try:
            print(f"File object of feature {feature}*********************** ",current_document.object_list[0].id)
        except:
            pass
        if 'HX-Request' in request.headers:
            print("inside Workpaper Automation if========2===========")
            # Render only the partial content for htmx request
            template_name = 'usecase_workpaper/iframe.html'

        else:
            print("inside Workpaper Automation if=========3==========")
            # Render the full page for a normal request
            current_document= None
            template_name = 'usecase_workpaper/dashboard.html'

        context = {
            'audits': audits,
            'current_document': current_document,
            'data_list': data_list,
            'final_report': None,
            'get_audit_name':None,
        }
        print("inside Workpaper Automation if======4=============")

        return render(request, template_name, context)
    
    # Workpaper Automation End
    else:
        return redirect('landing_page')



def individualReport(request, pk):
    recent_user = request.user
    qs = Audit.objects.get(id=pk)
    folders = AttachedFolder.objects.filter(audit_id=pk)
    obj = Document.objects.filter(document_name = qs)
    print("folders========",folders)
    folder_list = []
    for folder in folders:
        folder_list.append({
            'id': folder.id,
            'folder_name': folder.folder_name,
            'is_vector_db_in_progress': folder.is_vector_db_in_progress,
            'is_issue': folder.is_issue,
            'is_audit': folder.is_audit,
            'meeting_type': folder.meeting_type,
            'control_name': folder.control_name,
        })


    
    
    # doc_list = []
    # for item in obj:
    #     doc_list.append({
    #         'id': item.id,
    #         'name': item.name,
    #         'file_type': item.file_type,
    #         'operation_status': item.operation_status,
    #         'input_path': item.input_path, # > /static/media/project_files/audit_check_files/shubham/Workpaper Automation/Test1s-2024/Control Walkthrough/CTL1/one_audit/AR8_cleaned.pdf
    #         'output_path': item.output_path,
    #         'uploaded_at': item.uploaded_at,
            
    #     })
    doc_list = []
    for item in obj:
        # Extract `meeting_type` and `control_name` from `input_path`
        input_path_parts = item.input_path.split('/')  # Split the input path by '/'
        if len(input_path_parts) >= 6:  # Ensure the path has enough parts
            meeting_type = input_path_parts[-3]  # Third from the last part
            control_name = input_path_parts[-2]  # Second from the last part
        else:
            meeting_type = None
            control_name = None

        # Append document details with extracted fields
        doc_list.append({
            'id': item.id,
            'name': item.name,
            'file_type': item.file_type,
            'operation_status': item.operation_status,
            'input_path': item.input_path,
            'output_path': item.output_path,
            'uploaded_at': item.uploaded_at,
            'meeting_type': meeting_type,
            'control_name': control_name,
        })
    
    print(f"  >>>> query one  >>>  {qs}")
    # obj = qs.document_name_set.all().value
    
    context = {
        'report': obj, 
        'audits': qs,
        # 'metting_type': folder.meeting_type,        
        'doc_list': doc_list, 
        'folder_list': folder_list, 

        
        }

    if request.headers.get('HX-Request'):
        return render(request, 'usecase_workpaper/report_level/individual_report.html', context)
    else:
        return render(request, 'usecase_workpaper/report_level/dashboard.html', context)  # Fallback for full page render