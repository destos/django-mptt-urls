from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.client import RequestFactory

import mox
from model_mommy import mommy

from mptt_urls import url_mptt, superroot
from mptt_urls.views import process_url
from test_app.gallery.models import Category, Photo


class InvalidConfigTest(TestCase):
    def setUp(self):
        self.mox = mox.Mox()
        self.request = RequestFactory().get('')
        level1 = mommy.make(Category, slug='level1')
        level2 = mommy.make(Category, slug='level2', parent=level1)
        self.photo = mommy.make(Photo, slug='photo1', parent=level2)

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_model_slug_fields_required(self):
        # test leaf being required
        settings = {
            'node': {
                'model': 'test_app.gallery.models.Category'
            }
        }
        with self.assertRaisesRegexp(
                ImproperlyConfigured, r'^\'leaf\' settings cannot'):
            process_url(self.request, 'level1/level2/', settings)

        # test node being required
        settings = {
            'leaf': {
                'model': 'test_app.gallery.models.Photo'
            }
        }
        with self.assertRaisesRegexp(
                ImproperlyConfigured, r'^\'node\' settings cannot'):
            process_url(self.request, 'level1/level2/', settings)

    def test_template_view_redundant(self):
        settings = {
            'node': {
                'model': 'test_app.gallery.models.Category',
                'template': 'a.template',
                'view': 'a.view'
            },
            'leaf': {
                'model': 'test_app.gallery.models.Photo'
            },
        }
        with self.assertRaisesRegexp(
                ImproperlyConfigured, r'"template" and "view" values cannot be'
                                      ' used simultaneously'):
            process_url(self.request, 'level1/level2/', settings)

    def test_template_view_leaf_redeundant(self):
        settings = {
            'node': {
                'model': 'test_app.gallery.models.Category',
            },
            'leaf': {
                'model': 'test_app.gallery.models.Photo',
                'template': 'a.template',
                'view': 'a.view'
            },
        }
        with self.assertRaisesRegexp(
                ImproperlyConfigured, r'"template" and "view" values cannot be'
                                      ' used simultaneously'):
            process_url(self.request, 'level1/level2/photo1', settings)

    def test_template_view_missing(self):
        settings = {
            'node': {
                'model': 'test_app.gallery.models.Category'
            },
            'leaf': {
                'model': 'test_app.gallery.models.Photo'
            }
        }
        with self.assertRaisesRegexp(
                ImproperlyConfigured, r'"template" or "view"'):
            process_url(self.request, 'level1/level2/', settings)
