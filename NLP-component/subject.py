class Subject:

    REQUIRED_FIELDS = ["name", "number_of_units", "hours_per_unit"]

    def __init__(self, name: str):
        # Inicializa un diccionario con valores vacios
        self.data = {
            "name": name,
            "number_of_units": None,
            "hours_per_unit": None
        }

    def set_info(self, key, value):
        self.data[key] = value
        return True

    def get_info(self, key):
        return self.data.get(key)

    def get_data(self):
        return self.data

    def validate_data(self):
        # Verifica si los campos obligatorios de los subjects
        missing_fields = []
        data = self.data

        for field in Subject.REQUIRED_FIELDS:
            if data[field] is None:
                missing_fields.append(field)
                return missing_fields

        return True
