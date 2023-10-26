class no_study_day:
    REQUIRED_FIELDS = ["dates", "constraint_type"]

    def __init__(self):
        self.data = {
            "day": None,  # Has to be a string with the Name of the day
            "dates": None,
            "repeating_event": False,
            "constraint_type": None
        }
        # la intención es que trate de leer el tipo de constraint directo desde el input
        # si no se logra se pregunta

    def validate_data(self):
        # Verifica si los campos obligatorios estan completos
        missing_fields = []
        data = self.data

        for field in no_study_day.REQUIRED_FIELDS:
            if data[field] is None:
                missing_fields.append(field)
                return missing_fields

        return True

    def get_key(self, key):
        return self.data[key]


class no_study_hours:
    REQUIRED_FIELDS = ["hour_range", "everyday", "constraint_type"]

    def __init__(self):
        self.data = {
            "dates": None,
            "hour_range": None,  # Has to be a range of hours
            "everyday": False,
            "constraint_type": None
        }

    def validate_data(self):
        # Verifica si los campos obligatorios estan completos
        missing_fields = []
        data = self.data

        for field in no_study_hours.REQUIRED_FIELDS:
            if data[field] is None:
                missing_fields.append(field)
                return missing_fields

        return True

    def get_key(self, key):
        return self.data[key]
