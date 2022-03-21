from django.urls import include, path
from rest_framework import routers

from rnames_app.api import views

router = routers.DefaultRouter()
router.register(r'locations', views.LocationViewSet)
router.register(r'names', views.NameViewSet)
router.register(r'qualifiers', views.QualifierViewSet)
router.register(r'stratigraphic-qualifiers', views.StratigraphicQualifierViewSet)
router.register(r'qualifier-names', views.QualifierNameViewSet)
router.register(r'structured-names', views.StructuredNameViewSet)
router.register(r'references', views.ReferenceViewSet)
router.register(r'relations', views.RelationViewSet)
router.register(r'time-slices', views.TimeSliceViewSet)
router.register(r'binnings', views.BinningViewSet)

urlpatterns = [
	path('', include(router.urls)),
]
