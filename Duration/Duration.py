from datetime import datetime
from datetime import timedelta

def duration(start_date,end_date,start_time,end_time):
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    delta = d2 - d1
    FMT = '%H:%M:%S'
    tdelta = datetime.strptime(end_time, FMT) - datetime.strptime(start_time, FMT)
    if((start_time < end_time) and delta.days > 0):
        day = delta.days
        day = day-1
    else:
        day = delta.days
    tdelta = timedelta(
        days=day,
        seconds=tdelta.seconds,
        microseconds=tdelta.microseconds
    )
    return tdelta