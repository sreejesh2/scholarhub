
from rest_framework import serializers
from .models import User,ScholarShipProvider,ScholarShip,ApplyScholarShip


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone', 'dob', 'email', 'gender', 'phone_verified', 'otp', 'is_active', 'is_staff', 'is_deleted', 'uid', 'is_student', 'fcm_token', 'country_code','address','password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class ScholarShipProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarShipProvider
        fields = '__all__'        
        read_only_fields = ['user']

class ScholarShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarShip
        fields = '__all__'        

class ApplyScholarShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplyScholarShip
        fields = [
           'id', 'scholarship', 'student', 'application_status', 'submission_date', 'updated_at', 'additional_documents',
            'current_school', 'current_grade', 'major_field_of_study', 'awards_honors', 'relevant_courses_grades',
            'research_projects', 'clubs_organizations', 'volunteer_work', 'leadership_roles', 'sports_competitions',
            'family_income', 'number_of_dependents', 'financial_hardship_description', 'personal_essay', 'specific_questions',
            'references_contact_info', 'letters_of_recommendation', 'transcripts', 'resume_cv', 'proof_of_enrollment',
            'passport_photo'
        ]
        read_only_fields = ['application_status', 'submission_date', 'updated_at']        


class SApplyScholarShipSerializer(serializers.ModelSerializer):
    student= UserSerializer()
    class Meta:
        model = ApplyScholarShip
        fields = [
           'id', 'scholarship', 'student', 'application_status', 'submission_date', 'updated_at', 'additional_documents',
            'current_school', 'current_grade', 'major_field_of_study', 'awards_honors', 'relevant_courses_grades',
            'research_projects', 'clubs_organizations', 'volunteer_work', 'leadership_roles', 'sports_competitions',
            'family_income', 'number_of_dependents', 'financial_hardship_description', 'personal_essay', 'specific_questions',
            'references_contact_info', 'letters_of_recommendation', 'transcripts', 'resume_cv', 'proof_of_enrollment',
            'passport_photo'
        ]
        read_only_fields = ['application_status', 'submission_date', 'updated_at']        



class ApplyScholarShipStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplyScholarShip
        fields = ['application_status']