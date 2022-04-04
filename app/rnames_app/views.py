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
import traceback
from mpltern.ternary.datasets import get_scatter_points
import numpy as np
# end
import json

from django import db
from django.db import connection
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import (HttpResponse, JsonResponse, HttpResponseBadRequest)
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
#from rest_framework.views import APIView
from rest_framework.response import Response
#from .utils.utils import YourClassOrFunction
from rest_framework import status, generics
from .models import (Binning, Location, Name, Qualifier, QualifierName, BinningProgress,
                     Relation, Reference, StratigraphicQualifier, StructuredName, TimeSlice)
from .filters import (BinningSchemeFilter, LocationFilter, NameFilter, QualifierFilter, QualifierNameFilter,
                      ReferenceFilter, RelationFilter, StratigraphicQualifierFilter, StructuredNameFilter, TimeSliceFilter)
from .forms import (ColorfulContactForm, ContactForm, LocationForm, NameForm, QualifierForm, QualifierNameForm, ReferenceForm,
                    ReferenceRelationForm, ReferenceStructuredNameForm, RelationForm, StratigraphicQualifierForm, StructuredNameForm, TimeSliceForm)
from django.contrib.auth.models import User
from .filters import UserFilter

import sys
from subprocess import run, PIPE
from .utils.root_binning import main_binning_fun
from .utils.info import BinningProgressUpdater
from io import StringIO
from contextlib import redirect_stdout
from types import SimpleNamespace
import multiprocessing as mp
import time

from rnames_api.permissions import generate_api_key, list_api_keys, api_key_header
import rnames_api.models as api_models
# , APINameFilter


# def name_list(request):
#    names = Name.objects.is_active().order_by('name')
#    names = Name.objects.order_by('name')
#    return render(request, 'name_list.html', {'names': names})

def user_is_data_admin_or_owner(user, data):
    if user.groups.filter(name='data_admin').exists():
        return True

    if user.groups.filter(name='data_contributor').exists() and data.created_by == user:
        return True

    return False

def binning_process():
    connection.connect()
    info = BinningProgressUpdater()

    if not info.start_binning():
        return

    def time_slices(scheme):
        return list(TimeSlice.objects.is_active().filter(scheme=scheme).order_by('order').values_list('name', flat=True))

    queryset_list = list(Relation.objects.is_active().select_related().values_list(
        'id',
        'reference',
        'reference__year',
        'name_one__id',
        'name_one__location__name',
        'name_one__name__name',
        'name_one__qualifier__level',
        'name_one__qualifier__qualifier_name__name',
        'name_one__qualifier__stratigraphic_qualifier__name',

        'name_two__id',
        'name_two__location__name',
        'name_two__name__name',
        'name_two__qualifier__level',
        'name_two__qualifier__qualifier_name__name',
        'name_two__qualifier__stratigraphic_qualifier__name',
    ))

    cols = [
        'id',
        'reference_id',
        'reference_year',

        'name_1_id',
        'locality_name_1',
        'name_1',
        'level_1',
        'qualifier_name_1',
        'strat_qualifier_1',

        'name_2_id',
        'locality_name_2',
        'name_2',
        'level_2',
        'qualifier_name_2',
        'strat_qualifier_2',
    ]

    try:
        result = main_binning_fun(queryset_list, cols, {
            'rassm': time_slices('rasmussen'),
            'berg': time_slices('bergstrom'),
            'webby': time_slices('webby'),
            'stages': time_slices('stages'),
            'periods': time_slices('periods'),
            'epochs': time_slices('epochs'),
            'eras': time_slices('eras'),
            'eons': time_slices('eons')
        }, info)
    except Exception as e:
        info.set_error(str(e))
        traceback.print_exc()
        return

    update_progress = info.db_update_progress_updater(
        len(result['berg'])
        + len(result['webby'])
        + len(result['stages'])
        + len(result['periods'])
    )

    create_objects = []
    update_objects = []

    def update(obj, oldest, youngest, ts_count, refs, rule):
        obj.oldest = oldest
        obj.youngest = youngest
        obj.ts_count = ts_count
        obj.refs = refs
        obj.rule = rule
        update_objects.append(obj)

    def create(name, scheme, oldest, youngest, ts_count, refs, rule):
        obj = Binning(name=name, binning_scheme=scheme, oldest=oldest, youngest=youngest, ts_count=ts_count, refs=refs, rule=rule)
        create_objects.append(obj)

    def process_result(df, scheme):
        col = SimpleNamespace(**{k: v for v, k in enumerate(df.columns)})

        for row in df.values:
            name = row[col.name]
            data = Binning.objects.is_active().filter(name=name, binning_scheme=scheme)
            if len(data) == 0:
                create(name, scheme, row[col.oldest], row[col.youngest], row[col.ts_count], row[col.refs], row[col.rule])
            else:
                update(data[0], row[col.oldest], row[col.youngest], row[col.ts_count], row[col.refs], row[col.rule])
            update_progress.update()

    process_result(result['berg'], 'x_robinb')
    process_result(result['webby'], 'x_robinw')
    process_result(result['stages'], 'x_robins')
    process_result(result['periods'], 'x_robinp')

    Binning.objects.bulk_create(create_objects, 100)
    Binning.objects.bulk_update(update_objects, ['oldest', 'youngest', 'ts_count', 'refs', 'rule'], 100)

    info.finish_binning()

@login_required
def external(request):
    if not request.user.groups.filter(name='data_admin').exists():
        raise PermissionDenied

    db.connections.close_all()
    handle = mp.Process(target=binning_process)
    handle.start()
    return redirect('/rnames/admin/binning_progress')


def binning(request):

    return render(
        request,
        'binning.html',
    )

@login_required
def binning_info(request):
    data = {}

    data['binning'] = [0, 0]
    data['update'] = [0, 0]

    for entry in BinningProgress.objects.all():
        if entry.name == 'status':
            data['status'] = entry.value_one
            continue

        if entry.name == 'error' or entry.name == 'lock' or entry.name == 'status':
            continue

        if entry.name == 'db_update':
            data['update'] = [entry.value_one, entry.value_two]
            continue

        data['binning'][0] += entry.value_one
        data['binning'][1] += entry.value_two

    return JsonResponse(data)

@login_required
def binning_progress(request):
    return render(request, 'binning_progress.html')

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


@login_required
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


@login_required
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


def help_wizard(request):
    """
    View function for the wizard help page of site.
    """
    return render(
        request,
        'help_wizard.html',
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


class location_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

    model = Location
    success_url = reverse_lazy('location-list')


def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk, is_active=1)
    return render(request, 'location_detail.html', {'location': location})


@login_required
@permission_required('rnames_app.change_location', raise_exception=True)
def location_edit(request, pk):
    location = get_object_or_404(Location, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, location):
        raise PermissionDenied

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
@permission_required('rnames_app.add_location', raise_exception=True)
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


class name_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

    model = Name
    success_url = reverse_lazy('name-list')


def name_detail(request, pk):
    name = get_object_or_404(Name, pk=pk, is_active=1)
    return render(request, 'name_detail.html', {'name': name})


@login_required
@permission_required('rnames_app.change_name', raise_exception=True)
def name_edit(request, pk):
    name = get_object_or_404(Name, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, name):
        raise PermissionDenied

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
@permission_required('rnames_app.add_name', raise_exception=True)
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


class qualifier_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

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
@permission_required('rnames_app.add_qualifier', raise_exception=True)
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
@permission_required('rnames_app.change_qualifier', raise_exception=True)
def qualifier_edit(request, pk):
    qualifier = get_object_or_404(Qualifier, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, qualifier):
        raise PermissionDenied

    if request.method == "POST":
        form = QualifierForm(request.POST, instance=qualifier)
        if form.is_valid():
            qualifier = form.save(commit=False)
            qualifier.save()
            return redirect('qualifier-detail', pk=qualifier.pk)
    else:
        form = QualifierForm(instance=qualifier)
    return render(request, 'qualifier_edit.html', {'form': form})


class qualifiername_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

    model = QualifierName
    success_url = reverse_lazy('qualifiername-list')


def qualifiername_detail(request, pk):
    qualifiername = get_object_or_404(QualifierName, pk=pk, is_active=1)
    return render(request, 'qualifiername_detail.html', {'qualifiername': qualifiername})


@login_required
@permission_required('rnames_app.change_qualifiername', raise_exception=True)
def qualifiername_edit(request, pk):
    qualifiername = get_object_or_404(QualifierName, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, qualifiername):
        raise PermissionDenied

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
@permission_required('rnames_app.add_qualifiername', raise_exception=True)
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


class reference_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

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
@permission_required('rnames_app.change_reference', raise_exception=True)
def reference_edit(request, pk):
    reference = get_object_or_404(Reference, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, reference):
        raise PermissionDenied

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
@permission_required('rnames_app.add_reference', raise_exception=True)
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


class relation_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

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
@permission_required('rnames_app.change_relation', raise_exception=True)
def relation_edit(request, pk):
    relation = get_object_or_404(Relation, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, relation):
        raise PermissionDenied

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
@permission_required('rnames_app.add_relation', raise_exception=True)
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

    if not request.user.groups.filter(name='data_admin').exists():
        raise PermissionDenied

    # Generate counts of some of the main objects
    num_opinions = Relation.objects.is_active().count()

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'run_binning.html',
        context={'num_opinions': num_opinions, },
    )


class stratigraphic_qualifier_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

    model = StratigraphicQualifier
    success_url = reverse_lazy('stratigraphic-qualifier-list')


def stratigraphic_qualifier_detail(request, pk):
    stratigraphicqualifier = get_object_or_404(
        StratigraphicQualifier, pk=pk, is_active=1)
    return render(request, 'stratigraphic_qualifier_detail.html', {'stratigraphicqualifier': stratigraphicqualifier})


@login_required
@permission_required('rnames_app.change_stratigraphicqualifier', raise_exception=True)
def stratigraphic_qualifier_edit(request, pk):
    stratigraphicqualifier = get_object_or_404(
        StratigraphicQualifier, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, stratigraphicqualifier):
        raise PermissionDenied

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
@permission_required('rnames_app.add_stratigraphicqualifier', raise_exception=True)
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


class structuredname_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

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
@permission_required('rnames_app.add_structuredname', raise_exception=True)
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
@permission_required('rnames_app.change_structuredname', raise_exception=True)
def structuredname_edit(request, pk):
    structuredname = get_object_or_404(StructuredName, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, structuredname):
        raise PermissionDenied

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


class timeslice_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())

    model = TimeSlice
    success_url = reverse_lazy('timeslice-list')


def timeslice_detail(request, pk):
    ts = get_object_or_404(TimeSlice, pk=pk, is_active=1)
    return render(request, 'timeslice_detail.html', {'timeslice': ts})


@login_required
@permission_required('rnames_app.change_timeslice', raise_exception=True)
def timeslice_edit(request, pk):
    timeslice = get_object_or_404(TimeSlice, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, timeslice):
        raise PermissionDenied

    if request.method == "POST":
        form = TimeSliceForm(request.POST, instance=timeslice)
        if form.is_valid():
            timeslice = form.save(commit=False)
            timeslice.save()
            return redirect('timeslice-detail', pk=timeslice.pk)
    else:
        form = TimeSliceForm(instance=timeslice)
    return render(request, 'timeslice_edit.html', {'form': form})


def timeslice_list(request):
    f = TimeSliceFilter(
        request.GET, queryset=TimeSlice.objects.is_active().order_by('scheme', 'order'))

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
        'timeslice_list.html',
        {'page_obj': page_obj, 'filter': f, }
    )


@login_required
@permission_required('rnames_app.add_timeslice', raise_exception=True)
def timeslice_new(request):
    if request.method == "POST":
        form = TimeSliceForm(request.POST)
        if form.is_valid():
            timeslice = form.save(commit=False)
            timeslice.created_by_id = request.user.id
            timeslice.created_on = timezone.now()
            timeslice.save()
            return redirect('timeslice-detail', pk=timeslice.pk)
    else:
        form = TimeSliceForm()
    return render(request, 'timeslice_edit.html', {'form': form})

@login_required
def submit(request):
    names = {}
    locations = {}
    structured_names = {}
    relations = []
    updated_relations = []

    data = json.loads(request.body)

    amend = data['reference']['id']['type'] == 'db_reference'

    if amend:
        reference = Reference.objects.get(pk=data['reference']['id']['value'])
    else:
        reference = Reference(
            first_author=data['reference']['firstAuthor'],
            year=data['reference']['year'],
            title=data['reference']['title'],
            doi=data['reference']['doi'],
            link=data['reference']['link']
        )

    for name_data in data['names']:
        ty = name_data['id']['type']
        value = name_data['id']['value']
        name = name_data['name']

        if ty == 'name':
            names[value] = Name(name=name)
        if ty == 'location':
            locations[value] = Location(name=name)

    for structured_name_data in data['structured_names']:
        id = structured_name_data['id']['value']

        name_id = structured_name_data['name_id']['value']
        name_type = structured_name_data['name_id']['type']

        location_id = structured_name_data['location_id']['value']
        location_type = structured_name_data['location_id']['type']

        if location_type == 'db_location':
            location = Location.objects.is_active().get(pk=location_id)
        elif location_type == 'location':
            location = locations[location_id]
        else:
            location = None

        if name_type == 'db_name':
            name = Name.objects.is_active().get(pk=name_id)
        elif name_type == 'name':
            name = names[name_id]
        else:
            name = None

        if name == None or location == None:
            return HttpResponseBadRequest()

        # Wizard doesn't allow creating new qualifiers so this is always a value that exists
        # in the database
        qualifier = Qualifier.objects.is_active().get(pk=structured_name_data['qualifier_id']['value'])

        if structured_name_data['save_with_reference_id']:
            structured_name_reference = reference
        else:
            structured_name_reference = None

        structured_names[id] = StructuredName(
            name=name,
            qualifier=qualifier,
            location=location,
            reference=structured_name_reference,
            remarks=structured_name_data['remarks'],
        )

    for relation_data in data['relations']:
        name_one_id = relation_data['name1']['value']
        name_one_type = relation_data['name1']['type']

        name_two_id = relation_data['name2']['value']
        name_two_type = relation_data['name2']['type']

        if name_one_type == 'db_structured_name':
            name_one = StructuredName.objects.is_active().get(pk=name_one_id)
        elif name_one_type == 'structured_name':
            name_one = structured_names[name_one_id]
        else:
            name_one = None

        if name_two_type == 'db_structured_name':
            name_two = StructuredName.objects.is_active().get(pk=name_two_id)
        elif name_two_type == 'structured_name':
            name_two = structured_names[name_two_id]
        else:
            name_two = None

        if name_one == None or name_two == None:
            return HttpResponseBadRequest()

        belongs_to = relation_data['belongs_to']

        if relation_data['id']['type'] == 'db_relation':
            # Handle updating existing relation
            relation_id = relation_data['id']['value']
            relation = Relation.objects.get(pk=relation_id)

            # Names must match but they can be changed in case inclusion is inverted
            if not (
                (relation.name_one == name_one and relation.name_two == name_two) or
                (relation.name_one == name_two and relation.name_two == name_one)
                ):
                return HttpResponseBadRequest()

            relation.name_one = name_one
            relation.name_two = name_two
            relation.belongs_to = belongs_to

            updated_relations.append(relation)

        else:
            relation = Relation(
                name_one=name_one,
                name_two=name_two,
                belongs_to=belongs_to,
                reference=reference
            )

            relations.append(relation)

    # Ignore existing reference
    if amend == False:
        reference.full_clean()

    for name in names.values():
        name.full_clean()

    for location in locations.values():
        location.full_clean()

    for structured_name in structured_names.values():
        structured_name.full_clean(exclude=['name', 'location', 'reference'])

    for relation in relations:
        relation.full_clean(exclude=['name_one', 'name_two', 'reference'])

    for relation in updated_relations:
        relation.full_clean()

    # Ignore existing reference
    if amend == False:
        reference.save()

    for name in names.values():
        name.save()

    for location in locations.values():
        location.save()

    for structured_name in structured_names.values():
        structured_name.save()

    for relation in relations:
        relation.save()

    for relation in updated_relations:
        relation.save()

    return render(
        request,
        'wizard_result.html', {
            'reference': reference,
            'names': names.values(),
            'locations': locations.values(),
            'structured_names': structured_names.values(),
            'relations': relations,
            'updated_relations': updated_relations
        }
    )

@login_required
def profile(request):
    return render(request, 'profile_keys.html', {'api_keys': list_api_keys(request)})

@login_required
def profile_keys_new(request):
    if not request.user.is_staff:
        return django.http.HttpResponseForbidden

    key = generate_api_key(request)
    return render(request, 'profile_keys_new.html', {'api_keys': list_api_keys(request), 'token': key, 'api_token_header': api_key_header})

@login_required
def profile_key(request, pk):
    keys = list_api_keys(request).filter(id=pk)
    key = keys[0]

    if not key:
        return django.http.HttpResponseNotFound

    entries = []

    return render(request, 'profile_key.html', {'entries': entries, 'key': key})
