import django

django.setup()

from busshaming.data_processing import update_stop_sequences


if __name__ == '__main__':
    update_stop_sequences.update_all_stop_sequences()
