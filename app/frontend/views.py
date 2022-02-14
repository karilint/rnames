from django.shortcuts import render
from rnames_app.models import (Location, Name, Qualifier, QualifierName, Reference, StructuredName, Relation)
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.
@login_required
@permission_required('rnames_app.add_reference', raise_exception=True)
def index(request, *args, **kwargs):
    names = list(Name.objects.filter(is_active=True).values('id', 'name'))
    locations = list(Location.objects.filter(is_active=True).values('id', 'name'))
    qualifier_names = list(QualifierName.objects.filter(is_active=True).values('id', 'name'))
    qualifiers = list(Qualifier.objects.filter(is_active=True).values('id', 'level', 'qualifier_name_id', 'stratigraphic_qualifier_id'))
    references = list(Reference.objects.filter(is_active=True).values('id', 'title', 'first_author', 'link', 'year', 'doi'))
    structured_names = list(StructuredName.objects.filter(is_active=True).values('id', 'location_id', 'name_id', 'qualifier_id', 'reference_id', 'remarks'))

    reference_id = request.GET.get('amendId', None)
    amend_info = {'amend': reference_id != None}

    if reference_id:
        ref = Reference.objects.filter(is_active=True).get(pk=reference_id)
        rels = list(Relation.objects.filter(is_active=True, reference_id=reference_id).values('id', 'name_one_id', 'name_two_id', 'belongs_to'))
        amend_info['referenceId'] = reference_id
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
