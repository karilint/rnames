from django import forms
from django_select2.forms import (
    ModelSelect2Widget,
)
from .models import Location, Name, Qualifier, QualifierName, Reference, Relation, StratigraphicQualifier, StructuredName, TimeSlice

class ContactForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        help_text='Write here your message!'
    )
    source = forms.CharField(       # A hidden input for internal use
        max_length=50,              # tell from which page the user sent the message
        widget=forms.HiddenInput()
    )

class ColorfulContactForm(forms.Form):
    name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'class': 'w3-input w3-border',
                'placeholder': 'Write your name here'
            }
        )
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'class': 'w3-input w3-border',
                'placeholder': 'Write your email here'
            }
        )
    )
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(
            attrs={
            'class': 'w3-input w3-border'
            }
        ),
        help_text='Write here your message!'
    )

    def clean(self):
        cleaned_data = super(ColorfulContactForm, self).clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        message = cleaned_data.get('message')
        if not name and not email and not message:
            raise forms.ValidationError('You have to write something!')

class LocationForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ('name',)

class NameForm(forms.ModelForm):

    class Meta:
        model = Name
        fields = ('name',)

class QualifierForm(forms.ModelForm):

    class Meta:
        model = Qualifier
        fields = ('qualifier_name', 'stratigraphic_qualifier', 'level',)

class QualifierNameForm(forms.ModelForm):

    class Meta:
        model = QualifierName
        fields = ('name',)

class ReferenceForm(forms.ModelForm):
    link = forms.CharField(widget=forms.Textarea(attrs={'cols': 100, 'rows': 1}))
    class Meta:
        model = Reference
        fields = ('first_author','year','title','doi','link',)

class ReferenceWidget(ModelSelect2Widget):
    search_fields = ['title__icontains', 'first_author__icontains',]

class RelationWidget(ModelSelect2Widget):
    search_fields = ['name__name__icontains', 'location__name__icontains', 'qualifier__qualifier_name__name__icontains', 'qualifier__stratigraphic_qualifier__name__icontains',]

class ReferenceStructuredNameForm(forms.ModelForm):
    class Meta:
        model = Relation
        fields = ('is_active',)

    is_active = forms.IntegerField(       # At least one field needed in ModelForm although this is not needed in the actual input
        initial=1
        ,widget=forms.HiddenInput()
    )
    name_id = forms.IntegerField(       # A hidden input for internal use
        widget=forms.HiddenInput()
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w3-input w3-border',
                'readonly':'readonly',
            }
        )
    )
    qualifier = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w3-input w3-border',
                'readonly':'readonly',
            }
        )
    )
    location = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w3-input w3-border',
                'readonly':'readonly',
            }
        )
    )

#class ReferenceRelationForm(forms.ModelForm):
#    class Meta:
#        model = Relation
#        fields = ('name_one', 'name_two', 'belongs_to',)
#        widgets = {'name_one': RelationWidget, 'name_two': RelationWidget,}

class ReferenceRelationForm(forms.ModelForm):
    class Meta:
        model = Relation
        fields = ('is_active', 'belongs_to',)

    is_active = forms.IntegerField(       # At least one field needed in ModelForm although this is not needed in the actual input
        initial=1
        ,widget=forms.HiddenInput()
    )

    name_id = forms.IntegerField(       # A hidden input for internal use
        widget=forms.HiddenInput()
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w3-input w3-border',
                'readonly':'readonly',
            }
        )
    )
    qualifier = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w3-input w3-border',
                'readonly':'readonly',
            }
        )
    )
    location = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w3-input w3-border',
                'readonly':'readonly',
            }
        )
    )

class RelationForm(forms.ModelForm):
    class Meta:
        model = Relation
        fields = ('name_one', 'name_two', 'belongs_to', 'reference',)
        widgets = {'name_one': RelationWidget, 'name_two': RelationWidget, 'reference': ReferenceWidget, }

# For StructuredNameForm:
class LocationWidget(ModelSelect2Widget):
    search_fields = ['name__icontains',]

# For StructuredNameForm:
class NameWidget(ModelSelect2Widget):
    search_fields = ['name__icontains',]

# For StructuredNameForm:
class QualifierWidget(ModelSelect2Widget):
    search_fields = ['qualifier_name__name__icontains', 'stratigraphic_qualifier__name__icontains',]

class StructuredNameForm(forms.ModelForm):
    class Meta:
        model = StructuredName
        fields = ('name', 'qualifier', 'location', 'reference', 'remarks')
        widgets = {'location': LocationWidget, 'name': NameWidget, 'qualifier': QualifierWidget, 'reference': ReferenceWidget, }

class StratigraphicQualifierForm(forms.ModelForm):

    class Meta:
        model = StratigraphicQualifier
        fields = ('name',)


class TimeSliceForm(forms.ModelForm):

    class Meta:
        model = TimeSlice
        fields = ('scheme', 'order', 'name')
