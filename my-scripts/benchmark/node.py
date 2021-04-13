import json
import requests

from statistics import mean, pvariance


def run_bench(base_url):
    auth_token = ""
    try:
        auth_token = json.loads(requests.post(base_url + '/register', data={'username': 'user', 'password': '1234'}).text)['token']
    except KeyError:
        auth_token = json.loads(requests.post(base_url + '/login', data={'username': 'user', 'password': '1234'}).text)['token']


    trip = json.loads(requests.post(base_url + '/trip', 
        data={'name': 'trip'},
        headers={'Authorization': 'Bearer {}'.format(auth_token)})
        .text)

    n = 30

    times = [requests.post(base_url + '/images',
        data={'tripId': trip['id'], 
            'metadata': [json.dumps({'date': '1/1/2000', 'location': 'France'}) for x in range(n)]
        },
        headers={'Authorization': 'Bearer {}'.format(auth_token)},
        files=[('images', open('my-scripts/benchmark/bench_images/IMG.jpg', 'rb')) for x in range(n)]
    ).elapsed.total_seconds() for x in range(10)]

    print(mean(times), pvariance(times))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(epilog='Run from Lupine root directory')

    parser.add_argument('--docker', help='Docker instance base url')
    parser.add_argument('--lupine', help='Lupine instance base url')
    parser.add_argument('--native', help='Native instance base url')

    args = parser.parse_args()

    print('docker:', end=' ', flush=True)
    run_bench(args.docker)

    print('lupine:', end=' ', flush=True)
    run_bench(args.lupine)

    print('native:', end=' ', flush=True)
    run_bench(args.native)
