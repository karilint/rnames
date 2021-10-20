# 2020.02.12 Kari Lintulaakso
# Most of the views use both filters and pagination
# Basic filtering is from https://django-filter.readthedocs.io/en/master/guide/usage.html
# These two are combined using a solution provided by 'Reinstate Monica'
# at https://stackoverflow.com/questions/2047622/how-to-paginate-django-with-other-get-variables/57899037#57899037
import csv
# Start for matplotlib
import io
from django.http.response import Http404
import matplotlib.pyplot as plt
import urllib
import base64
import mpltern
from mpltern.ternary.datasets import get_scatter_points
import numpy as np
# end

from django.db import connection
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
#from rest_framework.views import APIView
from rest_framework.response import Response
#from .utils.utils import YourClassOrFunction
from rest_framework import status, generics
from .models import (Binning, Location, Name, Qualifier, QualifierName,
                     Relation, Reference, StratigraphicQualifier, StructuredName)
from .filters import (BinningSchemeFilter, LocationFilter, NameFilter, QualifierFilter, QualifierNameFilter,
                      ReferenceFilter, RelationFilter, StratigraphicQualifierFilter, StructuredNameFilter)
from .forms import (ColorfulContactForm, ContactForm, LocationForm, NameForm, QualifierForm, QualifierNameForm, ReferenceForm,
                    ReferenceRelationForm, ReferenceStructuredNameForm, RelationForm, StratigraphicQualifierForm, StructuredNameForm)
from django.contrib.auth.models import User
from .filters import UserFilter

import sys
from subprocess import run, PIPE
from .utils.root_binning import main_binning_fun
from .utils.tools import (get_cron_relations, get_time_slices)
from io import StringIO
from contextlib import redirect_stdout
# , APINameFilter


# def name_list(request):
#    names = Name.objects.is_active().order_by('name')
#    names = Name.objects.order_by('name')
#    return render(request, 'name_list.html', {'names': names})

def external(request):

    # Generate counts of some of the main objects
    num_opinions = Relation.objects.is_active().count()

    # inp = request.POST.get('param', 'K') # This doesn't appear to be used anywhere in binning
    rels = get_cron_relations()
    result = main_binning_fun(rels[0], get_time_slices())

    return render(
        request,
        'binning_done.html',
        context={
            'dl_duration': rels[1],
            'duration': result['duration'],
            'berg': result['berg'].to_html(classes='w3-table'),
            'webby': result['webby'].to_html(classes='w3-table'),
            'periods': result['binned_periods'].to_html(classes='w3-table'),
            'stages': result['binned_stages'].to_html(classes='w3-table')
        },
    )


def binning(request):

    return render(
        request,
        'binning.html',
    )


def binning_scheme_list(request):
    f = BinningSchemeFilter(
        request.GET,
        queryset=Binning.objects.is_active().order_by('binning_scheme', 'name')
    )

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'binning_scheme_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


def export_csv_binnings(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rnames_binnings.csv"'

    writer = csv.writer(response)
    writer.writerow(['binning_scheme', 'name', 'oldest',
                    'youngest', 'ts_count', 'refs', 'binning_date'])

    binnings = Binning.objects.is_active().values_list('binning_scheme', 'name',
                                                       'oldest', 'youngest', 'ts_count', 'refs', 'modified_on')
    for binning in binnings:
        # Converting tuple to list
        row = list(binning)
        # Replacing line breaks into ' '
        row[1] = row[1].replace('\n', ' ').replace('\r', '')
        row[2] = row[2].replace('\n', ' ').replace('\r', '')
        row[3] = row[3].replace('\n', ' ').replace('\r', '')
        row[5] = row[5].replace('\n', ' ').replace('\r', '')
        # Converting list back to tuple
        binning = tuple(row)

        writer.writerow(binning)

    return response


def export_csv_references(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rnames_references.csv"'

    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    writer.writerow(['id', 'year', 'first_author', 'title', 'link', ])

    references = Reference.objects.is_active().values_list(
        'id', 'year', 'first_author', 'title', 'link')

    for reference in references:
        # Converting tuple to list
        row = list(reference)
        # Replacing line breaks into ' '
        row[2] = row[2].replace('\n', ' ').replace('\r', '')
        row[3] = row[3].replace('\n', ' ').replace('\r', '')
        if row[4] is not None:
            row[4] = row[4].replace('\n', ' ').replace('\r', '')
        # Converting list back to tuple
        reference = tuple(row)
        writer.writerow(reference)

    return response


def help_database_structure(request):
    """
    View function for the database structure help page of site.
    """
    return render(
        request,
        'help_database_structure.html',
    )


def help_faq(request):
    """
    View function for the help page of site.
    """
    return render(
        request,
        'help_faq.html',
    )


def help_instruction(request):
    """
    View function for the instructions page of site.
    """
    return render(
        request,
        'help_instruction.html',
    )


def help_main(request):
    """
    View function for the help page of site.
    """
    return render(
        request,
        'help.html',
    )


def help_structure_of_binning_algorithm(request):
    """
    View function for the structure of the binning algorithm help page of site.
    """
    return render(
        request,
        'help_structure_of_binning_algorithm.html',
    )


def home(request):
    if request.method == 'POST':
        form = ColorfulContactForm(request.POST)
        if form.is_valid():
            pass  # does nothing, just trigger the validation
    else:
        form = ColorfulContactForm()
    return render(request, 'home.html', {'form': form})


def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_names = Name.objects.is_active().count()
    num_opinions = Relation.objects.is_active().count()
    num_references = Reference.objects.is_active().count()

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_names': num_names, 'num_opinions': num_opinions,
                 'num_references': num_references, },
    )


def parent(request):
    f = StructuredNameFilter(request.GET, queryset=StructuredName.objects.is_active(
    ).select_related().order_by('name', 'qualifier', 'location'))
    paginator = Paginator(f.qs, 5)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'parent.html',
        {'page_obj': page_obj, 'filter': f, }
    )


def child(request):
    f = StructuredNameFilter(request.GET, queryset=StructuredName.objects.is_active(
    ).select_related().order_by('name', 'qualifier', 'location'))
    paginator = Paginator(f.qs, 5)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'child.html',
        {'page_obj': page_obj, 'filter': f, }
    )


class location_delete(DeleteView):
    model = Location
    success_url = reverse_lazy('location-list')


def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk, is_active=1)
    return render(request, 'location_detail.html', {'location': location})


@login_required
def location_edit(request, pk):
    location = get_object_or_404(Location, pk=pk, is_active=1)
    if request.method == "POST":
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            location = form.save(commit=False)
            location.save()
            return redirect('location-detail', pk=location.pk)
    else:
        form = LocationForm(instance=location)
    return render(request, 'location_edit.html', {'form': form})


def location_list(request):
    f = LocationFilter(
        request.GET, queryset=Location.objects.is_active().order_by('name'))

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'location_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
def location_new(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.created_by_id = request.user.id
            location.created_on = timezone.now()
            location.save()
            return redirect('location-detail', pk=location.pk)
    else:
        form = LocationForm()
    return render(request, 'location_edit.html', {'form': form})


class name_delete(DeleteView):
    model = Name
    success_url = reverse_lazy('name-list')


def name_detail(request, pk):
    name = get_object_or_404(Name, pk=pk, is_active=1)
    return render(request, 'name_detail.html', {'name': name})


@login_required
def name_edit(request, pk):
    name = get_object_or_404(Name, pk=pk, is_active=1)
    if request.method == "POST":
        form = NameForm(request.POST, instance=name)
        if form.is_valid():
            name = form.save(commit=False)
            name.save()
            return redirect('name-detail', pk=name.pk)
    else:
        form = NameForm(instance=name)
    return render(request, 'name_edit.html', {'form': form})


def name_list(request):
    f = NameFilter(
        request.GET,
        queryset=Name.objects.is_active().order_by('name')
    )

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'name_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
def name_new(request):
    if request.method == "POST":
        form = NameForm(request.POST)
        if form.is_valid():
            name = form.save(commit=False)
#            name.created_by_id = request.user.id
#            name.created_at = timezone.now()
            name.save()
            return redirect('name-detail', pk=name.pk)
    else:
        form = NameForm()
    return render(request, 'name_edit.html', {'form': form})


class qualifier_delete(DeleteView):
    model = Qualifier
    success_url = reverse_lazy('qualifier-list')


def qualifier_detail(request, pk):
    qualifier = get_object_or_404(Qualifier, pk=pk, is_active=1)
    return render(request, 'qualifier_detail.html', {'qualifier': qualifier})


def qualifier_list(request):
    f = QualifierFilter(request.GET, queryset=Qualifier.objects.is_active(
    ).select_related().order_by('stratigraphic_qualifier', 'level', 'qualifier_name',))
    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'qualifier_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
def qualifier_new(request):
    if request.method == "POST":
        form = QualifierForm(request.POST)
        if form.is_valid():
            qualifier = form.save(commit=False)
            qualifier.save()
            return redirect('qualifier-detail', pk=qualifier.pk)
    else:
        form = QualifierForm()
    return render(request, 'qualifier_edit.html', {'form': form})


@login_required
def qualifier_edit(request, pk):
    qualifier = get_object_or_404(Qualifier, pk=pk, is_active=1)
    if request.method == "POST":
        form = QualifierForm(request.POST, instance=qualifier)
        if form.is_valid():
            qualifier = form.save(commit=False)
            qualifier.save()
            return redirect('qualifier-detail', pk=qualifier.pk)
    else:
        form = QualifierForm(instance=qualifier)
    return render(request, 'qualifier_edit.html', {'form': form})


class qualifiername_delete(DeleteView):
    model = QualifierName
    success_url = reverse_lazy('qualifiername-list')


def qualifiername_detail(request, pk):
    qualifiername = get_object_or_404(QualifierName, pk=pk, is_active=1)
    return render(request, 'qualifiername_detail.html', {'qualifiername': qualifiername})


@login_required
def qualifiername_edit(request, pk):
    qualifiername = get_object_or_404(QualifierName, pk=pk, is_active=1)
    if request.method == "POST":
        form = QualifierNameForm(request.POST, instance=qualifiername)
        if form.is_valid():
            qualifiername = form.save(commit=False)
            qualifiername.save()
            return redirect('qualifier-name-detail', pk=qualifiername.pk)
    else:
        form = QualifierNameForm(instance=qualifiername)
    return render(request, 'qualifiername_edit.html', {'form': form})


def qualifiername_list(request):
    f = QualifierNameFilter(
        request.GET,
        queryset=QualifierName.objects.is_active().order_by('name')
    )

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'qualifiername_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
def qualifiername_new(request):
    if request.method == "POST":
        form = QualifierNameForm(request.POST)
        if form.is_valid():
            qualifiername = form.save(commit=False)
            qualifiername.save()
            return redirect('qualifier-name-detail', pk=qualifiername.pk)
    else:
        form = QualifierNameForm()
    return render(request, 'qualifiername_edit.html', {'form': form})


class reference_delete(DeleteView):
    model = Reference
    success_url = reverse_lazy('reference-list')


def reference_detail(request, pk):
    reference = get_object_or_404(Reference, pk=pk, is_active=1)
    qs1 = (Relation.objects.is_active().filter(reference=reference).select_related()
           .values('name_one__id', 'name_one__name__name', 'name_one__qualifier__qualifier_name__name', 'name_one__location__name', 'name_one__qualifier__stratigraphic_qualifier__name')
           .distinct().order_by('name_one__id', 'name_one__name__name', 'name_one__qualifier__qualifier_name__name', 'name_one__location__name', 'name_one__qualifier__stratigraphic_qualifier__name'))
    qs2 = (Relation.objects.is_active().filter(reference=reference).select_related()
           .values('name_two__id', 'name_two__name__name', 'name_two__qualifier__qualifier_name__name', 'name_two__location__name', 'name_two__qualifier__stratigraphic_qualifier__name')
           .distinct().order_by('name_two__id', 'name_two__name__name', 'name_two__qualifier__qualifier_name__name', 'name_two__location__name', 'name_two__qualifier__stratigraphic_qualifier__name'))
    sn_list = qs1.union(qs2)
    f = RelationFilter(
        request.GET,
        queryset=Relation.objects.is_active().select_related().filter(
            reference__id=pk).order_by('name_one')
    )

    paginator = Paginator(f.qs, 5)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'reference_detail.html', {'reference': reference, 'page_obj': page_obj, 'filter': f, 'sn_list': sn_list, })


@login_required
def reference_edit(request, pk):
    reference = get_object_or_404(Reference, pk=pk, is_active=1)
    if request.method == "POST":
        form = ReferenceForm(request.POST, instance=reference)
        if form.is_valid():
            reference = form.save(commit=False)
            reference.save()
            return redirect('reference-detail', pk=reference.pk)
    else:
        form = ReferenceForm(instance=reference)
    return render(request, 'reference_edit.html', {'form': form})

# If you want to access the filtered objects in your views,
# for example if you want to paginate them, you can do that.
# They are in f.qs
# view function


def reference_list_old(request):
    f = ReferenceFilter(
        request.GET, queryset=Reference.objects.is_active().order_by('title'))
    paginator = Paginator(f.qs, 10)  # Show 10 References per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'reference_list.html', {'filter': f}, {'page_obj': page_obj})
#    return render(request, 'reference_list.html', {'filter': page_obj})
#    return render(request, 'reference_list.html', {'filter': f})


def reference_list(request):
    f = ReferenceFilter(
        request.GET, queryset=Reference.objects.is_active().order_by('title'))
    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'reference_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
def reference_new(request):
    if request.method == "POST":
        form = ReferenceForm(request.POST)
        if form.is_valid():
            reference = form.save(commit=False)
            reference.save()
            return redirect('reference-detail', pk=reference.pk)
    else:
        form = ReferenceForm()
    return render(request, 'reference_edit.html', {'form': form})


class old_reference_relation_delete(DeleteView):
    model = Relation

    def get_object(self, queryset=None):
        obj = super(reference_relation_delete, self).get_object()
        if not obj.reference:
            raise Http404
        return obj
    success_url = reverse_lazy('reference-detail')


def reference_structured_name_detail(request, pk, reference):
    structuredname = get_object_or_404(StructuredName, pk=pk, is_active=1)
    reference = get_object_or_404(Reference, pk=reference, is_active=1)
    current_relations = Relation.objects.is_active().filter(name_one=structuredname).filter(
        reference=reference).exclude(name_two=structuredname).select_related().order_by('name_one')
    current_name_two_ids = current_relations.values_list(
        'name_two__id', flat=True)
    available_relations = Relation.objects.is_active().filter(reference=reference).exclude(name_one__id__in=current_name_two_ids).exclude(name_two__id__in=current_name_two_ids).select_related().values('name_two',
                                                                                                                                                                                                         'name_two__name__name', 'name_two__qualifier__qualifier_name__name', 'name_two__qualifier__stratigraphic_qualifier__name', 'name_two__location__name', 'name_two__reference',).distinct().order_by('name_two__name__name')
    f = StructuredNameFilter(request.GET, queryset=available_relations)
    paginator = Paginator(f.qs, 5)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'reference_structured_name_detail.html', {'structuredname': structuredname, 'reference': reference, 'current_relations': current_relations, 'available_relations': available_relations, 'page_obj': page_obj, 'filter': f, })

#    f = StructuredNameFilter(request.GET, queryset=StructuredName.objects.is_active().select_related().order_by('name', 'qualifier', 'location'))


@login_required
def reference_structured_name_new(request, reference):
    reference = get_object_or_404(Reference, pk=reference, is_active=1)

    if request.method == "POST":
        form = ReferenceStructuredNameForm(request.POST)
        if form.is_valid():
            name_id = request.POST.get('name_id', 1)
            name_one = get_object_or_404(
                StructuredName, pk=name_id, is_active=1)
            relation = form.save(commit=False)
            relation.reference = reference
            relation.name_one = name_one
            relation.name_two = name_one
            relation.save()
            return redirect('reference-detail', pk=relation.reference.id)
    else:
        # Set default for names, set them later to same as name_one.
        name_one = get_object_or_404(StructuredName, pk=1, is_active=1)
        name_two = get_object_or_404(StructuredName, pk=1, is_active=1)

        form = ReferenceStructuredNameForm()
    return render(request, 'reference_sturctured_name_edit.html', {'reference': reference, 'form': form})

# https://stackoverflow.com/questions/52065046/django-deleteview-pass-argument-from-foreignkeys-model-to-get-success-url


class reference_relation_delete(DeleteView):
    model = Relation

    def get_success_url(self):
        reference = self.object.reference
        return reverse_lazy('reference-detail', kwargs={'pk': reference.pk})

# @login_required
# def reference_relation_new(request, reference):
#    reference = get_object_or_404(Reference, pk=reference, is_active=1)
#    if request.method == "POST":
#        form = ReferenceRelationForm(request.POST)
#        if form.is_valid():
#            relation = form.save(commit=False)
#            relation.reference = reference
#            relation.save()
#            return redirect('reference-detail', pk=relation.reference.id)
#    else:
#        form = ReferenceRelationForm()
#    return render(request, 'relation_edit.html', {'form': form})


@login_required
def reference_relation_new(request, name_one, reference):

    name_one = get_object_or_404(StructuredName, pk=name_one, is_active=1)
    reference = get_object_or_404(Reference, pk=reference, is_active=1)
    current_relations = Relation.objects.is_active().filter(name_one=name_one).filter(
        reference=reference).exclude(name_two=name_one).select_related().order_by('name_one')
    current_name_two_ids = current_relations.values_list(
        'name_two__id', flat=True)
    available_relations = (Relation.objects.is_active()
                           .filter(reference=reference)
                           .exclude(name_one=name_one)
                           .exclude(name_two=name_one)
                           .exclude(name_one__id__in=current_name_two_ids)
                           .exclude(name_two__id__in=current_name_two_ids)
                           .select_related()
                           .values('name_two', 'name_two__name__name', 'name_two__qualifier__qualifier_name__name', 'name_two__qualifier__stratigraphic_qualifier__name', 'name_two__location__name', 'name_two__reference__first_author', 'name_two__reference__year',)
                           .distinct().order_by('name_two__name__name'))

    if request.method == "POST":
        form = ReferenceRelationForm(request.POST)
        if form.is_valid():
            name_id = request.POST.get('name_id', 1)
            name_two = get_object_or_404(
                StructuredName, pk=name_id, is_active=1)
            relation = form.save(commit=False)
            relation.reference = reference
            relation.name_one = name_one
            relation.name_two = name_two
            relation.save()
            return redirect('reference-relation-new', name_one=name_one.id, reference=reference.id)
    else:
        # Set default for names
        name_one = name_one
        name_two = get_object_or_404(StructuredName, pk=1, is_active=1)
        form = ReferenceRelationForm()
    return render(request, 'reference_relation_edit.html', {'name_one': name_one, 'reference': reference, 'current_relations': current_relations, 'available_relations': available_relations, 'form': form},)


class relation_delete(DeleteView):
    model = Relation
    success_url = reverse_lazy('relation-list')


def relation_detail(request, pk):
    relation = get_object_or_404(Relation, pk=pk, is_active=1)
    return render(request, 'relation_detail.html', {'relation': relation})


def relation_sql_detail(request, name_one, name_two):

    with connection.cursor() as cursor:
        cursor.execute("""
            select r.id
            from rnames_app_relation r
            where (r.name_one_id=%s and r.name_two_id=%s)
            	or (r.name_one_id=%s and r.name_two_id=%s)
            	and r.is_active=true
            limit 1""", [name_one, name_two, name_two, name_one])

        relations = dictfetchall(cursor)[0]
        relation_id = relations.get('id')

    relation = get_object_or_404(Relation, pk=relation_id, is_active=1)

    with connection.cursor() as cursor:
        cursor.execute("""
            select distinct ref.*
            from rnames_app_relation r
            join rnames_app_reference ref
            	on ref.id=r.reference_id
            	and ref.is_active=true
            where (r.name_one_id=%s and r.name_two_id=%s)
            	or (r.name_one_id=%s and r.name_two_id=%s)
            	and r.is_active=true
    		order by ref.first_author, ref.year""", [name_one, name_two, name_two, name_one])

        references = dictfetchall(cursor)

    return render(request, 'relation_sql_detail.html', {'relation': relation, 'references': references})


@login_required
def relation_edit(request, pk):
    relation = get_object_or_404(Relation, pk=pk, is_active=1)
    if request.method == "POST":
        form = RelationForm(request.POST, instance=relation)
        if form.is_valid():
            relation = form.save(commit=False)
            relation.save()
            return redirect('relation-detail', pk=relation.pk)
    else:
        form = RelationForm(instance=relation)
    return render(request, 'relation_edit.html', {'form': form})

# https://docs.djangoproject.com/en/3.0/topics/pagination/
# https://django-filter.readthedocs.io/en/master/guide/usage.html


def relation_list(request):
    f = RelationFilter(
        request.GET,
        queryset=Relation.objects.is_active().select_related().order_by('name_one')
    )

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'relation_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
def relation_new(request, reference_id):
    if request.method == "POST":
        form = RelationForm(request.POST)
        if form.is_valid():
            relation = form.save(commit=False)
            relation.save()
            return redirect('relation-detail', pk=relation.pk)
    else:
        form = RelationForm()
    return render(request, 'relation_edit.html', {'form': form})


def rnames_detail(request):
    return render(request, 'rnames_detail.html', )


@login_required
def run_binning(request):
    """
    View function for the run binning operation.
    """
    # Generate counts of some of the main objects
    num_opinions = Relation.objects.is_active().count()

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'run_binning.html',
        context={'num_opinions': num_opinions, },
    )


class stratigraphic_qualifier_delete(DeleteView):
    model = StratigraphicQualifier
    success_url = reverse_lazy('stratigraphic-qualifier-list')


def stratigraphic_qualifier_detail(request, pk):
    stratigraphicqualifier = get_object_or_404(
        StratigraphicQualifier, pk=pk, is_active=1)
    return render(request, 'stratigraphic_qualifier_detail.html', {'stratigraphicqualifier': stratigraphicqualifier})


@login_required
def stratigraphic_qualifier_edit(request, pk):
    stratigraphicqualifier = get_object_or_404(
        StratigraphicQualifier, pk=pk, is_active=1)
    if request.method == "POST":
        form = StratigraphicQualifierForm(
            request.POST, instance=stratigraphicqualifier)
        if form.is_valid():
            stratigraphicqualifier = form.save(commit=False)
            stratigraphicqualifier.save()
            return redirect('stratigraphic-qualifier-detail', pk=stratigraphicqualifier.pk)
    else:
        form = StratigraphicQualifierForm(instance=stratigraphicqualifier)
    return render(request, 'stratigraphic_qualifier_edit.html', {'form': form})


def stratigraphic_qualifier_list(request):
    f = StratigraphicQualifierFilter(
        request.GET,
        queryset=StratigraphicQualifier.objects.is_active().order_by('name')
    )

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'stratigraphic_qualifier_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
def stratigraphic_qualifier_new(request):
    if request.method == "POST":
        form = StratigraphicQualifierForm(request.POST)
        if form.is_valid():
            stratigraphicqualifier = form.save(commit=False)
            stratigraphicqualifier.save()
            return redirect('stratigraphic-qualifier-detail', pk=stratigraphicqualifier.pk)
    else:
        form = StratigraphicQualifierForm()
    return render(request, 'stratigraphic_qualifier_edit.html', {'form': form})


class structuredname_delete(DeleteView):
    model = StructuredName
    success_url = reverse_lazy('structuredname-list')


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def structuredname_detail(request, pk):
    structuredname = get_object_or_404(StructuredName, pk=pk, is_active=1)

    with connection.cursor() as cursor:
        #        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [master_entity.id])
        cursor.execute("""
			select r.belongs_to
			--	, n1.name name_one
			--	, qn1.name qualifier_one
			--	, sq1.name stratigraphic_qualifier_one
			--	, q1.`level` qualifier_one_level
				, n2.name name
				, qn2.name qualifier
				, sq2.name stratigraphic_qualifier
				, q2.`level` `level`
				, l2.name location
            	, sn2.id fk

			from rnames_app_relation r
			join rnames_app_structuredname sn1
				on r.name_one_id=sn1.id and sn1.is_active=true
			join rnames_app_name n1
				on n1.id=sn1.name_id and n1.is_active=true
			join rnames_app_qualifier q1
				on q1.id=sn1.qualifier_id and q1.is_active=true
			join rnames_app_qualifiername qn1
				on qn1.id=q1.qualifier_name_id and qn1.is_active=true
			join rnames_app_stratigraphicqualifier sq1
				on sq1.id=q1.stratigraphic_qualifier_id and sq1.is_active=true

			join rnames_app_structuredname sn2
				on r.name_two_id=sn2.id and sn2.is_active=true
			join rnames_app_name n2
				on n2.id=sn2.name_id and n2.is_active=true
			join rnames_app_qualifier q2
				on q2.id=sn2.qualifier_id and q2.is_active=true
			join rnames_app_qualifiername qn2
				on qn2.id=q2.qualifier_name_id and qn2.is_active=true
			join rnames_app_stratigraphicqualifier sq2
				on sq2.id=q2.stratigraphic_qualifier_id and sq2.is_active=true
			join rnames_app_location l2
				on l2.id=sn2.location_id and l2.is_active=true
			where r.name_one_id=%s and r.name_two_id<>%s and r.is_active=true

			union

			select r.belongs_to
			--	, n1.name name_one
			--	, qn1.name qualifier_one
			--	, sq1.name stratigraphic_qualifier_one
			--	, q1.`level` qualifier_one_level
				, n1.name name
				, qn1.name qualifier
				, sq1.name stratigraphic_qualifier
				, q1.`level` `level`
				, l1.name location
            	, sn1.id fk

			from rnames_app_relation r
			join rnames_app_structuredname sn1
				on r.name_one_id=sn1.id and sn1.is_active=true
			join rnames_app_name n1
				on n1.id=sn1.name_id and n1.is_active=true
			join rnames_app_qualifier q1
				on q1.id=sn1.qualifier_id and q1.is_active=true
			join rnames_app_qualifiername qn1
				on qn1.id=q1.qualifier_name_id and qn1.is_active=true
			join rnames_app_stratigraphicqualifier sq1
				on sq1.id=q1.stratigraphic_qualifier_id and sq1.is_active=true
			join rnames_app_location l1
				on l1.id=sn1.location_id and l1.is_active=true

			join rnames_app_structuredname sn2
				on r.name_two_id=sn2.id and sn2.is_active=true
			join rnames_app_name n2
				on n2.id=sn2.name_id and n2.is_active=true
			join rnames_app_qualifier q2
				on q2.id=sn2.qualifier_id and q2.is_active=true
			join rnames_app_qualifiername qn2
				on qn2.id=q2.qualifier_name_id and qn2.is_active=true
			join rnames_app_stratigraphicqualifier sq2
				on sq2.id=q2.stratigraphic_qualifier_id and sq2.is_active=true
			join rnames_app_location l2
				on l2.id=sn2.location_id and l2.is_active=true
			where r.name_one_id<>%s and r.name_two_id=%s and r.is_active=true

			order by 5 desc,4,2""", [structuredname.id, structuredname.id, structuredname.id, structuredname.id])

        current_relations = dictfetchall(cursor)
    return render(request, 'structuredname_detail.html', {'structuredname': structuredname, 'current_relations': current_relations, })


def structuredname_list(request):
    f = StructuredNameFilter(request.GET, queryset=StructuredName.objects.is_active(
    ).select_related().order_by('name', 'qualifier', 'location'))
    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'structuredname_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
def structuredname_new(request):
    if request.method == "POST":
        form = StructuredNameForm(request.POST)
        if form.is_valid():
            structuredname = form.save(commit=False)
            structuredname.save()
            return redirect('structuredname-detail', pk=structuredname.pk)
    else:
        form = StructuredNameForm()
    return render(request, 'structuredname_edit.html', {'form': form})


@login_required
def structuredname_edit(request, pk):
    structuredname = get_object_or_404(StructuredName, pk=pk, is_active=1)
    if request.method == "POST":
        form = StructuredNameForm(request.POST, instance=structuredname)
        if form.is_valid():
            structuredname = form.save(commit=False)
            structuredname.save()
            return redirect('structuredname-detail', pk=structuredname.pk)
    else:
        form = StructuredNameForm(instance=structuredname)
    return render(request, 'structuredname_edit.html', {'form': form})


def structuredname_select(request):
    # def reference_detail(request, pk):
    #    reference = get_object_or_404(Reference, pk=pk, is_active=1)

    #    qs1=(Relation.objects.is_active().filter(reference=reference).select_related()
    #        .values('name_one__id')
    #        .distinct().order_by('name_one__id'))
    #    qs2=(Relation.objects.is_active().filter(reference=reference).select_related()
    #        .values('name_two__id')
    #        .distinct().order_by('name_two__id'))
    #    sn_list= qs1.union(qs2)

    #    f = StructuredNameFilter(request.GET, queryset=StructuredName.objects.is_active().exclude(id__in=sn_list).select_related().order_by('name', 'qualifier', 'location'))
    f = StructuredNameFilter(request.GET, queryset=StructuredName.objects.is_active(
    ).select_related().order_by('name', 'qualifier', 'location'))

    paginator = Paginator(f.qs, 5)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'select_structured_name.html',
        {'page_obj': page_obj, 'filter': f, }
    )


def user_search(request):
    user_list = User.objects.all()
    user_filter = UserFilter(request.GET, queryset=user_list)
    return render(request, 'user_list.html', {'filter': user_filter})
