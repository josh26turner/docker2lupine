from http_server import LupineServer, DEFAULT_IP, DEFAULT_PORT, STRACE_OUT
from strace2config.main import get_min_config

import fnmatch
import json
import os
import time

MANIFEST_OUT = 'manifestout/'
FIRECRACKER_OUT='firecrackerout/'
HOST_DIR=os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(epilog='Run from Lupine root directory')

    parser.add_argument('lupine', help='Built image to run')
    parser.add_argument('--ip', '-a', default=DEFAULT_IP)
    parser.add_argument('--port','-p', default=DEFAULT_PORT)
    parser.add_argument('--strace', '-s', action='store_true', help='debug to build minimal manifest')

    args = parser.parse_args()

    if not os.path.exists(FIRECRACKER_OUT):
        os.mkdir(FIRECRACKER_OUT)

    print('Starting lupine in firecracker')
    os.system('{host_dir}/firecracker-run.sh {lupine} "{init}" &> {out}{lupine}.log &'.format(
        lupine=args.lupine,
        out=FIRECRACKER_OUT,
        init='/init strace' if args.strace else '/init',
        host_dir=HOST_DIR))

    time.sleep(1) # Wait for machine start

    os.system('{}/net_setup.sh nat'.format(HOST_DIR))

    if args.strace:
        print('Starting server')
        lupine_server = LupineServer()
        lupine_server.start_server(ip_addr=args.ip, port=args.port)

        print('Run tests or perform a regular usage of the service...')
        input('Press enter when completed')
        lupine_server.set_done(True)

        print('Getting strace files')
        lupine_server.wait_for_finish()
        lupine_server.kill_server()

        print('Parsing strace files')
        init, kernel = get_min_config(list(map(lambda file: STRACE_OUT + file, filter(lambda file: fnmatch.fnmatch(file, args.lupine + '*'), os.listdir(STRACE_OUT)))))

        print('Writing new config')
        manifest_name = MANIFEST_OUT + args.lupine + '.json'
        with open(manifest_name, 'r') as manifest_file:
            manifest = json.load(manifest_file)

            manifest['linux_configuration']['options'] = kernel
            manifest['runtime']['enabled_init_options'] = init

            with open(manifest_name, 'w') as manifest_file:
                json.dump(manifest, manifest_file, default=lambda o: o.__dict__, indent=4)
