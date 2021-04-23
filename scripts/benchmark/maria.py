import mariadb
import time

from statistics import mean, pvariance


def run_bench(addr: str, itr: int = 20) -> list[float]:
    try:
        conn = mariadb.connect(
            user='root',
            password='pass',
            host=addr)

        cur = conn.cursor()

        res = []

        for _ in range(itr):
            t = time.perf_counter()
            cur.execute('SELECT BENCHMARK(100000000,ENCODE(\'hello\',\'goodbye\'));')
            res.append(time.perf_counter() - t)

        conn.close()

        return res
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        exit(1)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(epilog='Run from Lupine root directory')

    parser.add_argument('--docker', help='Docker instance base url')
    parser.add_argument('--lupine', help='Lupine instance base url')

    args = parser.parse_args()

    print('platform: mean variance')
    print('measured in seconds, lower better')

    print('docker:', end=' ', flush=True)
    res = run_bench(args.docker)
    print(round(mean(res), 4), round(pvariance(res), 4))

    print('lupine:', end=' ', flush=True)
    res = run_bench(args.lupine)
    print(round(mean(res), 4), round(pvariance(res), 4))
    