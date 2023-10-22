from dateutil import parser


def extract_dates(dates: list):
    date_list = []
    for date in dates:
        if type(date) == list:
            date_range = []
            for d in date:
                parsed_date = parser.parse(d, fuzzy=True)
                date_range.append(parsed_date)
            date_list.append(date_range)
        else:
            parsed_date = parser.parse(date, fuzzy=True)
            date_list.append(parsed_date)

    return date_list


# TODO realizar función para extraer horas
# necesito igual una función que me identifique a qué hora es cual hora para los constraits de horas
# esta función debe trabajar con el dato de la duración de la hora del problem data

# TODO hacer que el serializer arme el numero de horas basado en la duración de las horas y cuantas deben ser por día
