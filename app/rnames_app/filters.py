# https://django-filter.readthedocs.io/en/master/guide/usage.html
# If you want to access the filtered objects in your views,
# for example if you want to paginate them, you can do that.
# They are in f.qs
import rest_framework_filters as filters

from .models import (Binning
    , Location
    , Name
    , Qualifier
    , QualifierName
    , Reference
    , Relation
    , StratigraphicQualifier
    , StructuredName
    , TimeSlice)
from django.contrib.auth.models import User

class BinningSchemeFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Binning
        fields = ['binning_scheme', 'name', ]

class LocationFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Location
        fields = ['name', ]

class NameFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Name
        fields = ['name', ]

class QualifierFilter(filters.FilterSet):
    qualifier_name__name = filters.CharFilter(lookup_expr='icontains')
    stratigraphic_qualifier__name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Qualifier
        fields = ['qualifier_name__name','stratigraphic_qualifier__name', ]

class QualifierNameFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = QualifierName
        fields = ['name', ]

class RelationFilter(filters.FilterSet):

    name_one__name__name = filters.CharFilter(lookup_expr='icontains')
    name_two__name__name = filters.CharFilter(lookup_expr='icontains')
    reference__doi = filters.CharFilter(lookup_expr='icontains')
    reference__title = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Relation
        fields = ['name_one__name__name', 'name_two__name__name', 'belongs_to', 'reference__doi', 'reference__title' ]

class ReferenceFilter(filters.FilterSet):
    first_author = filters.CharFilter(lookup_expr='icontains')
    title = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Reference
        fields = ['first_author', 'year', 'title', ]

class StratigraphicQualifierFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = StratigraphicQualifier
        fields = ['name', ]

class StructuredNameFilter(filters.FilterSet):
    qualifier__qualifier_name__name = filters.CharFilter(lookup_expr='icontains')
    qualifier__stratigraphic_qualifier__name = filters.CharFilter(lookup_expr='icontains')
    name__name = filters.CharFilter(lookup_expr='icontains')
    location__name = filters.CharFilter(lookup_expr='icontains')
    reference__doi = filters.CharFilter(lookup_expr='icontains')
    reference__title = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = StructuredName
        fields = ['name__name','qualifier__qualifier_name__name','qualifier__stratigraphic_qualifier__name','location__name', 'reference__doi', 'reference__title' ]

class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', ]


class APINameFilter(filters.FilterSet):
#    name = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Name
        fields = ['name', 'created_by__first_name', ]

class TimeSliceFilter(filters.FilterSet):
    scheme = filters.CharFilter(lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = TimeSlice
        fields = ['scheme', 'name' ]
