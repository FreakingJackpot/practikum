from io import BytesIO

from openpyxl import load_workbook
from catalog.models import Category, Product, Color, Manufacturer, Attribute, AttributeValue


class ExcelProductImporter:
    PRODUCT_FIELDS = ('Артикул', 'Название', 'Производитель', 'Описание', 'Цена', 'Цена со скидкой', 'Цвет', 'Активен')

    def __init__(self, file):
        self.file = file

    def run(self):
        wb = load_workbook(filename=BytesIO(self.file.read()), read_only=True)

        for category_name in wb.sheetnames:
            category = self.__get_model_obj(Category, name=category_name)
            sheet = wb[category.name]

            error = self.__process_sheet(sheet, category)
            if error:
                return error

    @staticmethod
    def __get_model_obj(model, **kwargs):
        obj, _ = model.objects.get_or_create(**kwargs)
        return obj

    def __process_sheet(self, sheet, category):
        products_to_update = []
        values_to_create = []
        values_to_update = []
        labels = []

        rows = iter(sheet.rows)
        row = next(rows)

        for cell in row:
            labels.append(cell.value.strip())

        attributes = self._get_attributes(labels)

        for row in rows:
            item = {}.fromkeys(labels, None)

            for cell in enumerate(row):
                if cell[0] < len(labels):
                    item[labels[cell[0]]] = cell[1].value

            # Проверка на удаленное значение
            if item == {}.fromkeys(labels, None):
                break

            manufacturer = self.__get_model_obj(Manufacturer, name=item['Производитель'])
            colors = self._get_colors(item)
            product = self._create_or_update_product(item, category, manufacturer, colors, products_to_update)
            for attribute in attributes:
                self._create_or_update_attr_value(product, attribute, item, values_to_create, values_to_update)

        Product.objects.bulk_update(products_to_update, ('description', 'price', 'manufacturer'))

        AttributeValue.objects.bulk_create(values_to_create)
        AttributeValue.objects.bulk_update(values_to_update, ('value',))

    def _get_attributes(self, labels):
        attributes = []
        attributes_labels = filter(lambda x: x not in self.PRODUCT_FIELDS, labels)
        for label in attributes_labels:
            attributes.append(self.__get_model_obj(Attribute, name=label))
        return attributes

    def _create_or_update_product(self, item, category, manufacturer, colors, products_to_update):
        product = Product.objects.filter(vendor_code=item['Артикул'], category=category).first()
        if product:
            product.vendor_code = item['Артикул']
            product.description = item['Описание']
            product.price = item['Цена']
            product.discount_price = item['Цена со скидкой']
            product.active = True if item['Активен'].capitalize() == 'Да' else False
            product.manufacturer = manufacturer
            product.color.add(*colors)
            products_to_update.append(product)
        else:
            defaults = {'vendor_code': item['Артикул'], 'name': item['Название'], 'category': category,
                        'description': item['Описание'],
                        'price': item['Цена'], 'discount_price': item['Цена со скидкой'],
                        'active': True if item['Активен'] == 'Да' else False, 'manufacturer': manufacturer}
            product = Product.objects.create(**defaults)
            product.color.add(*colors)

        return product

    def _create_or_update_attr_value(self, product, attribute, item, values_to_create, values_to_update):
        value = item[attribute.name]
        defaults = {'product': product, 'attribute': attribute, 'value': value}

        queryset = AttributeValue.objects.filter(product=product, attribute=attribute)
        if queryset:
            attribute_value = queryset.first()
            attribute_value.value = defaults['value']
            values_to_update.append(attribute_value)
        else:
            values_to_create.append(AttributeValue(**defaults))

    def _get_colors(self, item):
        colors = []
        for name in item['Цвет'].split('/').strip():
            colors.append(self.__get_model_obj(Color, name=name))
        return colors
