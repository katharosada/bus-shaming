import django
#import cProfile

django.setup()

from busshaming.data_processing import process_realtime_dumps


if __name__ == '__main__':
    #cProfile.run('process_realtime_dumps.process_next(10)', filename='output.txt')
    process_realtime_dumps.process_next(10)
