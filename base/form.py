from django import forms
from .models import User ,ScholarShipProvider,ScholarShip,ApplyScholarShip,Student

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name", "email", "phone", "address", "dob","password"
        ]
        widgets = {
        
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select dob', 'id': 'id_dob', 'type': 'date'}),
            'password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),

        }


class StudentRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name", "email", "phone", "address", "dob","password","education_level","cast","disability","gpa"
        ]
        widgets = {
        
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select dob', 'id': 'id_dob', 'type': 'date'}),
            'password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'education_level': forms.Select(choices=ScholarShip.EDU_OP, attrs={'class': 'form-control'}),
            'cast': forms.Select(choices=ScholarShip.CAST_OP, attrs={'class': 'form-control'}),
            'disability': forms.Select(choices=ScholarShip.DIS_OP, attrs={'class': 'form-control'}),
            'gpa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Gpa'}),

        }        



class StudentEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name", "email", "phone", "address", "dob","education_level","cast","disability","gpa"
        ]
        widgets = {
        
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select dob', 'id': 'id_dob', 'type': 'date'}),
            'education_level': forms.Select(choices=ScholarShip.EDU_OP, attrs={'class': 'form-control'}),
            'cast': forms.Select(choices=ScholarShip.CAST_OP, attrs={'class': 'form-control'}),
            'disability': forms.Select(choices=ScholarShip.DIS_OP, attrs={'class': 'form-control'}),
            'gpa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Gpa'}),

        }        




class LoginForm(forms.Form):
   email=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder': 'Enter email'}))
   password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control",'placeholder': 'Enter Password'}))  

class ProviderLoginForm(forms.Form):
   provider_id=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder': 'Enter id'}))
   password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control",'placeholder': 'Enter Password'}))  




class ScholarShipProviderForm(forms.ModelForm):
    class Meta:
        model = ScholarShipProvider
        fields = ["state_gov","name","description","website",
                  "contact_email","registration_number","year_established","provider_type","phone_number",
                  "address","pin_code","city","country","image"]
        widgets = {
            'state_gov': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'website': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter website'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter registration number'}),
            'year_established': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select year established', 'type': 'date'}),
            'provider_type': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pin code'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter country'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }  



class ApplyScholarShipForm(forms.ModelForm):
    valid_provider = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ApplyScholarShip
        fields = [
          
            'current_school', 'current_grade', 'major_field_of_study', 'awards_honors', 'relevant_courses_grades',
            'research_projects', 'clubs_organizations', 'volunteer_work', 'leadership_roles', 'sports_competitions',
            'family_income', 'number_of_dependents', 'financial_hardship_description', 'personal_essay', 'specific_questions',
            'references_contact_info', 'letters_of_recommendation', 'transcripts', 'resume_cv', 'proof_of_enrollment',
            'passport_photo','additional_documents','valid_provider'
        ]
                  
        widgets = {
            'current_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter current school'}),
            'current_grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter current grade'}),
            'major_field_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter major field of study'}),
            'awards_honors': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter awards and honors'}),
            'relevant_courses_grades': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter relevant courses and grades'}),
            'research_projects': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe research projects'}),
            'clubs_organizations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List clubs and organizations'}),
            'volunteer_work': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe volunteer work'}),
            'leadership_roles': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List leadership roles'}),
            'sports_competitions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe sports competitions'}),
            'family_income': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter family income'}),
            'number_of_dependents': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of dependents'}),
            'financial_hardship_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe financial hardship'}),
            'personal_essay': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your personal essay'}),
            'specific_questions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Answer specific questions'}),
            'references_contact_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Provide references contact info'}),
            'letters_of_recommendation': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload letters of recommendation'}),
            'transcripts': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload transcripts'}),
            'resume_cv': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload resume/CV'}),
            'proof_of_enrollment': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload proof of enrollment'}),
            'passport_photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload passport photo'}),
            'additional_documents': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload additional documents'}),
        }

class StudentIDForm(forms.Form):
    student_id = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder': 'Enter id'}))        
  



class ScholarShipForm(forms.ModelForm):
    class Meta:
        model = ScholarShip
        fields = ["title","description","amount","start_date","end_date","education_level","cast","disability","gpa"]
        widgets = {
            'education_level': forms.Select(choices=ScholarShip.EDU_OP, attrs={'class': 'form-control'}),
            'cast': forms.Select(choices=ScholarShip.CAST_OP, attrs={'class': 'form-control'}),
            'disability': forms.Select(choices=ScholarShip.DIS_OP, attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ScholarShipForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

class StudentsForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_id"]