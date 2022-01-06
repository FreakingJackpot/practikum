from tempfile import NamedTemporaryFile

from django.test import TestCase
from catalog.models import Product, Category, AttributeValue
from catalog.services.import_products_from_excel import ExcelProductImporter
from catalog.services.export_products import ExcelProductExporter


class ImportProductsTestCase(TestCase):

    def test_import(self):
        # insert
        with open('./catalog/fixtures/test.xlsx', 'rb') as f:
            importer = ExcelProductImporter(f)
            importer.run()

        categories_count = Category.objects.count()
        products_count = Product.objects.count()
        value = AttributeValue.objects.filter(value='Ширина: 90 см X Высота: 190 см X Глубина: 40 см').exists()

        self.assertEqual(2, categories_count)
        self.assertEqual(11, products_count)
        self.assertTrue(value)

        # update
        with open('./catalog/fixtures/test2.xlsx', 'rb') as f:
            importer = ExcelProductImporter(f)
            importer.run()

        value = AttributeValue.objects.filter(value='Ширина: 91 см X Высота: 190 см X Глубина: 40 см').exists()

        self.assertTrue(value)


class ExportProductsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open('./catalog/fixtures/test.xlsx', 'rb') as f:
            importer = ExcelProductImporter(f)
            importer.run()

    def test_export(self):
        with NamedTemporaryFile(prefix='mebel', suffix='xlsx') as tmp:
            exporter = ExcelProductExporter()
            wb = exporter.run()
            self.assertEqual(len(wb.get_sheet_names()), 2)
            wb.save(tmp.name)
