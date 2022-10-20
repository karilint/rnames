from django.shortcuts import render
from rnames_app.models import (Location, Name, Qualifier, QualifierName, Reference, StructuredName, Relation)
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.
@login_required
@permission_required('rnames_app.add_reference', raise_exception=True)
def index(request, pk=None, *args, **kwargs):
    names = list(Name.objects.all().values('id', 'name'))
    locations = list(Location.objects.all().values('id', 'name'))
    qualifier_names = list(QualifierName.objects.all().values('id', 'name'))
    qualifiers = list(Qualifier.objects.all().values('id', 'level', 'qualifier_name_id', 'stratigraphic_qualifier_id'))
    references = list(Reference.objects.all().values('id', 'title', 'first_author', 'link', 'year', 'doi'))
    structured_names = list(StructuredName.objects.all().values('id', 'location_id', 'name_id', 'qualifier_id', 'reference_id', 'remarks'))

    amend_info = {'amend': pk != None}

    if pk:
        ref = Reference.objects.all().get(pk=pk)
        rels = list(Relation.objects.filter(reference_id=pk).values('id', 'name_one_id', 'name_two_id', 'belongs_to'))
        amend_info['referenceId'] = pk
        amend_info['relations'] = rels

    return render(request, 'frontend/index.html', {
        'names': names,
        'locations': locations,
        'qualifier_names': qualifier_names,
        'qualifiers': qualifiers,
        'references': references,
        'structured_names': structured_names,
        'amend_info': amend_info
    })
