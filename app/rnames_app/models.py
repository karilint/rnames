import re
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey
from django.core.validators import MaxValueValidator, MinValueValidator
from simple_history.models import HistoricalRecords
# Used to generate URLs by reversing the URL patterns
from django.urls import reverse
from rnames_api.models import ApiKeyHistoricalModel

class BaseModel(models.Model):
    """
    A base model including basic fields for each Model
    see. https://pypi.org/project/django-userforeignkey/
    """
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = UserForeignKey(
        auto_user_add=True, verbose_name="The user that is automatically assigned", related_name='createdby_%(class)s')
    modified_by = UserForeignKey(
        auto_user=True, verbose_name="The user that is automatically assigned", related_name='modifiedby_%(class)s')
# https://django-simple-history.readthedocs.io/en/2.6.0/index.html
    history = HistoricalRecords(
        bases=[ApiKeyHistoricalModel,],
        history_change_reason_field=models.TextField(null=True),
        inherit=True)
# https://stackoverflow.com/questions/5190313/django-booleanfield-how-to-set-the-default-value-to-true
    class Meta:
        abstract = True

class TimeScale(BaseModel):
    ts_name = models.CharField(max_length=200, blank=False)
    is_public = models.BooleanField(blank=False, default=False, help_text='Are the scheme and its results public')
    def __str__(self):
        return '%s (%i)' % (self.ts_name, self.pk)

    class Meta:
        unique_together = [['ts_name', 'created_by']]

class Location(BaseModel):
    """
    Model representing a Location in RNames (e.g. Sweden, Baltoscandia, New Mexico, China, North Atlantic, etc.)
    """
    name = models.CharField(max_length=200, unique=True,
                            help_text="Enter a Location (e.g. Sweden, Baltoscandia, New Mexico, China, North Atlantic, etc.)")

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
    name = models.CharField(max_length=200, unique=True,
                            help_text="Enter a Name (e.g. Katian, Viru, etc.)")

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
    name = models.CharField(max_length=200, unique=True,
                            help_text="Enter a Qualifier Name (e.g. Trilobite Sub Zone, Chemo zone, Formation, my, Regional stage etc.)")

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
# https://www.crossref.org/blog/dois-and-matching-regular-expressions/
doi_regex_patterns = [
    r'^10.\d{4,9}/[-._;()/:A-Z0-9]+$',
    r'^10.1002/[^\s]+$',
    r'^10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\d$',
    r'^10.1021/\w\w\d+$',
    r'^10.1207/[\w\d]+\&\d+_\d+$'
]
doi_regex = [re.compile(pattern, re.I) for pattern in doi_regex_patterns]


def doi_is_valid(doi):
    if doi is None or type(doi) is not str:
        return False

    return any(regex.match(doi) for regex in doi_regex)


def validate_doi(value):
    if not doi_is_valid(value):
        raise ValidationError(
            _('Value "%(value)s" is not a valid doi number'),
            params={'value': value},
        )


class Reference(BaseModel):
    """
    Model representing a Reference in RNames
    """
    first_author = models.CharField(
        max_length=50, help_text="Enter the name of the first author of the reference", blank=True, null=True,)
    year = models.IntegerField(validators=[MinValueValidator(
        1800), MaxValueValidator(2100)], blank=True, null=True,)
    title = models.CharField(
        max_length=250, help_text="Enter the title of the reference")
    doi = models.CharField(max_length=50, validators=[
                           validate_doi], help_text="Enter the DOI number that begins with 10 followed by a period", blank=True, null=True,)
    link = models.URLField(
        max_length=200, help_text="Enter a valid URL for the reference", blank=True, null=True,)

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
    name = models.CharField(max_length=200, unique=True,
                            help_text="Enter a Stratigraphic Qualifier Name (e.g. Lithostratigraphy, Chemostratigraphy, Sequence stratigraphy, Asolute age, Chronostratigraphy, Biostratigraphy, etc.)")

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
    stratigraphic_qualifier = models.ForeignKey(
        StratigraphicQualifier, on_delete=models.CASCADE)
    LEVEL = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
    )

    level = models.PositiveSmallIntegerField(
        choices=LEVEL, default=1, blank=False, help_text='The level within the Qualifier hiearchy')

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
    reference = models.ForeignKey(Reference, on_delete=models.SET_NULL, blank=True, null=True,
                                  help_text="Reference is not required unless you want to distinguish between two similar Structured Names", )
    remarks = models.TextField(
        max_length=1000, help_text="Enter remarks for the Structured Name", blank=True, null=True,)

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
    name_one = models.ForeignKey(
        StructuredName, on_delete=models.CASCADE, related_name='nameone_%(class)s')
    name_two = models.ForeignKey(
        StructuredName, on_delete=models.CASCADE, related_name='nametwo_%(class)s')
    BELONGS = (
        (1, 'Yes'),
        (0, 'No'),
    )

    belongs_to = models.PositiveSmallIntegerField(
        choices=BELONGS, default=0, blank=True, help_text='Belongs to')

    class DatabaseOrigin(models.IntegerChoices):
        __empty__ = _('(Unknown)')
        RNAMES = 1, _('RNames')
        PBDB = 2, _('Paleobiology Database')
        MACROSTRAT = 3, _('Macrostrat')

    database_origin = models.IntegerField(choices=DatabaseOrigin.choices, default=DatabaseOrigin.RNAMES)

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

class BinningSchemeName(models.Model):
    ts_name = models.ForeignKey(TimeScale, on_delete=models.CASCADE)
    structured_name = models.ForeignKey(StructuredName, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)

    class Meta:
        unique_together = [['ts_name', 'structured_name'], ['ts_name', 'sequence']]

class CountryCode(models.Model):
    iso3166_1_alpha_2 = models.CharField(max_length=2, unique=True, help_text="ISO 3166-1 alpha-2 country code")
    official_name_en = models.CharField(max_length=255, help_text="Official English name")
    region_name = models.CharField(max_length=255, help_text="Region Name")

class AbsoluteAgeValue(BaseModel):
    structured_name = models.ForeignKey(StructuredName, on_delete=models.CASCADE, help_text="Absolute Age Structured Name")
    age = models.FloatField(blank=False, null=False, help_text="Absolute Age in millions of years")
    age_upper_confidence = models.FloatField(default=0, help_text="Upper Confidence Value in millions of years")
    age_lower_confidence = models.FloatField(default=0, help_text="Lower Confidence Value in millions of years")
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)

class Binning(models.Model):
    """
    Model representing a Binning Scheme result in RNames (e.g. Ordovician Time Slices, Phanerozoic Stages, Phanerozoic Epochs, etc.)
    """
    structured_name = models.ForeignKey(StructuredName, on_delete=models.CASCADE, related_name='+')
    oldest = models.ForeignKey(StructuredName, on_delete=models.CASCADE, related_name='+')
    youngest = models.ForeignKey(StructuredName, on_delete=models.CASCADE, related_name='+')
    binning_scheme = models.ForeignKey(TimeScale, blank=True, null=True, help_text='The Binning Scheme', on_delete=models.CASCADE)
    refs = models.CharField(max_length=200, validators=[validate_comma_separated_integer_list])

    class Meta:
        pass
        # ordering = ['name', 'binning_scheme']
        # unique_together = ('binning_scheme', 'name',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular binning instance.
        """
        return reverse('binning-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s: %s' % (self.binning_scheme.ts_name, self.name)

class BinningGeneralised(models.Model):
    name = models.CharField(max_length=255)
    oldest = models.CharField(max_length=255)
    youngest = models.CharField(max_length=255)
    binning_scheme = models.ForeignKey(TimeScale, on_delete=models.CASCADE)

class BinningAbsoluteAge(models.Model):
    structured_name = models.ForeignKey(StructuredName, on_delete=models.CASCADE, related_name='+')
    oldest = models.ForeignKey(StructuredName, on_delete=models.CASCADE, related_name='+')
    youngest = models.ForeignKey(StructuredName, on_delete=models.CASCADE, related_name='+')
    binning_scheme = models.ForeignKey(TimeScale, blank=True, null=True, help_text='The Binning Scheme', on_delete=models.CASCADE)
    refs = models.CharField(max_length=200, validators=[validate_comma_separated_integer_list])
    oldest_age = models.FloatField(default=0, help_text="Lower Confidence Value in millions of years")
    youngest_age = models.FloatField(default=0, help_text="Upper Confidence Value in millions of years")
    reference_age = models.FloatField(default=0, help_text="Age in millions of years")
    age_constraints = models.CharField(max_length=255)
