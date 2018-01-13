import sys
import django
django.setup()

from busshaming.data_processing import realtime_validator


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <route_id>')
        sys.exit(1)

    realtime_validator.validate_route(sys.argv[1])

