from django.urls import include, path
from rest_framework import routers

from rnames_api import views

router = routers.DefaultRouter()
router.register(r'locations', views.LocationViewSet, basename='api-location')
router.register(r'names', views.NameViewSet, basename='api-name')
router.register(r'qualifiers', views.QualifierViewSet, basename='api-qualifier')
router.register(r'stratigraphic-qualifiers', views.StratigraphicQualifierViewSet, basename='api-stratigraphic-qualifier')
router.register(r'qualifier-names', views.QualifierNameViewSet, basename='api-qualifier-name')
router.register(r'structured-names', views.StructuredNameViewSet, basename='api-structured-name')
router.register(r'references', views.ReferenceViewSet, basename='api-reference')
router.register(r'relations', views.RelationViewSet, basename='api-relation')
router.register(r'binnings', views.BinningViewSet, basename='api-binning')
router.register(r'absolute-age-values', views.AbsoluteAgeValueViewSet, basename='api-absolute-age-value')
router.register(r'time-scales', views.TimeScaleViewSet, basename='api-time-scale')
router.register(r'time-scale-names', views.BinningSchemeNameSerializer, basename='api-time-scale-name')

urlpatterns = [
	path('', include(router.urls)),
]
