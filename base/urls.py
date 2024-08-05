from . import views
from django.urls import path

urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.SendOTPView.as_view(),name='reg'),
    path('user_reg/',views.UserSendOTPView.as_view(),name='user_reg'),
    path('verify/otp/<int:pk>/',views.VerifyOTPView.as_view(),name='verify'),
    path('student/',views.pre_register_page,name='pre_reg'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('provider/create/',views.ProviderCreateView.as_view(),name='provider_c'),
    path('adminp/',views.admin,name='adminp'),
    path('request/send/<int:pk>/<str:status>/',views.admin_request,name='admin_request'),
    path('scholarship/categorys/',views.scholar_ship_category,name='cat_sc'),
    path('cental/scholarships/',views.central_gov,name='cent_sch'),
    path('state/scholarships/',views.state_gov,name='state_sch'),
    path('provider/login/',views.ProviderLoginView.as_view(),name='pro_l'),
    path('organizations/', views.org_list, name='org_list'),
    path('institutions/', views.collage_list, name='collage_list'),
    path('scholarship/list/<int:pk>/',views.list_scholarship,name='sch_list'),
    path('notify/',views.notify,name='notify'),
    path('recommentation/',views.recommendation,name='recom'),
    path('profile/',views.profile,name='profile'),
    path('ad/scholarships/',views.admin_scholarship,name= 'ad_sc'),
    path('create/html/scholarship/',views.ScholarShipCreateView.as_view(),name='create_sch'),
    path('ad/applied/scholarship/<int:sch_id>/',views.AppliedScholarships.as_view(),name='applied_sdnts'),
    path('change/application_status/<int:pk>/<str:status>/',views.admin_change_status,name='change_status_ad'),
    path('students/list/',views.Students.as_view(),name='students_list'),
    path('central/appied/scholarship/',views.central_applied_students_view,name='cas'),
    path('state/appied/scholarship/',views.state_applied_students_view,name='sas'),
    path('status/change/college/<int:a_id>/<str:status>/',views.ApprovedCollegeLevel.as_view(),name='st_c'),
    path('status/change/college/state/<int:a_id>/<str:status>/',views.ApprovedStateCollegeLevel.as_view(),name='st_s'),
    path('collage/approved/students/state/',views.collage_approved_students_central,name='central_coll_ap'),
    path('state/approv/<int:a_id>/<str:status>/',views.ApprovedStateLevel.as_view(),name='state_approve'),



    path('api/check-scholarship-provider/', views.check_scholarship_provider, name='check_scholarship_provider'),
    path('user/profile/', views.user_profile_view, name='user-profile'),
    path('scholarship-provider/create/', views.ScholarShipProviderCreateView.as_view(), name='scholarship-provider-create'),
    path('scholarship-provider/detail/', views.UserScholarShipProviderDetailView.as_view(), name='scholarship-provider-detail'),
    # path('scholarship/create/<int:provider_id>/', views.ScholarShipCreateView.as_view(), name='scholarship-create'),
    path('scholarship/my-provided-scholarships/', views.UserProvidedScholarShipListView.as_view(), name='user-provided-scholarship-list'),
    path('providers/', views.ProviderListView.as_view(), name='provider-list'),
    path('scholarship/list/<int:provider_id>/',views.ScholarShipListView.as_view(),name='list-scholarship'),
    path('apply-scholarship/<int:sclr_id>/', views.ApplyScholarShipView.as_view(), name='apply-scholarship'),
    path('applied-scholarships/<int:sclr_id>/', views.ListAppliedScholarShipsView.as_view(), name='applied-scholarships'),
    path('scholarship-detail/<int:sclr_id>/', views.ScholarShipDetailView.as_view(), name='scholarship-detail'),
    path('update-application-status/<int:app_id>/', views.ApplyScholarShipStatusUpdateView.as_view(), name='update-application-status'),
    path('exam/<int:sclr_id>/',views.ApprovedScholarShipApplicationsView.as_view(),name='exam'),
    path('scholarship/confirm/<int:sclr_id>/<int:student_id>/',views.ConfirmedScholarShip.as_view(),name='cm')

]
     
