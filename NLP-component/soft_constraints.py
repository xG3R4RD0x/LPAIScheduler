class no_study_day:
    def __init__(self):
        self.data = {
            "day": None,  # Has to be a string with the Name of the day
            "dates": None,
            "repeating_event": False
        }


class no_study_hours:
    def __init__(self):
        self.data = {
            "day": None,
            "hour_range": None,  # Has to be a range of hours
            "repeating_event": False
        }
