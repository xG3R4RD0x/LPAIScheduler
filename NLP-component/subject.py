class Subject:
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
