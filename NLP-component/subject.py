class Subject:

    REQUIRED_FIELDS = ["name", "number_of_units"]

    def __init__(self):
        # Inicializa un diccionario con valores vacios
        self.data = {
            "name": None,
            "Number_of_units": None,
            "hours_per_unit": None
        }

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
