import django

django.setup()

from busshaming.data_processing import process_timetable_data
from busshaming.data_processing import update_stop_sequences


if __name__ == '__main__':
    process_timetable_data.fetch_and_process_timetables()
    update_stop_sequences.update_all_stop_sequences()
