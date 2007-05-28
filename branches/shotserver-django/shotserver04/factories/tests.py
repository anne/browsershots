from psycopg import IntegrityError, ProgrammingError, DatabaseError
from unittest import TestCase
from django.db import transaction
from django.contrib.auth.models import User
from shotserver04.platforms.models import Architecture
from shotserver04.platforms.models import Platform, OperatingSystem
from shotserver04.factories.models import Factory, ScreenSize, ColorDepth


class FactoriesTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create()
        self.architecture = Architecture.objects.create()
        self.platform = Platform.objects.create()
        self.operating_system = OperatingSystem.objects.create(
            platform=self.platform)
        self.factory = Factory.objects.create(
            name='factory',
            admin=self.user,
            architecture=self.architecture,
            operating_system=self.operating_system)
        self.size_640 = ScreenSize.objects.create(
            factory=self.factory, width=640, height=480)
        self.size_800 = ScreenSize.objects.create(
            factory=self.factory, width=800, height=600)
        self.size_1024 = ScreenSize.objects.create(
            factory=self.factory, width=1024, height=768)
        self.depth_16 = ColorDepth.objects.create(
            factory=self.factory, bits_per_pixel=16)
        self.depth_24 = ColorDepth.objects.create(
            factory=self.factory, bits_per_pixel=24)

    def tearDown(self):
        self.depth_16.delete()
        self.depth_24.delete()
        self.size_640.delete()
        self.size_800.delete()
        self.size_1024.delete()
        self.factory.delete()
        self.operating_system.delete()
        self.platform.delete()
        self.architecture.delete()
        self.user.delete()

    def testFactoryName(self):
        self.factory.name = 'factory'
        self.factory.save()
        self.assertEqual(len(Factory.objects.filter(name='factory')), 1)

    def testFactoryNameEmpty(self):
        try:
            self.factory.name = ''
            self.assertRaises(IntegrityError, self.factory.save)
        finally:
            transaction.rollback()

    def testFactoryNameInvalid(self):
        try:
            self.factory.name = '-'
            self.assertRaises(IntegrityError, self.factory.save)
        finally:
            transaction.rollback()

    def testFactoryCreateDuplicate(self):
        try:
            self.assertRaises(IntegrityError, Factory.objects.create,
                              name='factory', admin=self.user,
                              architecture=self.architecture,
                              operating_system=self.operating_system)
        finally:
            transaction.rollback()

    def testFactoryCreateEmpty(self):
        try:
            self.assertRaises(IntegrityError, Factory.objects.create,
                              admin=self.user,
                              architecture=self.architecture,
                              operating_system=self.operating_system)
        finally:
            transaction.rollback()

    def testFactoryCreateInvalid(self):
        try:
            self.assertRaises(IntegrityError, Factory.objects.create,
                              name='-', admin=self.user,
                              architecture=self.architecture,
                              operating_system=self.operating_system)
        finally:
            transaction.rollback()

    def testScreenSize(self):
        queryset = self.factory.screensize_set
        self.assertEqual(len(queryset.all()), 3)
        self.assertEqual(len(queryset.filter(width=800)), 1)
        self.assertEqual(len(queryset.filter(width__exact=800)), 1)
        self.assertEqual(len(queryset.filter(width__gte=800)), 2)
        self.assertEqual(len(queryset.filter(width__lte=800)), 2)
        self.assertEqual(len(queryset.filter(width__gt=800)), 1)
        self.assertEqual(len(queryset.filter(width__lt=800)), 1)

    def testScreenSizeDuplicate(self):
        try:
            self.assertRaises(IntegrityError, ScreenSize.objects.create,
                              factory=self.factory, width=800, height=600)
        finally:
            transaction.rollback()

    def testColorDepth(self):
        queryset = self.factory.colordepth_set
        self.assertEqual(len(queryset.all()), 2)

    def testColorDepthDuplicate(self):
        try:
            self.assertRaises(IntegrityError, ColorDepth.objects.create,
                              factory=self.factory, bits_per_pixel=24)
        finally:
            transaction.rollback()


class ForeignKeyTestCase(TestCase):

    def testInvalidArchitecture(self):
        try:
            self.assertRaises(DatabaseError, Factory.objects.create,
                              architecture_id=-1)
        finally:
            transaction.rollback()

    def testInvalidOperatingSystem(self):
        try:
            self.assertRaises(DatabaseError, Factory.objects.create,
                              operating_system_id=-1)
        finally:
            transaction.rollback()

    def testInvalidAdmin(self):
        try:
            self.assertRaises(DatabaseError, Factory.objects.create,
                              admin_id=-1)
        finally:
            transaction.rollback()

    def testInvalidFactoryForScreenSize(self):
        try:
            self.assertRaises(DatabaseError, ScreenSize.objects.create,
                              factory_id=-1, width=800, height=600)
        finally:
            transaction.rollback()

    def testInvalidFactoryForColorDepth(self):
        try:
            self.assertRaises(DatabaseError, ColorDepth.objects.create,
                              factory_id=-1, bits_per_pixel=24)
        finally:
            transaction.rollback()