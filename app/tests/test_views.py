from django.apps import AppConfig
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission

class IndexViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

class BinningViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/binning/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'binning.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('binning'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'binning.html')

class HelpMainViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/help')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('help-main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help.html')

class HelpFaqViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/help/faq')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_faq.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('help-faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_faq.html')

class HelpDatabaseStructureViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/help/database-structure')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_database_structure.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('help-database-structure'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_database_structure.html')

class HelpStructureOfBinningAlgorithmViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/help/structure-of-binning-algorithm')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_structure_of_binning_algorithm.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('help-structure-of-binning-algorithm'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help_structure_of_binning_algorithm.html')

class LocationListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/locations')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'location_list.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('location-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'location_list.html')

class LocationAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_location')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('location-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('location-new'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_if_logged_in_and_authorized(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('location-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'location_edit.html')

class NameListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'name_list.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('name-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'name_list.html')

class NameAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_name')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('name-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('name-new'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_if_logged_in_and_authorized(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('name-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'name_edit.html')

class QualifierListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/qualifiers')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qualifier_list.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('qualifier-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qualifier_list.html')

class QualifierAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_qualifier')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('qualifier-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('qualifier-new'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_if_logged_in_and_authorized(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('qualifier-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qualifier_edit.html')

class QualifierNameListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/qualifier_names')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('qualifiername-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qualifiername_list.html')

class QualifierNameAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_qualifiername')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('qualifiername-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('qualifiername-new'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_if_logged_in_and_authorized(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('qualifiername-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qualifiername_edit.html')

class ReferenceListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/references')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reference_list.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('reference-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reference_list.html')

class ReferenceAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_reference')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('reference-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('reference-new'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_if_logged_in_and_authorized(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('reference-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reference_edit.html')

class RelationListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/relations')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'relation_list.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('relation-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'relation_list.html')

class RelationAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_relation')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('relation-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('relation-new'))
        self.assertEqual(response.status_code, 403)

    # todo: test_correct_template_if_logged_in_and_authorized

class StratigraphicQualifierListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/stratigraphic_qualifiers')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stratigraphic_qualifier_list.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('stratigraphic-qualifier-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stratigraphic_qualifier_list.html')

class StratigraphicQualifierAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_stratigraphicqualifier')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('stratigraphic-qualifier-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('stratigraphic-qualifier-new'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_if_logged_in_and_authorized(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('stratigraphic-qualifier-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stratigraphic_qualifier_edit.html')

class StructuredNameListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/structured_names')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'structuredname_list.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('structuredname-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'structuredname_list.html')

class StructuredNameAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_structuredname')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('structuredname-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('structuredname-new'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_if_logged_in_and_authorized(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('structuredname-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'structuredname_edit.html')

class TimeSliceListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/rnames/timeslices')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'timeslice_list.html')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('timeslice-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'timeslice_list.html')

class TimeSliceAddViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        admgrp, created = Group.objects.get_or_create(name='data_admin')
        perm = Permission.objects.get(codename='add_timeslice')
        admgrp.permissions.add(perm)
        admgrp.user_set.add(test_user2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('timeslice-new'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_unauthorized(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('timeslice-new'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_if_logged_in_and_authorized(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('timeslice-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'timeslice_edit.html')
