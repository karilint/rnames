from django.test import TestCase
from django.urls import reverse

class IndexViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

class NameListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('name-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'name_list.html')

class BinningViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/binning/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('binning'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'binning.html')

class HelpMainViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/help')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('help-main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help.html')

class HelpFaqViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/help/faq')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('help-faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_faq.html')

class HelpDatabaseStructureViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/help/database-structure')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('help-database-structure'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_database_structure.html')

class HelpStructureOfBinningAlgorithmViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/help/structure-of-binning-algorithm')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('help-structure-of-binning-algorithm'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_structure_of_binning_algorithm.html')

class ReferenceListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/references')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('reference-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reference_list.html')

class StructuredNameListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/structured_names')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('structuredname-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'structuredname_list.html')

class RelationListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/relations')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('relation-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'relation_list.html')

class LocationListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/locations')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('location-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'location_list.html')

class QualifierListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/qualifiers')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('qualifier-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qualifier_list.html')

class QualifierNameListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/qualifier_names')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('qualifiername-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qualifiername_list.html')

class StratigraphicQualifierListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/stratigraphic_qualifiers')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('stratigraphic-qualifier-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stratigraphic_qualifier_list.html')

class TimeSliceListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/timeslices')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('timeslice-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'timeslice_list.html')
