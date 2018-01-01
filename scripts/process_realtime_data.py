import django

django.setup()

from busshaming.data_processing import process_realtime_dumps


if __name__ == '__main__':
    process_realtime_dumps.process_next(10)
