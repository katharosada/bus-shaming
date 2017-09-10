import django

django.setup()

from busshaming.data_processing import process_timetable_data


if __name__ == '__main__':
    process_timetable_data.fetch_and_process_timetables()
