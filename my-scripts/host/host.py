from http_server import LupineServer, DEFAULT_IP, DEFAULT_PORT

import os
import time

FIRECRACKER_OUT='firecrackerout/'

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(epilog='Run from Lupine root directory')

    parser.add_argument('lupine', help='Built image to run')
    parser.add_argument('-ip', default=DEFAULT_IP)
    parser.add_argument('-p', default=DEFAULT_PORT)

    args = parser.parse_args()

    if not os.path.exists(FIRECRACKER_OUT):
        os.mkdir(FIRECRACKER_OUT)

    print('Starting lupine in firecracker')
    os.system('./my-scripts/host/firecracker-run.sh {lupine} "/init strace" &> {out}{lupine}.log &'.format(lupine=args.lupine, out=FIRECRACKER_OUT))

    time.sleep(3) # Wait for machine start

    os.system('./my-scripts/host/net_setup.sh')

    print('Starting server')
    lupine_server = LupineServer()
    lupine_server.start_server(ip_addr=args.ip, port=args.p)

    print('Run tests or perform a regular usage of the service...')
    input('Press enter when completed')
    lupine_server.set_done(True)

    print('Getting strace files')
    lupine_server.wait_for_finish()
    lupine_server.kill_server()
