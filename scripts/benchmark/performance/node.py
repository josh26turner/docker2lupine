import requests

from statistics import mean, pvariance


def run_bench(base_url):
    n = 10

    times = [requests.get(base_url).elapsed.total_seconds() for x in range(10)]

    print(mean(times), pvariance(times))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(epilog='Run from Lupine root directory')

    parser.add_argument('--docker', help='Docker instance base url')
    parser.add_argument('--lupine', help='Lupine instance base url')
    parser.add_argument('--native', help='Native instance base url')

    args = parser.parse_args()

    print('platform: mean variance')
    print('measured in seconds, lower better')

    print('docker:', end=' ', flush=True)
    run_bench(args.docker)

    print('lupine:', end=' ', flush=True)
    run_bench(args.lupine)
