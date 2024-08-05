from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from django.utils import timezone

class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not phone:
            raise ValueError("The Phone number field must be set")
        
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, last_login=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(email, phone, password, **extra_fields)

def generate_uuid():
    return uuid.uuid4()

class User(AbstractBaseUser):
    full_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=15)
    dob = models.DateField(null=True,blank=True)
    email = models.EmailField(max_length=200, unique=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    uid = models.UUIDField(default=generate_uuid, editable=False, unique=True)
    is_student = models.BooleanField(default=False, null=True, blank=True)
    fcm_token = models.CharField(max_length=1000, blank=True, null=True)
    country_code = models.CharField(max_length=10, default='+91', blank=True, null=True)
    address = models.TextField(max_length=1000)
    EDU_OP = (('10','10'),
              ('plus_two','Plus Two'),
              ('ug','UG'),
              ('pg','PG'))
    education_level = models.CharField(max_length=200,choices=EDU_OP,null=True,blank=True)
    CAST_OP=(('sc_st','SE-ST'),
              ('obc','OBC'),
              ('genaral','Genaral')
            )
    cast =models.CharField(max_length=200,choices=CAST_OP,null=True,blank=True)
    DIS_OP=(('1','Yes'),
            ('0','No'),)
    disability =models.CharField(max_length=200,choices=DIS_OP,null=True,blank=True)
    gpa = models.CharField(max_length=255,null=True,blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} - {self.full_name}"
    
    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

class CentralGoverment(models.Model):
    image = models.ImageField(upload_to='images',null=True,blank=True)
    name =  models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    provider_id = models.CharField(max_length=255, unique=True,null=True,blank=True)
    password = models.CharField(max_length=255, null=True,blank=True)
    def __str__(self) -> str:
        return self.name

class StateGoverment(models.Model):
    central_gov = models.ForeignKey(CentralGoverment,on_delete=models.CASCADE,null=True)
    image = models.ImageField(upload_to='images',null=True,blank=True)
    name =  models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    provider_id = models.CharField(max_length=255, unique=True,null=True,blank=True)
    password = models.CharField(max_length=255, null=True,blank=True)

    def __str__(self) -> str:
        return self.name


class ScholarShipProvider(models.Model):
    state_gov = models.ForeignKey(StateGoverment,on_delete=models.CASCADE,null=True,blank=True)
    STATUS_CHOICES = (
        ('A', 'Approved'),
        ('P', 'Pending'),
        ('R', 'Rejected'),
    )
   
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    website = models.CharField(max_length=300,blank=True, null=True)
    contact_email = models.EmailField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    registration_number = models.CharField(max_length=255, unique=True)
    year_established = models.CharField(max_length=255)
    PROVIDER_CHOICES = (
        ('organization', 'Organization (club)'),
        ('institution', 'Institution (Collage/School)'),
    )
    provider_type = models.CharField(max_length=255,choices=PROVIDER_CHOICES)
    phone_number = models.PositiveIntegerField(null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    pin_code = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    remark = models.CharField(max_length=255,null=True,blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='P') 
    image = models.ImageField(upload_to='scolarship_provider',null=True,blank=True)
    provider_id = models.CharField(max_length=200,null=True,blank=True)
    password = models.CharField(max_length=200,null=True,blank=True)

    def get_central_applied_students(self):
        central_scholarships = ScholarShip.objects.filter(central__isnull=False)
        central_applications = ApplyScholarShip.objects.filter(scholarship__in=central_scholarships,valid_provider_obj=self,college_level='pending')
        return central_applications
    
    def get_state_applied_students(self):
        state_scholarships = ScholarShip.objects.filter(state__isnull=False)
        state_applications = ApplyScholarShip.objects.filter(scholarship__in=state_scholarships,valid_provider_obj=self,college_level='pending')
        return state_applications
    
 

    def __str__(self):
        return self.name 
    
class ScholarShip(models.Model):
    provider = models.ForeignKey(ScholarShipProvider, on_delete=models.CASCADE,null=True,blank=True)
    central = models.ForeignKey(CentralGoverment, on_delete=models.CASCADE,null=True,blank=True)
    state = models.ForeignKey(StateGoverment, on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    application_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    EDU_OP = (('10','10'),
              ('plus_two','Plus Two'),
              ('ug','UG'),
              ('pg','PG'))
    education_level = models.CharField(max_length=200,choices=EDU_OP,null=True,blank=True)
    CAST_OP=(('sc_st','SE-ST'),
              ('obc','OBC'),
              ('genaral','Genaral')
            )
    cast =models.CharField(max_length=200,choices=CAST_OP,null=True,blank=True)
    DIS_OP=(('1','Yes'),
            ('0','No'),)
    disability =models.CharField(max_length=200,choices=DIS_OP,null=True,blank=True)
    gpa = models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return f'{self.title} '

    
class ApplyScholarShip(models.Model):
    COM= (
         ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    scholarship = models.ForeignKey(ScholarShip, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    application_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    submission_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_documents = models.FileField(upload_to='scholarship_documents', null=True, blank=True)

    # Academic Information
    current_school = models.CharField(max_length=255)
    current_grade = models.CharField(max_length=50)  # This can be a drop-down menu in forms
    major_field_of_study = models.CharField(max_length=255)
   

    # Academic Achievements
    awards_honors = models.TextField(null=True, blank=True)
    relevant_courses_grades = models.TextField(null=True, blank=True)
    research_projects = models.TextField(null=True, blank=True)

    # Extracurricular Activities
    clubs_organizations = models.TextField(null=True, blank=True)
    volunteer_work = models.TextField(null=True, blank=True)
    leadership_roles = models.TextField(null=True, blank=True)
    sports_competitions = models.TextField(null=True, blank=True)

    # Financial Information
    family_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    number_of_dependents = models.IntegerField(null=True, blank=True)
    financial_hardship_description = models.TextField(null=True, blank=True)

    # Essay/Personal Statement
    personal_essay = models.TextField(null=True, blank=True)
    specific_questions = models.TextField(null=True, blank=True)

    # References
    references_contact_info = models.TextField(null=True, blank=True)
    letters_of_recommendation = models.FileField(upload_to='letters_of_recommendation', null=True, blank=True)

    # Documentation
    transcripts = models.FileField(upload_to='transcripts', null=True, blank=True)
    resume_cv = models.FileField(upload_to='resume_cv', null=True, blank=True)
    proof_of_enrollment = models.FileField(upload_to='proof_of_enrollment', null=True, blank=True)
    passport_photo = models.FileField(upload_to='passport_photos', null=True, blank=True)
    confirmed = models.BooleanField(default=False,null=True,blank=True)
    state_level = models.CharField(max_length=40,choices=COM, default='pending')
    central_level = models.CharField(max_length=40,choices=COM, default='pending')
    college_level = models.CharField(max_length=40,choices=COM, default='pending')
    valid_provider = models.PositiveIntegerField(null=True,blank=True)
    valid_provider_obj = models.ForeignKey(ScholarShipProvider,on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return f'{self.student.full_name} - {self.scholarship.title}'
    

# class ApprovedScholarShip(models.Model):
#     apply_scholarship = models.ForeignKey(ApplyScholarShip,on_delete=models.CASCADE)
#     conformed_date = mo


class Log(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null= True,blank=True)
    body = models.CharField(max_length=500,null=True,blank=True)
    is_viewed = models.BooleanField(default=False)


class Student(models.Model):
    provider = models.ForeignKey(ScholarShipProvider,on_delete=models.CASCADE)
    student_id = models.CharField(max_length=100)    