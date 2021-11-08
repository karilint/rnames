from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey
from django.core.validators import MaxValueValidator, MinValueValidator
from simple_history.models import HistoricalRecords
from django.urls import reverse #Used to generate URLs by reversing the URL patterns

class CustomQuerySet(QuerySet):
    def delete(self):
        self.update(is_active=False)

# https://simpleisbetterthancomplex.com/tips/2016/08/16/django-tip-11-custom-manager-with-chainable-querysets.html
class ActiveManager(models.Manager):
    def is_active(self):
        return self.model.objects.filter(is_active=True)

    def get_queryset(self):
        return CustomQuerySet(self.model, using=self._db)

# https://medium.com/@KevinPavlish/add-common-fields-to-all-your-django-models-bce033ac2cdc
class BaseModel(models.Model):
    """
    A base model including basic fields for each Model
    see. https://pypi.org/project/django-userforeignkey/
    """
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = UserForeignKey(auto_user_add=True, verbose_name="The user that is automatically assigned", related_name='createdby_%(class)s')
    modified_by = UserForeignKey(auto_user=True, verbose_name="The user that is automatically assigned", related_name='modifiedby_%(class)s')
# https://django-simple-history.readthedocs.io/en/2.6.0/index.html
    history = HistoricalRecords(
        history_change_reason_field=models.TextField(null=True),
        inherit=True)
# https://stackoverflow.com/questions/5190313/django-booleanfield-how-to-set-the-default-value-to-true
    is_active = models.BooleanField(default=True, help_text='Is the record active')
    objects = ActiveManager()

# https://stackoverflow.com/questions/4825815/prevent-delete-in-django-model
    def delete(self):
        self.is_active = False
        print(self._meta.object_name)

        # List of first lefel models
        # qualifier -> stratigraphicqualifier, qualifier_name
        # relation -> NameOne, NameTwo, Reference
        # StructuredName -> Location, Name, Qualifier, (Reference)

        if self._meta.object_name == 'Reference': # https://stackoverflow.com/questions/3599524/get-class-name-of-django-model
            qs = Relation.objects.is_active().filter(reference__id=self.pk)
            for x in qs:
                print(str(x._meta.object_name) + ' id: ' + str(x.pk) + ' deleted')
                x.delete()

        if self._meta.object_name == 'Reference': # https://stackoverflow.com/questions/3599524/get-class-name-of-django-model
            qs = StructuredName.objects.is_active().filter(reference__id=self.pk)
            for x in qs:
                print(str(x._meta.object_name) + ' id: ' + str(x.pk) + ' deleted')
                x.delete()

        if self._meta.object_name == 'StructuredName':
            qs = Relation.objects.is_active().filter(name_one__id=self.pk) | Relation.objects.is_active().filter(name_two__id=self.pk)
            for x in qs:
                print(str(x._meta.object_name) + ' id: ' + str(x.pk) + ' deleted')
                x.delete()

        if self._meta.object_name == 'Name':
            qs=StructuredName.objects.is_active().filter(name__id=self.pk)
            for x in qs:
                print(str(x._meta.object_name) + ' id: ' + str(x.pk) + ' deleted')
                x.delete()

        if self._meta.object_name == 'Location':
            qs=StructuredName.objects.is_active().filter(location__id=self.pk)
            for x in qs:
                print(str(x._meta.object_name) + ' id: ' + str(x.pk) + ' deleted')
                x.delete()

        if self._meta.object_name == 'Qualifier':
            qs=StructuredName.objects.is_active().filter(qualifier__id=self.pk)
            for x in qs:
                print(str(x._meta.object_name) + ' id: ' + str(x.pk) + ' deleted')
                x.delete()

        if self._meta.object_name == 'QualifierName':
            qs=Qualifier.objects.is_active().filter(qualifier_name__id=self.pk)
            for x in qs:
                print(str(x._meta.object_name) + ' id: ' + str(x.pk) + ' deleted')
                x.delete()

        if self._meta.object_name == 'StratigraphicQualifier':
            qs=Qualifier.objects.is_active().filter(stratigraphic_qualifier__id=self.pk)
            for x in qs:
                print(str(x._meta.object_name) + ' id: ' + str(x.pk) + ' deleted')
                x.delete()

        print(str(self._meta.object_name) + ' id: ' + str(self.pk) + ' deleted')
        self.save()

    class Meta:
        abstract = True

class Binning(BaseModel):
    """
    Model representing a Binning Scheme result in RNames (e.g. Ordovician Time Slices, Phanerozoic Stages, Phanerozoic Epochs, etc.)
    """
    BINNING = (
        ('x_robinb', 'Ordovician Time Slices (Bergström)'),
        ('x_robinw', 'Ordovician Time Slices (Webby)'),
        ('x_robins', 'Phanerozoic Stages (ICS Chart, 2020)'),
        ('x_robinp', 'Phanerozoic Epochs (ICS Chart, 2020)'),
    )

    binning_scheme = models.CharField(max_length=200, choices=BINNING, blank=False, help_text='The Binning Scheme')
    name = models.CharField(max_length=200, help_text="Enter a Name (e.g. Katian, Viru, etc.)")
    oldest = models.CharField(max_length=200, help_text="Enter a Name (e.g. Katian, Viru, etc.)")
    youngest = models.CharField(max_length=200, help_text="Enter a Name (e.g. Katian, Viru, etc.)")
    ts_count = models.PositiveSmallIntegerField(default=0, blank=False, help_text='The count of Time Slices within the binned Name.')
    refs = models.CharField(max_length=200, validators=[validate_comma_separated_integer_list])
    rule = models.CharField(max_length=5, blank=False, help_text='Enter the rule for the Binning.')

    class Meta:
        ordering = ['name', 'binning_scheme']
        unique_together = ('binning_scheme', 'name',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular binning instance.
        """
        return reverse('binning-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s: %s' % (self.binning_scheme, self.name)

class Location(BaseModel):
    """
    Model representing a Location in RNames (e.g. Sweden, Baltoscandia, New Mexico, China, North Atlantic, etc.)
    """
    name = models.CharField(max_length=200, unique=True, help_text="Enter a Location (e.g. Sweden, Baltoscandia, New Mexico, China, North Atlantic, etc.)")

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular name instance.
        """
        return reverse('location-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)


class Name(BaseModel):
    """
    Model representing a Name in RNames (e.g. Katian, Viru, etc.)
    """
    name = models.CharField(max_length=200, unique=True, help_text="Enter a Name (e.g. Katian, Viru, etc.)")

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular name instance.
        """
        return reverse('name-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)


class QualifierName(BaseModel):
    """
    Model representing a Qualifier Name in RNames (e.g. Trilobite Sub Zone, Chemo zone, Formation, my, Regional stage, etc.)
    """
    name = models.CharField(max_length=200, unique=True, help_text="Enter a Qualifier Name (e.g. Trilobite Sub Zone, Chemo zone, Formation, my, Regional stage etc.)")


    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular qualifier name instance.
        """
        return reverse('qualifier-name-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)

# For doi validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_doi(value):
    if not value.startswith( '10.' ):
        raise ValidationError(
            _('Value "%(value)s" does not begin with 10 followed by a period'),
            params={'value': value},
        )

class Reference(BaseModel):
    """
    Model representing a Reference in RNames
    """
    first_author = models.CharField(max_length=50, help_text="Enter the name of the first author of the reference", blank=True, null=True,)
    year = models.IntegerField(validators=[MinValueValidator(1800), MaxValueValidator(2100)], blank=True, null=True,)
    title = models.CharField(max_length=250, help_text="Enter the title of the reference")
    doi = models.CharField(max_length=50, validators=[validate_doi], help_text="Enter the DOI number that begins with 10 followed by a period", blank=True, null=True,)
    link = models.URLField(max_length=200, help_text="Enter a valid URL for the reference", blank=True, null=True,)

    class Meta:
        ordering = ['first_author', 'year', 'title']

    def get_absolute_url(self):
        """
        Returns the url to access a particular reference instance.
        """
        return reverse('reference-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s, %s: %s' % (self.first_author, self.year, self.title)


class StratigraphicQualifier(BaseModel):
    """
    Model representing a Stratigraphic Qualifier Name in RNames (e.g. Lithostratigraphy, Chemostratigraphy, Sequence stratigraphy, Asolute age, Chronostratigraphy, Biostratigraphy, etc.)
    """
    name = models.CharField(max_length=200, unique=True, help_text="Enter a Stratigraphic Qualifier Name (e.g. Lithostratigraphy, Chemostratigraphy, Sequence stratigraphy, Asolute age, Chronostratigraphy, Biostratigraphy, etc.)")


    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular stratigraphic qualifier instance.
        """
        return reverse('stratigraphic-qualifier-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)


class Qualifier(BaseModel):
    """
    Model representing a Qualifier in RNames (e.g. Eon/Chronostratigraphy, Era/Chronostratigraphy, Formation/Lithostratigraphy, etc.)
    """
    qualifier_name = models.ForeignKey(QualifierName, on_delete=models.CASCADE)
    stratigraphic_qualifier = models.ForeignKey(StratigraphicQualifier, on_delete=models.CASCADE)
    LEVEL = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
    )

    level = models.PositiveSmallIntegerField(choices=LEVEL, default=1, blank=False, help_text='The level within the Qualifier hiearchy')

    class Meta:
        ordering = ['stratigraphic_qualifier', 'level', 'qualifier_name']
        unique_together = ('qualifier_name', 'stratigraphic_qualifier',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular qualifier instance.
        """
        return reverse('qualifier-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s / %s - %s' % (self.qualifier_name, self.stratigraphic_qualifier, self.level)

class StructuredName(BaseModel):
    """
    Model representing a StructuredName - a combination of Name, Qualifier, Location (and Reference) in RNames (e.g. 1a / TimeSlice_Webby / Global, 451.08 / absolute Time / Global, etc.)
    """
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    qualifier = models.ForeignKey(Qualifier, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    reference = models.ForeignKey(Reference, on_delete=models.SET_NULL, blank=True, null=True, help_text="Reference is not required unless you want to distinguish between two similar Structured Names", )
    remarks = models.TextField(max_length=1000, help_text="Enter remarks for the Structured Name", blank=True, null=True,)

    class Meta:
        ordering = ['name', 'qualifier', 'location', 'reference']
        unique_together = ('name', 'qualifier', 'location', 'reference')

    def get_absolute_url(self):
        """
        Returns the url to access a particular structured name instance.
        """
        return reverse('structured-name-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        if self.reference is None:
            return '%s - %s - %s' % (self.name, self.qualifier, self.location)
        else:
            return '%s - %s - %s - %s' % (self.name, self.qualifier, self.location, self.reference)


class Relation(BaseModel):
    """
    Model representing a Relation between two Structured Names in RNames (e.g. Likhall-Bed-Sweden/466.72-absolute Time-Global, etc.)
    """
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    name_one = models.ForeignKey(StructuredName, on_delete=models.CASCADE, related_name='nameone_%(class)s')
    name_two = models.ForeignKey(StructuredName, on_delete=models.CASCADE, related_name='nametwo_%(class)s')
    BELONGS = (
        (1, 'Yes'),
        (0, 'No'),
    )

    belongs_to = models.PositiveSmallIntegerField(choices=BELONGS, default=0, blank=True, help_text='Belongs to')

    class Meta:
        ordering = ['reference', 'name_one', 'name_two']
        unique_together = ('reference', 'name_one', 'name_two',)

    def level_1(self):
        return self.name_one.qualifier.level

    def level_2(self):
        return self.name_two.qualifier.level

    def locality_name_1(self):
        return self.name_one.location.name

    def locality_name_2(self):
        return self.name_two.location.name

    def name_1(self):
        return self.name_one.name.name

    def name_2(self):
        return self.name_two.name.name

    def get_absolute_url(self):
        """
        Returns the url to access a particular relation instance.
        """
        return reverse('relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s | %s' % (self.name_one, self.name_two)

class TimeSlice(BaseModel):
    name = models.CharField(max_length=200, blank=False)
    order = models.IntegerField(help_text='Chronological order within scheme.')
    scheme = models.CharField(max_length=200, blank=False)

    class Meta:
        ordering = ['scheme', 'order']

    def __str__(self):
        return '%s %d %s' % (self.scheme, self.order, self.name)

    def get_absolute_url(self):
        """
        Returns the url to access a particular name instance.
        """
        return reverse('timeslice-detail', args=[str(self.id)])

