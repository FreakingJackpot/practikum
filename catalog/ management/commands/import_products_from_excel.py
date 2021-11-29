from io import BytesIO
from openpyxl import load_workbook
from catalog.models import Category, Product, Color, Manufacturer, Attribute, AttributeValue


class ExcelProductImporter:
    PRODUCT_FIELDS = ('Артикул', 'Название', 'Описание', 'Цена', 'Наличие', 'Производитель', 'Цвет')

    def __init__(self, file):
        self.file = file

    def main(self):
        wb = load_workbook(filename=BytesIO(self.file.read()), read_only=True)
        categories = Category.objects.filter(name__in=wb.get_sheet_names())

        for category in categories:
            sheet = wb.get_sheet_by_name(category.name)
            error = self.__process_sheet(sheet, category)
            if error:
                return error

    @staticmethod
    def __get_model_obj(model, **kwargs):
        obj = model.objects.get_or_create(**kwargs)
        return obj

    def __process_sheet(self, sheet, category):
        products_to_create = []
        products_to_update = []
        values_to_create = []
        values_to_update = []
        product_colors = {}
        labels = []

        for row in enumerate(sheet.rows):
            item = {} if not labels else {}.fromkeys(labels, None)
            for cell in enumerate(row[1]):
                if row[0] and cell[0] < len(labels):
                    item[labels[cell[0]]] = cell[1].value
                elif not row[0]:
                    labels.append(cell[1].value.strip())
            # Проверка на удаленное значение
            if item == {}.fromkeys(labels, None):
                break

            if row[0]:
                manufacturer = self.__get_model_obj(Manufacturer, name=item['Производитель'])

                colors = []
                for name in item['Цвет'].split('/'):
                    colors.append(self.__get_model_obj(Color, name=name))

                product = Product.objects.filter(name=item['Название'], category=category).first()
                if product:
                    product.description = item['Описание']
                    product.price = item['Цена']
                    product.stock = item['Наличие']
                    product.manufacturer = manufacturer
                    product.color.add(*colors)
                    products_to_update.append(product)
                else:
                    defaults = {'name': item['Название'], 'category': category, 'description': item['Описание'],
                                'price': item['Цена'], 'stock': item['Наличие'],
                                'manufacturer': manufacturer}
                    product = Product(**defaults)
                    product_colors[product] = colors
                    products_to_create.append(product)

                for attribute in attributes:
                    if item[attribute.name] is not None:
                        value = str(item[attribute.name]).split(' ')
                        defaults = {'product': product, 'attribute': attribute, 'value': value[0],
                                    'label': value[-1] if len(value) > 1 else ''}
                    else:
                        value = item[attribute.name]
                        defaults = {'product': product, 'attribute': attribute, 'value': value, 'label': ''}

                    queryset = AttributeValue.objects.filter(product=product, attribute=attribute)
                    if queryset:
                        attribute_value = queryset.first()
                        attribute_value.value = defaults['value']
                        attribute_value.label = defaults['label']
                        values_to_update.append(attribute_value)
                    else:
                        values_to_create.append(AttributeValue(**defaults))

            else:
                attribute_names = [i for i in labels if i.strip() not in self.product_fields]
                queryset = Attribute.objects.filter(name__in=attribute_names, category=category)

                attributes = []
                try:
                    for attribute in queryset:
                        if attribute.name not in attribute_names:
                            raise ValueError
                        attributes.append(attribute)
                except ValueError:
                    return f"Аттрибута \"{attribute.name}\" нету в базе данных"

                del attribute_names

        Product.objects.bulk_create(products_to_create)
        Product.objects.bulk_update(products_to_update, ('description', 'price', 'manufacturer'))

        for product in product_colors:
            product.color.add(*product_colors[product])

        AttributeValue.objects.bulk_create(values_to_create)
        AttributeValue.objects.bulk_update(values_to_update, ('value', 'label'))
