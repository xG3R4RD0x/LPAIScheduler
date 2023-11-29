from dateutil import parser
from datetime import datetime, timedelta
from NLP import problem_data as pd


def extract_dates(dates: list):
    date_list = []
    if type(dates) == str:
        dates = [dates]

    for date in dates:
        if type(date) == list:
            date_range = []
            for d in date:
                if type(d) != datetime:
                    parsed_date = parser.parse(d, fuzzy=True)
                date_range.append(parsed_date)
            date_list.append(date_range)
        else:
            if type(date) != datetime:
                date = parser.parse(date, fuzzy=True)
            date_list.append(date)
    date_list = process_dates(date_list)

    return date_list


def process_dates(date_list: list):
    result_dates = []

    for item in date_list:
        if isinstance(item, list):  # If it is a list, it is a range of dates
            start_date, end_date = item  # Extract start and end dates from the range

            # Generate all dates in the range and add them to a list
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)

            # Add the list of date range to the result
            result_dates.append(date_range)
        elif isinstance(item, datetime):  # If it is a datetime object, it is an individual date
            result_dates.append(item)

    return result_dates


def generate_total_time_datetime_list(ProblemData: pd):

    start_date = extract_dates(
        ProblemData.data["hard_constraints"]["start_date"])
    total_days = ProblemData.data["hard_constraints"]["total_time"]
    date_list = [start_date[0] + timedelta(days=d) for d in range(total_days)]

    return date_list


def generate_dates_response_string(date_list: list):
    response = "Thanks for your input, I will take in mind that you won't be able to study on the following dates:\n"
    for d in date_list:
        if type(d) == list:
            dates_str = "from "+d[0] + "to "+d[1]
            response += dates_str+"\n"
        else:
            response += d+"\n"
    response


def flatten_list(list):
    flat_list = []
    for sub_list in list:
        if type(sub_list) == list:
            flat_list.extend(sub_list)
        else:
            flat_list.append(sub_list)
    return flat_list


# TODO realizar función para extraer horas
# necesito igual una función que me identifique a qué hora es cual hora para los constraits de horas
# esta función debe trabajar con el dato de la duración de la hora del problem data

# TODO hacer que el serializer arme el numero de horas basado en la duración de las horas y cuantas deben ser por día
