from django.shortcuts import render,redirect
from .form import UserForm,LoginForm,ScholarShipProviderForm,ProviderLoginForm,ApplyScholarShipForm,StudentIDForm
from rest_framework.response import Response
from .serializers import UserSerializer,ScholarShipProviderSerializer,ScholarShipSerializer,ApplyScholarShipSerializer,SApplyScholarShipSerializer,ApplyScholarShipStatusSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import User,ScholarShipProvider,ScholarShip,ApplyScholarShip,CentralGoverment,StateGoverment,Log,Student
import random
from django.core.mail import send_mail
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework import generics
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.timezone import now
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate,login,logout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

sender_email = f'Scholar Hub <{settings.EMAIL_HOST_USER}>'

def home(request):

    # Render the home page with unread_logs_count
    return render(request, 'home.html')

def pre_register_page(request):
    return render(request,'pre_reg.html')

class VerifyOTPView(View):
    template_name = 'otp.html'

    def get(self, request, pk, *args, **kwargs):
        # You can add any context data here if needed
        context = {
            'pk': pk
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        # Collect the OTP digits from the POST request
        num1 = request.POST.get('num1')
        num2 = request.POST.get('num2')
        num3 = request.POST.get('num3')
        num4 = request.POST.get('num4')
        num5 = request.POST.get('num5')
        num6 = request.POST.get('num6')

        # Combine them into a single OTP string
        otp = f"{num1}{num2}{num3}{num4}{num5}{num6}"

        try:
            user_obj = User.objects.get(id=pk)
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            return redirect('verify-otp', pk=pk)

        otp_expiry_time = user_obj.otp_created_at + timedelta(minutes=5)
        if timezone.now() > otp_expiry_time:
            messages.error(request, 'OTP expired')
            return redirect('verify-otp', pk=user_obj.id)

        # Verify the OTP
        if user_obj.otp == otp:
            user_obj.phone_verified = True
            user_obj.otp = None  # Clear OTP after successful verification
            user_obj.otp_created_at = None
            user_obj.save()
            login(request, user_obj)
   
            messages.success(request, 'Phone number verified successfully!')
            return redirect('home')

        messages.error(request, 'Invalid OTP. Please try again.')
        return redirect('verify-otp', pk=pk)

class SendOTPView(View):
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        form = UserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone']
            country_code = form.cleaned_data.get('country_code', None)
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['full_name']
            dob = form.cleaned_data.get('dob', None)
            gender = form.cleaned_data.get('gender', None)
            email = form.cleaned_data.get('email', None)
            address = form.cleaned_data.get('address', None)

            try:
                user = User.objects.get(phone=phone_number, is_deleted=False)
                messages.error(request,"Phone number is already registered ")
                return render(request, self.template_name, {
                    'form': form,
                    'message': 'Phone number is already registered.'
                })
            except User.DoesNotExist:
                current_otp = random.randint(100000, 999999)
                otp_created_at = timezone.now()

                user = User.objects.create(
                    phone=phone_number,
                    country_code=country_code,
                    otp=current_otp,
                    otp_created_at=otp_created_at,
                    full_name=full_name,
                    dob=dob,
                    gender=gender,
                    email=email,
                    address=address,
                    is_student = True
                )

                if email:
                    try:
                        send_mail(
                            'Your OTP Code',
                            f'Your Registration OTP code is {current_otp}',
                            sender_email,
                            [email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        messages.error(request,"f'Failed to send OTP email: {e}")
                        return render(request, self.template_name, {
                            'form': form,
                            'message': f'Failed to send OTP email: {e}'
                        })

                user.set_password(password)
                user.save()

                # Implement message_handler.send_otp(phone_number, current_otp) as needed
                messages.success(request," Student registerd Successfully")
                return redirect('verify',pk=user.id)
        return render(request, self.template_name, {'form': form})
    
class UserSendOTPView(View):
    template_name = 'user_reg.html'

    def get(self, request, *args, **kwargs):
        form = UserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone']
            country_code = form.cleaned_data.get('country_code', None)
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['full_name']
            dob = form.cleaned_data.get('dob', None)
            gender = form.cleaned_data.get('gender', None)
            email = form.cleaned_data.get('email', None)
            address = form.cleaned_data.get('address', None)

            try:
                user = User.objects.get(phone=phone_number, is_deleted=False)
                messages.error(request,'Phone number is already registered.')
                return render(request, self.template_name, {
                    'form': form
                })
            except User.DoesNotExist:
                current_otp = random.randint(100000, 999999)
                otp_created_at = timezone.now()

                user = User.objects.create(
                    phone=phone_number,
                    country_code=country_code,
                    otp=current_otp,
                    otp_created_at=otp_created_at,
                    full_name=full_name,
                    dob=dob,
                    gender=gender,
                    email=email,
                    address=address,
                    
                )

                if email:
                    try:
                        send_mail(
                            'Your OTP Code',
                            f'Your Registration OTP code is {current_otp}',
                            sender_email,
                            [email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        messages.error(request, f'Failed to send OTP email: {e}')
                        return render(request, self.template_name, {
                            'form': form,
                            'message': f'Failed to send OTP email: {e}'
                        })

                user.set_password(password)
                user.save()

                # Implement message_handler.send_otp(phone_number, current_otp) as needed
                messages.success(request," Student registerd Successfully")
                return redirect('verify',pk=user.id)
        return render(request, self.template_name, {'form': form})    

class LogoutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("home")

class LoginView(View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            pwd = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=pwd)  # `username` should be used for `authenticate`
            if user:
                if user.is_staff:
                    login(request, user)
                    return redirect('home')  # Replace with your staff dashboard URL
                else:
                    current_otp = random.randint(100000, 999999)
                    otp_created_at = timezone.now()
                    user.otp = current_otp
                    user.otp_created_at = otp_created_at
                    user.save()

                    # Send the OTP via email
                    try:
                        send_mail(
                            'Your OTP Code',
                            f'Your OTP code is {current_otp}',
                            sender_email,  # Replace with your sender email
                            [email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        messages.error(request, f'Failed to send OTP email: {e}')
                        return render(request, self.template_name, {"form": form})

                    return redirect("verify", pk=user.id)
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {"form": form})

class ProviderCreateView(View):
    template_name = 'provider_c.html'
    def get(self, request, *args, **kwargs):
        form = ScholarShipProviderForm
        return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
        form = ScholarShipProviderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Scholarship provider created successfully!')
            return redirect('home')  # Replace 'success_url' with your success page URL name
        else:
            messages.error(request, form.errors)
        return render(request, self.template_name, {'form': form})

def admin(request):
    if not request.user.is_staff:
        return redirect('login')  # Redirect non-staff users to login or some other appropriate view
    rq = ScholarShipProvider.objects.filter(status = 'P').order_by('-id')
    return render(request, 'admin_b.html', {"rq": rq})

def admin_request(request, pk, status):

    s = get_object_or_404(ScholarShipProvider, id=pk)

    if status not in ['A', 'R']:
        messages.error(request, "Invalid status value.")
        return redirect('adminp')

    s.status = status
    s.save()

    subject = 'Scholar Hub'
    if status == 'A':
        username = s.contact_email.split('@')[0]
        password = get_random_string(length=8)
        s.provider_id = username
        s.password = password
        s.save()
        
        message = f'Your Scholarship Provider Request is Approved. Your scholarship provider id is {username} and your password is {password}'
    else:
        message = 'Your Scholarship Provider Request is Rejected'

    try:
        send_mail(
            subject,
            message,
            sender_email,
            [s.contact_email],
            fail_silently=False,
        )
        messages.success(request, f'Status updated to {s.name} and email sent successfully.')
    except Exception as e:
        messages.error(request, f'Status updated but failed to send email: {e}')

    return redirect('adminp')

def scholar_ship_category(request):
    return render(request,'provider_category.html')

def central_gov(request):
    central_scholarships = ScholarShip.objects.filter(central__isnull=False)
    current_date = timezone.now().date()
    return render(request, 'cen_sch.html', {'scholarships': central_scholarships,'current_date': current_date})

def state_gov(request):
    state_scholarships = ScholarShip.objects.filter(state__isnull=False)
    current_date = timezone.now().date()
    return render(request, 'state_sch.html', {'scholarships': state_scholarships,'current_date': current_date})

def org_list(request):
    state_scholarships = ScholarShipProvider.objects.filter(provider_type='organization')
    
    return render(request, 'org_list.html', {'providers': state_scholarships})


def collage_list(request):
    scholarships = ScholarShipProvider.objects.filter(provider_type='institution')
    return render(request, 'clg_list.html', {'providers': scholarships})


class ProviderLoginView(View):
    template_name = 'pro_login.html'

    def get(self, request, *args, **kwargs):
        form = ProviderLoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = ProviderLoginForm(request.POST)
        if form.is_valid():
            provider_id = form.cleaned_data.get("provider_id")
            pwd = form.cleaned_data.get("password")

            try:
                sc = ScholarShipProvider.objects.get(provider_id=provider_id, password=pwd)
                if sc.provider_type == 'organization':
                    return render(request, 'org_panel.html')
                elif sc.provider_type == 'institution':
                    return render(request, 'ins_panel.html')
                else:
                    messages.error(request, "Invalid provider type.")
            except ScholarShipProvider.DoesNotExist:
                try:
                    cl = CentralGoverment.objects.get(lid=provider_id, password=pwd)
                    return render(request, 'cl_panel.html')
                except CentralGoverment.DoesNotExist:
                    try:
                        sl = StateGoverment.objects.get(lid=provider_id, password=pwd)
                        return render(request, 'sl_panel.html')
                    except StateGoverment.DoesNotExist:
                        messages.error(request, "Invalid provider ID or password.")
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {"form": form})


def list_scholarship(request, pk):
    pvdr = get_object_or_404(ScholarShipProvider, id=pk)
    scholarships = ScholarShip.objects.filter(provider=pvdr)
    current_date = timezone.now().date()
    return render(request, 'scholar_ship.html', {'scholarships': scholarships,'current_date': current_date})


@method_decorator(login_required(login_url='login'), name='dispatch')
class ApplyScholarShipView(View):
    def get(self, request, sclr_id):
        sclr_obj = get_object_or_404(ScholarShip, id=sclr_id)
        
        if sclr_obj.provider.provider_type == 'institution':
            return render(request, 'student_check.html', {'form': StudentIDForm(), 'scholarship': sclr_obj})

        form = ApplyScholarShipForm()
        return render(request, 'apply_scholarship.html', {'form': form, 'scholarship': sclr_obj})

    def post(self, request, sclr_id):
        sclr_obj = get_object_or_404(ScholarShip, id=sclr_id)
        
        if sclr_obj.provider.provider_type == 'institution':
            form = StudentIDForm(request.POST)
            if form.is_valid():
                student_id = form.cleaned_data['student_id']
                
                if self.is_valid_student(student_id, sclr_obj.provider):
                    return render(request, 'apply_scholarship.html', {'form': ApplyScholarShipForm(), 'scholarship': sclr_obj})
                else:
                    messages.error(request, 'Invalid student ID for this institution.')
                    return render(request, 'student_check.html', {'form': form, 'scholarship': sclr_obj})

        form = ApplyScholarShipForm(request.POST, request.FILES)
        if form.is_valid():
            if sclr_obj.end_date and now().date() > sclr_obj.end_date:
                messages.error(request, 'The application period for this scholarship has ended.')
                return render(request, 'apply_scholarship.html', {'form': form, 'scholarship': sclr_obj})

            if ApplyScholarShip.objects.filter(scholarship=sclr_obj, student=request.user).exists():
                messages.error(request, 'You have already applied for this scholarship.')
                return render(request, 'apply_scholarship.html', {'form': form, 'scholarship': sclr_obj})

            application = form.save(commit=False)
            application.scholarship = sclr_obj
            application.student = request.user
            application.save()

            if sclr_obj.start_date and sclr_obj.end_date:
                days_duration = (sclr_obj.end_date - sclr_obj.start_date).days
                duration_message = f'The scholarship duration is {days_duration} days.'
            else:
                duration_message = 'The scholarship duration is not specified.'

            send_mail(
                'Scholar Hub',
                f'Your {sclr_obj.title} Application Submitted Successfully. {duration_message}',
                sender_email,  # Replace with your actual sender email
                [request.user.email],
                fail_silently=False,
            )
            Log.objects.create(user=request.user, body=f"Scholarship {sclr_obj.title} application submitted successfully")
            messages.success(request, 'Scholarship application submitted successfully.')
            return redirect('home')

        messages.error(request, 'Failed to submit scholarship application. Please correct the errors below.')
        return render(request, 'apply_scholarship.html', {'form': form, 'scholarship': sclr_obj})

    def is_valid_student(self, student_id, provider):
        # Check if there is a student with the given ID and the specified provider
        return Student.objects.filter(student_id=student_id, provider=provider).exists()

def notify(request):
    # Get the logs for the current user and mark them as viewed
    logs = Log.objects.filter(user=request.user).order_by('-id')
    
    # Update logs to mark them as viewed
    logs.update(is_viewed=True)
    
    return render(request, 'notify.html', {'logs': logs})









@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_scholarship_provider(request):
    try:
        # Check if the logged-in user has a ScholarShipProvider
        provider = ScholarShipProvider.objects.get(user=request.user)
        return Response({'status': 1, 'message': 'User has a scholarship provider.',"value":True})
    except ScholarShipProvider.DoesNotExist:
        # If no provider is found
        return Response({'status': 1, 'message': 'User does not have a scholarship provider.',"value":False})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    try:
        user = request.user
        has_provider = ScholarShipProvider.objects.filter(user=user,status='approved').exists()
        
        response_data = {
            'status': True,
            'message': 'User has an associated scholarship provider' if has_provider else 'User does not have an associated scholarship provider',
            'has_scholarship_provider': has_provider,
            'user': UserSerializer(user).data
        }
        
        return Response(response_data)
    except Exception as e:
        return Response({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

class ScholarShipProviderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_obj = request.user
        data = request.data.copy()
        data['user'] = user_obj.id
        
        # Check if user already has a pending scholarship provider
        pending_provider = ScholarShipProvider.objects.filter(user=user_obj, status='pending').first()
        
        if pending_provider:
            return Response({
                'status': 0,
                'message': 'You already have a pending application'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ScholarShipProviderSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user_obj)
            send_mail(
                        'Scholar HUB provider Creation',
                        f'Your Scholarship provider request created successfully',
                        sender_email,
                        [user_obj.email],
                        fail_silently=False,
                    )
            return Response({
                'status': 1,
                'message': 'Scholarship provider created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 0,
            'message': 'Failed to create scholarship provider',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class UserScholarShipProviderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScholarShipProviderSerializer

    def get_object(self):
        user = self.request.user
        try:
            return ScholarShipProvider.objects.get(user=user)
        except ScholarShipProvider.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        scholarship_provider = self.get_object()
        if not scholarship_provider:
            return Response({
                'status': 0,
                'message': 'No scholarship provider found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(scholarship_provider)
        return Response({
            'status': 1,
            'message': 'Scholarship provider details retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)    
    
class ScholarShipCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, provider_id):
        data = request.data.copy()

        # Check if the provider exists
        try:
            provider = ScholarShipProvider.objects.get(id=provider_id)
        except ScholarShipProvider.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'Scholarship provider not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Add provider to the data
        data['provider'] = provider.id

        serializer = ScholarShipSerializer(data=data)
        if serializer.is_valid():
            serializer.save(provider=provider)
            return Response({
                'status': 1,
                'message': 'Scholarship created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 0,
            'message': 'Failed to create scholarship',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)    
    
class UserProvidedScholarShipListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the current user
        user = request.user
        # Get the scholarship provider for the current user
        try:
            provider = ScholarShipProvider.objects.get(user=user)
        except ScholarShipProvider.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'Scholarship provider not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all scholarships for the provider
        scholarships = ScholarShip.objects.filter(provider=provider)
        
        # Serialize the scholarships
        serializer = ScholarShipSerializer(scholarships, many=True)
        
        return Response({
            'status': 1,
            'message': 'Scholarships retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class ProviderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
    
        # Get all scholarships for the provider
        scholarshiprovider = ScholarShipProvider.objects.all()
        
        # Serialize the scholarships
        serializer = ScholarShipProviderSerializer(scholarshiprovider, many=True)
        
        return Response({
            'status': 1,
            'message': 'Scholarships retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class ScholarShipListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,provider_id):
 
        try:
            provider = ScholarShipProvider.objects.get(id=provider_id)
        except ScholarShipProvider.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'Scholarship provider not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all scholarships for the provider
        scholarships = ScholarShip.objects.filter(provider=provider)
        
        # Serialize the scholarships
        serializer = ScholarShipSerializer(scholarships, many=True)
        
        return Response({
            'status': 1,
            'message': 'Scholarships retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)



class ListAppliedScholarShipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,sclr_id):
        obj= ScholarShip.objects.get(id=sclr_id)
        applications = ApplyScholarShip.objects.filter(scholarship=obj)
        serializer = SApplyScholarShipSerializer(applications, many=True)
        return Response({
            'status': 1,
            'message': 'Applied scholarships retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)   
    
class ScholarShipDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, sclr_id):
        scholarship = get_object_or_404(ScholarShip, id=sclr_id)
        serializer = ScholarShipSerializer(scholarship)
        return Response({
            'status': 1,
            'message': 'Scholarship details retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

class ApplyScholarShipStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, app_id):
        # Retrieve the application
        application = get_object_or_404(ApplyScholarShip, id=app_id)
        
        # Serialize the data
        serializer = ApplyScholarShipStatusSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            updated_application = serializer.save()

            # Determine the status and send an email accordingly
            status_message = ''
            if updated_application.application_status == 'approved':
                status_message = 'Congratulations! Your scholarship application has been approved.'
            elif updated_application.application_status == 'rejected':
                status_message = 'We regret to inform you that your scholarship application has been rejected.'
            else:
                status_message = 'Your scholarship application is still pending.'

            send_mail(
                'Scholarship Application Status Update',
                status_message,
                sender_email, 
                [updated_application.student.email],
                fail_silently=False,
            )

            return Response({
                'status': 1,
                'message': 'Application status updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 0,
            'message': 'Failed to update application status',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class ApprovedScholarShipApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, sclr_id):
        additional_filter = request.data.get('content')
        
        # Retrieve the scholarship object or return 404
        sclr_obj = get_object_or_404(ScholarShip, id=sclr_id)
        
        # Filter approved applications for the given scholarship
        approved_applications = ApplyScholarShip.objects.filter(application_status='approved', scholarship=sclr_obj)
        
        # Serialize the approved applications
        serializer = SApplyScholarShipSerializer(approved_applications, many=True)
        
        # Send email to each student in the approved applications
        # Replace with your sender email
        for application in approved_applications:
            student_email = application.student.email
            if student_email:
                send_mail(
                    'Scholarship Exam Details',
                    additional_filter,
                    sender_email,
                    [student_email],
                    fail_silently=False,
                )
        
        return Response({
            'status': 1,
            'message': 'Approved scholarship applications retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class ConfirmedScholarShip(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, sclr_id,student_id):
        sclr_obj = get_object_or_404(ScholarShip, id=sclr_id)
        
        # Check if the student already has a confirmed scholarship
        student = User.objects.get(id=student_id)
        existing_confirmed = ApplyScholarShip.objects.filter(student=student, confirmed=True).exists()
        
        if existing_confirmed:
            return Response({
                'status': 0,
                'message': 'You already have a confirmed scholarship.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Filter the application
        application = ApplyScholarShip.objects.filter(student=student, scholarship=sclr_obj, application_status='approved').first()
        
        if application:
            application.confirmed = True
            application.save()
            
            # Define the email content
            subject = 'Congratulations...!'
            from_email = sender_email
            to_email = [application.student.email]
            text_content = 'Your scholarship application has been confirmed successfully.'
            
            # Render the HTML content from the template
            html_content = render_to_string('scholarship_confirmed_email.html', {
                'bank_name': 'Fedaral Bank',
                'bank_address_line1': 'Federal Bank Kakkanad seaport airport road ',
                'bank_address_line2': 'IFSC Code: FDRL0001469 and MICR Code:',
                'check_number': '123456 5663 677',
                'payee_name': application.student.full_name,
                'amount': application.scholarship.amount,  # Replace with the actual amount
                'date': now().date().strftime('%B %d, %Y'),
            })

            # Create the email
            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            return Response({
                'status': 1,
                'message': 'Scholarship confirmed successfully',
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 0,
            'message': 'No approved application found to confirm.',
        }, status=status.HTTP_400_BAD_REQUEST)
