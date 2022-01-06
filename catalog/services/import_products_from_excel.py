from io import BytesIO

from openpyxl import load_workbook
from catalog.models import Category, Product, Color, Vendor, Attribute, AttributeValue


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

        attributes = self._get_attributes(labels, category)

        for row in rows:
            item = {}.fromkeys(labels, None)

            for cell in enumerate(row):
                if cell[0] < len(labels):
                    item[labels[cell[0]]] = cell[1].value

            # Проверка на удаленное значение
            if item == {}.fromkeys(labels, None):
                break

            manufacturer = self.__get_model_obj(Vendor, name=item['Производитель'])
            colors = self._get_colors(item)
            product = self._create_or_update_product(item, category, manufacturer, colors, products_to_update)
            for attribute in attributes:
                self._create_or_update_attr_value(product, attribute, item, values_to_create, values_to_update)

        Product.objects.bulk_update(products_to_update,
                                    ('price', 'vendor', 'description', 'discount_price', 'active'))

        AttributeValue.objects.bulk_create(values_to_create)
        AttributeValue.objects.bulk_update(values_to_update, ('value',))

    def _get_attributes(self, labels, category):
        attributes_labels = set(filter(lambda x: x not in self.PRODUCT_FIELDS, labels))
        attributes_map = {attr.name: attr for attr in Attribute.objects.filter(category=category)}

        to_delete = set(attributes_map.keys()) - set(attributes_labels)
        for label in to_delete:
            AttributeValue.objects.filter(attribute__category=category, attribute=attributes_map[label]).delete()
            category.attribute.remove(attributes_map[label])
            attributes_map.pop(label)

        to_create = set(attributes_labels) - set(attributes_map.keys())
        new_attrs = []
        for label in to_create:
            attr, _ = Attribute.objects.get_or_create(name=label)
            attributes_map[label] = attr
            new_attrs.append(attr)
        category.attribute.add(*new_attrs)

        return attributes_map.values()

    def _create_or_update_product(self, item, category, manufacturer, colors, products_to_update):
        product = Product.objects.prefetch_related('color').filter(vendor_code=item['Артикул']).first()
        if product:
            updates = self._check_product_attr_change(product, item, manufacturer)
            product.color.add(*colors)
            if updates:
                products_to_update.append(product)
        else:
            defaults = {'vendor_code': item['Артикул'], 'name': item['Название'], 'category': category,
                        'description': item['Описание'],
                        'price': item['Цена'], 'discount_price': item['Цена со скидкой'],
                        'active': True if item['Активен'] == 'Да' else False, 'vendor': manufacturer}
            product = Product.objects.create(**defaults)
            product.color.add(*colors)

        return product

    def _check_product_attr_change(self, product, item, manufacturer):
        updates = False
        if item['Описание'] != product.description:
            product.description = item['Описание']
            updates = True
        if item['Цена'] != product.price:
            product.price = item['Цена']
            updates = True
        if item['Цена со скидкой'] != product.discount_price:
            product.discount_price = item['Цена со скидкой']
            updates = True
        activity = True if item['Активен'].capitalize() == 'Да' else False
        if activity != product.active:
            product.active = activity
            updates = True
        if manufacturer != product.vendor:
            product.vendor = manufacturer
            updates = True
        return updates

    def _create_or_update_attr_value(self, product, attribute, item, values_to_create, values_to_update):
        value = item.get(attribute.name, None)

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
        for name in item['Цвет'].split('/'):
            colors.append(self.__get_model_obj(Color, name=name.strip()))
        return colors
