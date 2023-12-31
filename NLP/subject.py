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

    def get_fields(self):
        fields = Subject.REQUIRED_FIELDS
        fields.pop(0)
        return fields

    def get_key(self, key):
        return self.data[key]

    def validate_data(self):
        # Verifica si los campos obligatorios de los subjects
        missing_fields = []
        data = self.data

        for field in Subject.REQUIRED_FIELDS:
            if data[field] is None:
                missing_fields.append(field)
        if not missing_fields:
            return True
        else:
            return missing_fields

    def update_info(self, info: dict):
        for key, value in info:
            self.data[key] = value
