from socket_server import LupineServer, DEFAULT_IP, DEFAULT_PORT, STRACE_OUT
from strace2config.main import get_min_config

import fnmatch
import json
import os
import time

MANIFEST_OUT = 'manifestout/'
FIRECRACKER_OUT='firecrackerout/'
HOST_DIR=os.path.dirname(os.path.abspath(__file__))


def update_config(lupine: str) -> None:
    print('Parsing strace files')
    init, kernel = get_min_config(list(map(lambda file: STRACE_OUT + file, filter(lambda file: fnmatch.fnmatch(file, lupine + '.*'), os.listdir(STRACE_OUT)))))

    print('Writing new config')
    manifest_name = MANIFEST_OUT + lupine + '.json'
    with open(manifest_name, 'r') as manifest_file:
        manifest = json.load(manifest_file)

        manifest['linux_configuration']['options'] = kernel
        manifest['runtime']['enabled_init_options'] = init

        with open(manifest_name, 'w') as manifest_file:
            json.dump(manifest, manifest_file, default=lambda o: o.__dict__, indent=4)


def extract_strace(lupine: str) -> None:        
    os.system('sudo mount rootfsbuild/{lupine}.ext4 /mnt'.format(lupine=args.lupine))
    os.system('cp /mnt/{lupine}.* straceout'.format(lupine=args.lupine))
    os.system('sudo umount /mnt')

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
    os.system('sudo {host_dir}/firecracker-run.sh {lupine} "{init}" &> {out}{lupine}.log &'.format(
        lupine=args.lupine,
        out=FIRECRACKER_OUT,
        init='/init strace' if args.strace else '/init',
        host_dir=HOST_DIR))

    while os.system('ip addr show tap100 > /dev/null 2>&1') != 0:
        pass

    lupine_server = LupineServer()
    lupine_server.start_server(ip_addr=args.ip, port=args.port)

    if args.strace:
        print('Run tests or perform a regular usage of the service...')

    input('Press enter when finished')
    lupine_server.set_done(True)
    lupine_server.wait_for_finish()

    while not os.system('pgrep -x firecracker > /dev/null'):
        pass

    if args.strace:
        extract_strace(args.lupine)
        update_config(args.lupine)
