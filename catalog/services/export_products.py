from openpyxl import Workbook
from catalog.models import Category, Product


class ExcelProductExporter:
    PRODUCT_FIELDS = ('Артикул', 'Название', 'Производитель', 'Описание', 'Цена', 'Цена со скидкой', 'Цвет', 'Активен')

    def run(self):
        wb = Workbook(write_only=True)
        categories = Category.objects.prefetch_related('attribute').all()

        for category in categories:
            ws = wb.create_sheet(title=category.name)

            self._fill_work_sheet(ws, category)

        return wb

    def _fill_work_sheet(self, ws, category):
        products = Product.objects.prefetch_related('prod_attr_value__attribute', 'color').filter(category=category)
        labels = self._get_labels(category)
        ws.append(tuple(labels.keys()))

        for product in products:

            values = dict.fromkeys(range(len(labels)))
            values[0] = product.vendor_code
            values[1] = product.name
            values[2] = product.manufacturer.name
            values[3] = product.description
            values[4] = product.price
            values[5] = product.discount_price
            values[6] = '/'.join(color.name for color in product.color.all())
            values[7] = product.active

            for value in product.prod_attr_value.all():
                attr_name = value.attribute.name
                if attr_name in labels:
                    values[labels[attr_name]] = value.value
            ws.append(tuple(values[i] for i in range(len(labels))))

    def _get_labels(self, category):
        labels = {attr: i for i, attr in enumerate(self.PRODUCT_FIELDS)}
        attrs_labels = {attr.name: i for i, attr in enumerate(category.attribute.all(), len(self.PRODUCT_FIELDS))}
        labels.update(attrs_labels)

        return labels
