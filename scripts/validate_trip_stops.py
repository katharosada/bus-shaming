import django

django.setup()

from busshaming.data_processing import update_stop_sequences


if __name__ == '__main__':
    import sys
    route_id = sys.argv[1]

    update_stop_sequences.verify_stop_sequences(route_id)
