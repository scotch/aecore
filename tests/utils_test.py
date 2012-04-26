from aecore.test_utils import BaseTestCase
from aecore import utils


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class TestImportStringClass(object):
    pass

class TestImportClass(BaseTestCase):
    def test_import_class(self):
        klass = utils.import_class('utils_test.TestImportStringClass')
        self.assertEqual(klass, TestImportStringClass)
