from django.test import TestCase
from django.core.files import File
from catalog.models import Product, Category, AttributeValue
from catalog.services.import_products_from_excel import ExcelProductImporter


class ImportProductsTestCase(TestCase):

    def test_import(self):
        from os import getcwd
        print(getcwd())
        with open('./catalog/fixtures/test.xlsx', 'rb') as f:
            importer = ExcelProductImporter(f)
            importer.run()

        categories_count = Category.objects.count()
        products_count = Product.objects.count()
        value = AttributeValue.objects.filter(value='Ширина: 90 см X Высота: 190 см X Глубина: 40 см').first()

        self.assertEqual(2, categories_count)
        self.assertEqual(11, products_count)
        self.assertTrue(value)
        self.assertEqual(1, value.product_id)
