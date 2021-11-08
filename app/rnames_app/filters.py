# https://django-filter.readthedocs.io/en/master/guide/usage.html
# If you want to access the filtered objects in your views,
# for example if you want to paginate them, you can do that.
# They are in f.qs
import django_filters
from .models import (Binning
    , Location
    , Name
    , Qualifier
    , QualifierName
    , Reference
    , Relation
    , StratigraphicQualifier
    , TimeSlice)
from django.contrib.auth.models import User
from django_filters import rest_framework as filters

class BinningSchemeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Binning
        fields = ['binning_scheme', 'name', ]

class LocationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Location
        fields = ['name', ]

class NameFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Name
        fields = ['name', ]

class QualifierFilter(django_filters.FilterSet):
    qualifier_name__name = django_filters.CharFilter(lookup_expr='icontains')
    stratigraphic_qualifier__name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Qualifier
        fields = ['qualifier_name__name','stratigraphic_qualifier__name', ]

class QualifierNameFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = QualifierName
        fields = ['name', ]

class RelationFilter(django_filters.FilterSet):

    name_one__name__name = django_filters.CharFilter(lookup_expr='icontains')
    name_two__name__name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Relation
        fields = ['name_one__name__name', 'name_two__name__name', ]

class ReferenceFilter(django_filters.FilterSet):
    first_author = django_filters.CharFilter(lookup_expr='icontains')
    title = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Reference
        fields = ['first_author', 'year', 'title', ]

class StratigraphicQualifierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = StratigraphicQualifier
        fields = ['name', ]

class StructuredNameFilter(django_filters.FilterSet):
    qualifier__qualifier_name__name = django_filters.CharFilter(lookup_expr='icontains')
    qualifier__stratigraphic_qualifier__name = django_filters.CharFilter(lookup_expr='icontains')
    name__name = django_filters.CharFilter(lookup_expr='icontains')
    location__name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Name
        fields = ['name__name','qualifier__qualifier_name__name','qualifier__stratigraphic_qualifier__name','location__name', ]

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', ]


class APINameFilter(filters.FilterSet):
#    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Name
        fields = ['name', 'created_by__first_name', ]

class TimeSliceFilter(django_filters.FilterSet):
    scheme = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = TimeSlice
        fields = ['scheme', 'name' ]
