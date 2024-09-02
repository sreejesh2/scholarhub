from django.shortcuts import render,redirect
from .form import UserForm,LoginForm,ScholarShipProviderForm,ProviderLoginForm,ApplyScholarShipForm,StudentIDForm,ScholarShipForm,StudentsForm,StudentRegisterForm,StudentEditForm
from rest_framework.response import Response
from .serializers import UserSerializer,ScholarShipProviderSerializer,ScholarShipSerializer,ApplyScholarShipSerializer,SApplyScholarShipSerializer,ApplyScholarShipStatusSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import User,ScholarShipProvider,ScholarShip,ApplyScholarShip,CentralGoverment,StateGoverment,Log,Student
from django.db.models import Q
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
import razorpay
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
from decimal import Decimal
from scholarhub import settings


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
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
        form = StudentRegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone']
            country_code = form.cleaned_data.get('country_code', None)
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['full_name']
            dob = form.cleaned_data.get('dob', None)
            gender = form.cleaned_data.get('gender', None)
            email = form.cleaned_data.get('email', None)
            address = form.cleaned_data.get('address', None)
            education_level = form.cleaned_data.get('education_level', None)
            cast = form.cleaned_data.get('cast', None)
            disability = form.cleaned_data.get('disability', None)
            cgpa = form.cleaned_data.get('cgpa', None)

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
                    is_student = True,
                    education_level = education_level,
                    cast =cast,
                    disability=disability,
                    cgpa=cgpa

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


def generate_otp():
    return random.randint(100000, 999999)

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            # Store the OTP in the user's profile or a temporary session
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            # Send OTP via email
            send_mail(
                'Your OTP for Password Reset',
                f'Your OTP is {otp}. Please enter this to reset your password.',
                sender_email,  # Replace with your email
                [email],
                fail_silently=False,
            )
            # Redirect to OTP verification page
           
            return redirect('verify_otpf' , pk= user.id)
        except User.DoesNotExist:
            messages.error(request, 'No user is associated with this email address.')
            return redirect('login')

    return render(request, 'login.html')


def provider_password_reset(request):
    if request.method == "POST":
        provider_id = request.POST.get('provider_id')
        if not provider_id:
            messages.error(request, "Provider ID is required.")
            return redirect('provider-login')  # Redirect to the login page if no provider ID is entered

        # Initialize provider as None
        provider = None

        # Check in ScholarshipProvider first
        try:
            provider = ScholarShipProvider.objects.get(provider_id=provider_id)
        except ScholarShipProvider.DoesNotExist:
            pass

        # If not found, check in Central Government
        if not provider:
            try:
                provider = CentralGoverment.objects.get(provider_id=provider_id)
            except CentralGoverment.DoesNotExist:
                pass

        # If not found, check in State Government
        if not provider:
            try:
                provider = StateGoverment.objects.get(provider_id=provider_id)
            except StateGoverment.DoesNotExist:
                provider = None

        if provider:
            return redirect('reset_pass_pro' ,provider_id=provider_id )  # Redirect to the desired view

        else:
            messages.error(request, "Invalid provider ID.")
            return redirect('pro_l')

    return render(request, 'login.html')


def provider_reset(request, provider_id):
    if request.method == "POST":
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 == pass2:
            # Initialize the provider object
            provider = None

            # Check in ScholarshipProvider first
            try:
                provider = ScholarShipProvider.objects.get(provider_id=provider_id)
            except ScholarShipProvider.DoesNotExist:
                pass

            # If not found, check in Central Government
            if not provider:
                try:
                    provider = CentralGoverment.objects.get(provider_id=provider_id)
                except CentralGoverment.DoesNotExist:
                    pass

            # If not found, check in State Government
            if not provider:
                try:
                    provider = StateGoverment.objects.get(provider_id=provider_id)
                except StateGoverment.DoesNotExist:
                    provider = None

            if provider:
                # Update the password for the identified provider
                provider.password = pass1  # Consider hashing the password if it's plain text
                provider.save()

                messages.success(request, "Password updated successfully.")
                return redirect('pro_l')
            else:
                messages.error(request, "Invalid provider ID.")
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, 'reset_pass.html')


class VerifyOTPViewFor(View):
    template_name = 'otpf.html'

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
            return redirect('verify-otpf', pk=pk)

        otp_expiry_time = user_obj.otp_created_at + timedelta(minutes=5)
        if timezone.now() > otp_expiry_time:
            messages.error(request, 'OTP expired')
            return redirect('verify-otpf', pk=pk)

        # Verify the OTP
        if user_obj.otp == otp:
            user_obj.phone_verified = True
            user_obj.otp = None  # Clear OTP after successful verification
            user_obj.otp_created_at = None
            user_obj.save()
            
   
            messages.success(request, 'otp verified successfully!')
            return redirect('f-page' ,pk=pk)

        messages.error(request, 'Invalid OTP. Please try again.')
        return redirect('verify-otpf', pk=pk)

def fpage(request,pk):
    if request.method == "POST":
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
        # Example: Check if passwords match
        if pass1 == pass2:
            # Handle the logic when passwords match
            # For example, update the user's password
            user = User.objects.get(id=pk)
            user.set_password(pass1)
            user.save()
            
            messages.success(request, "Password updated successfully.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, 'f-page.html')


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
                request.session['provider_id'] = sc.provider_id  # Storing the provider's ID in the session
                if sc.provider_type == 'organization':
                    
                    return redirect('ad_sc')
                elif sc.provider_type == 'institution':
                    
                    return redirect('ad_sc')
                else:
                    messages.error(request, "Invalid provider type.")
            except ScholarShipProvider.DoesNotExist:
                try:
                    cl = CentralGoverment.objects.get(provider_id=provider_id, password=pwd)
                    request.session['provider_id'] = cl.provider_id
                    
                    return redirect('ad_sc')
                except CentralGoverment.DoesNotExist:
                    try:
                        sl = StateGoverment.objects.get(provider_id=provider_id, password=pwd)
                        request.session['provider_id'] = sl.provider_id  # Storing the state government's ID in the session
                        
                        return redirect('ad_sc')
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
        provider_is_institution = sclr_obj.provider and sclr_obj.provider.provider_type == 'institution'
        central_is_institution = sclr_obj.central 
        state_is_institution = sclr_obj.state 
        
        if provider_is_institution or central_is_institution or state_is_institution:
            return render(request, 'student_check.html', {'form': StudentIDForm(), 'scholarship': sclr_obj})
        
        form = ApplyScholarShipForm()
        return render(request, 'apply_scholarship.html', {'form': form, 'scholarship': sclr_obj})  

    def post(self, request, sclr_id):
        sclr_obj = get_object_or_404(ScholarShip, id=sclr_id)
        provider_is_institution = sclr_obj.provider and sclr_obj.provider.provider_type == 'institution'
        central_is_institution = sclr_obj.central 
        state_is_institution = sclr_obj.state 

        valid_provider = None  # Initialize the variable

        if central_is_institution or state_is_institution or provider_is_institution:
            form = StudentIDForm(request.POST)
            if form.is_valid():
                student_id = form.cleaned_data['student_id']
                valid_provider = self.get_valid_provider(student_id)

                if valid_provider:
                   
                   
                    application_form = ApplyScholarShipForm(initial={'valid_provider': valid_provider.id})
                    return render(request, 'apply_scholarship.html', {'form': application_form, 'scholarship': sclr_obj, 'valid_provider': valid_provider})
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
            valid_provider_id = form.cleaned_data.get('valid_provider')
            valid_provider_instance = ScholarShipProvider.objects.get(id=valid_provider_id) if valid_provider_id else None
            
            application = form.save(commit=False)
            application.scholarship = sclr_obj
            application.student = request.user
            if central_is_institution or state_is_institution:
                application.valid_provider_obj = valid_provider_instance

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

    def get_valid_provider(self, student_id):
        # Check if there is a student with the given ID and return the provider if valid
        student = Student.objects.filter(student_id=student_id).first()
        if student:
            return student.provider
        return None


def notify(request):
    # Get the logs for the current user and mark them as viewed
    logs = Log.objects.filter(user=request.user).order_by('-id')
    
    # Update logs to mark them as viewed
    logs.update(is_viewed=True)
    
    return render(request, 'notify.html', {'logs': logs})


def recommendation(request):
    if request.user.is_authenticated:
        scholarships = ScholarShip.objects.all()
        current_date = timezone.now().date()

        if request.user.is_student:
            # Create a list of Q objects for filtering
            filters = Q()
            exact_match = True

            if request.user.education_level:
                filters &= Q(education_level=request.user.education_level)
            else:
                exact_match = False

            if request.user.cast:
                filters &= Q(cast=request.user.cast)
            else:
                exact_match = False

            if request.user.disability:
                filters &= Q(disability=request.user.disability)
            else:
                exact_match = False

            if request.user.cgpa:
                filters &= Q(cgpa__lte=request.user.cgpa)
            else:
                exact_match = False

            # Apply filters only if exact match is required
            if exact_match:
                scholarships = scholarships.exclude(provider__provider_type='institution').filter(filters)
            else:
                scholarships = scholarships.none()  # No exact match found

        return render(request, 'recommendations.html', {'scholarships': scholarships, 'current_date': current_date})
    else:
        return render(request, 'login.html')



@login_required(login_url='login')
def profile(request):
    user_obj = User.objects.get(id=request.user.id)
    
    # Check if the user is a student
    if user_obj.is_student:
        # Render the template with all details if the user is a student
        return render(request, 'profile.html', {'profile': user_obj, 'detailed': True})
    else:
        # Render the template with basic details if the user is not a student
        return render(request, 'profile.html', {'profile': user_obj, 'detailed': False})

def admin_scholarship(request):
    provider_id = request.session.get('provider_id')  # Get provider ID from session

    if not provider_id:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')  # Redirect to login page or show an error message

    try:
        provider = ScholarShipProvider.objects.get(provider_id=provider_id)
        scholarships = ScholarShip.objects.filter(provider=provider)
        if provider.provider_type == 'organization':
            return render(request, 'org_panel.html', {'scholarships': scholarships, 'provider': provider})
        elif provider.provider_type == 'institution':
            return render(request, 'ins_panel.html', {'scholarships': scholarships, 'provider': provider})
    except ScholarShipProvider.DoesNotExist:
        try:
            provider = CentralGoverment.objects.get(provider_id=provider_id)
            scholarships = ScholarShip.objects.filter(central=provider)
            return render(request, 'cl_panel.html', {'scholarships': scholarships, 'provider': provider})
        except CentralGoverment.DoesNotExist:
            try:
                provider = StateGoverment.objects.get(provider_id=provider_id)
                scholarships = ScholarShip.objects.filter(state=provider)
                return render(request, 'sl_panel.html', {'scholarships': scholarships, 'provider': provider})
            except StateGoverment.DoesNotExist:
                messages.error(request, "Invalid provider ID.")
                return redirect('login')

    messages.error(request, "Invalid provider ID.")
    return redirect('login')


class ScholarShipCreateView(View):
    template_name = 'scholarship_c.html'
    
    def get(self, request, *args, **kwargs):
        form = ScholarShipForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ScholarShipForm(request.POST, request.FILES)
        if form.is_valid():
            scholarship = form.save(commit=False)
            
            # Retrieve provider_id from session
            provider_id = request.session.get('provider_id')

            if provider_id:
                # Check if provider_id matches a provider, central, or state
                try:
                    provider = ScholarShipProvider.objects.get(provider_id=provider_id)
                    scholarship.provider = provider
                except ScholarShipProvider.DoesNotExist:
                    try:
                        central = CentralGoverment.objects.get(provider_id=provider_id)
                        scholarship.central = central
                    except CentralGoverment.DoesNotExist:
                        try:
                            state = StateGoverment.objects.get(provider_id=provider_id)
                            scholarship.state = state
                        except StateGoverment.DoesNotExist:
                            messages.error(request, 'Invalid provider ID')
                            return render(request, self.template_name, {'form': form})

            scholarship.save()
            messages.success(request, 'Scholarship provider created successfully!')
            return redirect('ad_sc')  # Replace 'home' with your success page URL name
        else:
            messages.error(request, form.errors)
        
        return render(request, self.template_name, {'form': form})


class AppliedScholarships(View):
    template_name = 'apply_sch.html'
    
    def get(self, request, sch_id, *args, **kwargs):
        sch_obj = get_object_or_404(ScholarShip, id=sch_id)
        applied_scholarships = ApplyScholarShip.objects.filter(scholarship=sch_obj)
        is_institution = (sch_obj.provider and sch_obj.provider.provider_type == 'institution') or False
        return render(request, self.template_name, {
            "apply_sch": applied_scholarships,
            "scholarship": sch_obj,
            "is_institution": is_institution,
        })


def admin_change_status(request, pk, status):
    # Retrieve the ApplyScholarShip object
    aled_sh = get_object_or_404(ApplyScholarShip, id=pk)

    # Update the application status
    aled_sh.application_status = status
    aled_sh.save()


    # Log the status change
    Log.objects.create(user=aled_sh.student, body=f"Your {aled_sh.scholarship.title} scholarship application is now {status}")

    # Send an email notification
    send_mail(
        'Scholar Hub',
        f'Your {aled_sh.scholarship.title} scholarship application is now {status}',
        sender_email,  # Use the sender email configured in settings
        [aled_sh.student.email],  # Send to the email of the student who applied
        fail_silently=False,
    )

    # Notify the user of the status change and redirect
    messages.success(request, f"The scholarship application status has been updated to {status}.")
    return redirect('applied_sdnts', sch_id = aled_sh.scholarship.id ) 

class ApprovedScholarships(View):
    template_name = 'approved_sch.html'
    
    def get(self, request, sch_id, *args, **kwargs):
        sch_obj = get_object_or_404(ScholarShip, id=sch_id)
        applied_scholarships = ApplyScholarShip.objects.filter(scholarship=sch_obj,status='approved')
        return render(request, self.template_name, {
            "approved_sch": applied_scholarships,
            "scholarship": sch_obj,
        })

class Students(View):
    template_name = 'students.html'
    
    def get(self, request, *args, **kwargs):
        form = StudentsForm()
        provider_id = request.session.get('provider_id')
        if provider_id is None:
        # Handle the case where the provider_id is not in the session
        # For example, you might redirect to a login page or show an error message
          return redirect('login')  # Adjust this to your login URL or error handling

        # Fetch the students associated with this provider
        students_list = Student.objects.filter(provider__provider_id=provider_id)
        return render(request, 'students.html', {'students': students_list,"form":form})
    def post(self, request, *args, **kwargs):
        form = StudentsForm(request.POST)
        provider_id = request.session.get('provider_id')
        
        if form.is_valid() and provider_id:
            student = form.save(commit=False)
            provider = ScholarShipProvider.objects.get(provider_id=provider_id)
            student.provider = provider
            student.save()
            return redirect('students_list')  # Adjust this to the appropriate URL name

        # If the form is not valid, re-render the page with the form and errors
        students_list = Student.objects.filter(provider__provider_id=provider_id)
        return render(request, self.template_name, {'students': students_list, 'form': form})
       
# def central_gov_applied(request):
#     provider_id = request.session.get('provider_id')  # Get provider ID from session

#     if not provider_id:
#         messages.error(request, "Session expired. Please log in again.")
#         return redirect('login')  # Redirect to login page or show an error message



def central_applied_students_view(request):
    provider_id = request.session.get('provider_id') 
    if not provider_id:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login') 
    provider = get_object_or_404(ScholarShipProvider, provider_id=provider_id)
    central_applications = provider.get_central_applied_students()
    return render(request, 'central_gov_applied.html', {'applications': central_applications})



def state_applied_students_view(request):
    provider_id = request.session.get('provider_id') 
    if not provider_id:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login') 
    provider = get_object_or_404(ScholarShipProvider, provider_id=provider_id)
    central_applications = provider.get_state_applied_students()
    return render(request, 'state_gov_applied.html', {'applications': central_applications})


class ApprovedCollegeLevel(View):
    template_name = 'central_gov_applied.html'
    
    def get(self, request, a_id, status, *args, **kwargs):
        # Retrieve the ApplyScholarShip object or return a 404 if not found
        a_obj = get_object_or_404(ApplyScholarShip, id=a_id)
        
        # Update the college_level field
        a_obj.college_level = status
        a_obj.save()

        # Send email notification
        send_mail(
            'Scholar Hub - Status Update',
            f'Your scholarship application with ID {a_obj} has been updated to {status}.',
            sender_email,  # Replace with your actual sender email
            [a_obj.student.email],
            fail_silently=False,
        )
        Log.objects.create(user=a_obj.student,body= f'Your scholarship application with ID {a_obj} has been updated to {status}.',)
        
        # Redirect to the specified URL
        return redirect('cas')  


class ApprovedStateCollegeLevel(View):
    template_name = 'state_gov_applied.html'
    
    def get(self, request, a_id,status, *args, **kwargs):
        a_obj = get_object_or_404(ApplyScholarShip, id=a_id)
        a_obj.college_level = status
        a_obj.save()
        send_mail(
            'Scholar Hub - Status Update',
            f'Your scholarship application with ID {a_obj} has been updated to {status}.',
            sender_email,  # Replace with your actual sender email
            [a_obj.student.email],
            fail_silently=False,
        )
        Log.objects.create(user=a_obj.student,body= f'Your scholarship application with ID {a_obj} has been updated to {status}.',)
        
        return redirect('sas')    


def collage_approved_students_central(request):
    provider_id = request.session.get('provider_id') 
    if not provider_id:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login') 

    applied_students= ApplyScholarShip.objects.filter(college_level='approved',scholarship__central__isnull=False,state_level= 'pending')
    return render(request, 'collage_approved_students.html', {'applications': applied_students})


class ApprovedStateLevel(View):
    template_name = 'collage_approved_students.html'
    
    def get(self, request, a_id,status, *args, **kwargs):
        a_obj = get_object_or_404(ApplyScholarShip, id=a_id)
        a_obj.state_level = status
        a_obj.save()
        send_mail(
            'Scholar Hub - Status Update',
            f'Your scholarship application with ID {a_obj} has been updated by State Gov to {status}.',
            sender_email,  # Replace with your actual sender email
            [a_obj.student.email],
            fail_silently=False,
        )
        Log.objects.create(user=a_obj.student,body= f'Your scholarship application with ID {a_obj} has been updated by State Gov to {status}.',)
        return redirect('central_coll_ap') 


def create_exam(request, s_id):
    sch_obj = get_object_or_404(ScholarShip, id=s_id)
    
    if request.method == 'POST':
        # Get exam details from the form
        exam_date = request.POST['exam_date']
        exam_time = request.POST['exam_time']
        exam_venue = request.POST['exam_venue']
        
        # Get the approved applications
        apply_objs = ApplyScholarShip.objects.filter(scholarship=sch_obj, application_status='approved')
        
        # Send email to each approved applicant
        for a in apply_objs:
            send_mail(
                'Exam Details',
                f'Dear {a.student.full_name},\n\n'
                f'Your exam is scheduled as follows:\n'
                f'Date: {exam_date}\n'
                f'Time: {exam_time}\n'
                f'Venue: {exam_venue}\n\n'
                f'Good luck!\n'
                f'Scholar Hub Team',
                sender_email,  # Replace with your actual sender email
                [a.student.email],  # Assuming 'applicant_email' is a field in the ApplyScholarShip model
                fail_silently=False,
            )
        
        # Redirect to a success page or the scholarship details page
        return redirect('ad_sc')  # Make sure 'scholarship_detail' is a valid URL name

    # If GET request, render the form template
    return render(request, 'create_exam.html', {'sch_obj': sch_obj})


class ProcessPaymentView(View):
    def get(self, request, a_id, *args, **kwargs):
        allpy = get_object_or_404(ApplyScholarShip, id=a_id)
        amount = allpy.scholarship.amount.quantize(Decimal('1.00')) * 100  # Convert to paise and ensure no floating point issues

        # Convert amount to an integer (paise)
        amount_in_paise = int(amount)

        # Create Razorpay order
        order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Save the order ID to the donation object
        allpy.order_id = order['id']
        allpy.save()

        return render(request, "payment.html", {
            'order_id': order['id'],
            'amount': amount_in_paise,
            'api_key': 'rzp_test_91eopcxhCbCO8V',
            "scholarship": allpy
        })

def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    signature = request.GET.get('signature')
    scholarship_id = request.GET.get('scholarship_id')
    
    # Retrieve the ApplyScholarShip object and update its status
    allpy = get_object_or_404(ApplyScholarShip, id = scholarship_id)
    allpy.is_paid = True
    allpy.payment_status = 'paid'
    allpy.save()
    
    return render(request, 'payment_success.html', {
        'payment_id': payment_id,
        'order_id': order_id,
        'signature': signature,
    })

def payment_failure(request):
    code = request.GET.get('code')
    description = request.GET.get('description')
    return render(request, 'payment_failure.html', {'code': code, 'description': description})


def state_approved_students_central(request,s_id):
    provider_id = request.session.get('provider_id') 
    if not provider_id:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login') 
    s_obj=ScholarShip.objects.get(id=s_id)
    applied_students= ApplyScholarShip.objects.filter(state_level='approved',scholarship__central__isnull=False,central_level= 'pending',scholarship=s_obj)
    return render(request, 'state_approved_students.html', {'applications': applied_students})

@login_required
def user_edit(request):
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = StudentEditForm(instance=request.user)
    
    return render(request, 'user_edit.html', {'form': form})


def admin_rejected(request):
    if not request.user.is_staff:
        return redirect('login')  # Redirect non-staff users to login or some other appropriate view
    rq = ScholarShipProvider.objects.filter(status = 'R').order_by('-id')
    return render(request, 'admin_r.html', {"rq": rq})



def admin_approved(request):
    if not request.user.is_staff:
        return redirect('login')  # Redirect non-staff users to login or some other appropriate view
    rq = ScholarShipProvider.objects.filter(status = 'A').order_by('-id')
    return render(request, 'admin_a.html', {"rq": rq})








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
    
# class ScholarShipCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, provider_id):
#         data = request.data.copy()

#         # Check if the provider exists
#         try:
#             provider = ScholarShipProvider.objects.get(id=provider_id)
#         except ScholarShipProvider.DoesNotExist:
#             return Response({
#                 'status': 0,
#                 'message': 'Scholarship provider not found'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         # Add provider to the data
#         data['provider'] = provider.id

#         serializer = ScholarShipSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save(provider=provider)
#             return Response({
#                 'status': 1,
#                 'message': 'Scholarship created successfully',
#                 'data': serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             'status': 0,
#             'message': 'Failed to create scholarship',
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)    
    
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



