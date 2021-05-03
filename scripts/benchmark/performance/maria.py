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

    parser.add_argument('ip_address', help='MariaDB IP address')
    parser.add_argument('itr', default=50, type=int, help='number of iterations', nargs='?')

    args = parser.parse_args()
    res = run_bench(args.ip_address, itr=args.itr)
    print(str(round(mean(res), 4)) + ',' + str(round(pvariance(res) ** 0.5, 4)))
