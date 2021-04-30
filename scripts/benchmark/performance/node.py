import requests

from statistics import mean, pvariance


def run_bench(base_url, itr=10):
    times = [requests.get(base_url).elapsed.total_seconds() for x in range(itr)]

    print(str(round(mean(times), 4)) + ',' + str(round(pvariance(times) ** 0.5, 4)))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(epilog='Run from Lupine root directory')

    parser.add_argument('ip_address', help='node IP address')
    parser.add_argument('itr', default=10, type=int, help='number of iterations', nargs='?')

    args = parser.parse_args()
    res = run_bench('http://' + args.ip_address + ':3000/', itr=args.itr)
