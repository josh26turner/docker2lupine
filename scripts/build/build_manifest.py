import json
import subprocess
import os
import sys

from manifest import Manifest, Runtime, LinuxConf

manifest_out = 'manifestout/'


def inspect_docker_image(docker_image):
    os.system('docker pull {} 2>/dev/null'.format(docker_image))
    docker_json = subprocess.check_output(['docker', 'inspect', docker_image])
    return json.loads(docker_json)[0]


def import_module_by_path(path):
    name = os.path.splitext(os.path.basename(path))[0]
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_linux_options():
    load_options = import_module_by_path('scripts/host/strace2config/load_options.py')
    options = load_options.get_all_options()
    linux_conf = []
    init_conf = []
    
    for option in options:
        linux_conf += option.product.kernel or []
        init_conf += option.product.init or []

    return sorted(linux_conf), sorted(init_conf)


def dump_fs(image_name, skip_fs_dump, output) -> str:
    tar = output + '.tar'
    if not skip_fs_dump:
        docker_id = subprocess.check_output(['docker', 'create', image_name]).decode('utf-8').replace('\n', '')
        os.system('docker export {id} > {tarball}'.format(id=docker_id, tarball=tar))
        os.system('docker rm {} > /dev/null'.format(docker_id))
    return tar


def build_manifest(docker_obj, skip_fs_dump, kml, output, envs, cmd, init) -> Manifest:
    manifest = Manifest()

    manifest.runtime.entry = (docker_obj['Config']['Entrypoint'] or []) + (docker_obj['Config']['Cmd'] or []) + cmd
    manifest.runtime.envs = docker_obj['Config']['Env'] + envs
    manifest.runtime.working_directory = docker_obj['Config']['WorkingDir']

    manifest.linux_configuration.options, manifest.runtime.enabled_init_options = get_linux_options()
    if init is not None:
        manifest.runtime.enabled_init_options = init
    
    manifest.linux_configuration.kml = kml

    manifest.filesystem = dump_fs(docker_obj['RepoTags'][0], skip_fs_dump, output)

    return manifest
    

if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser(epilog='Run from the Lupine root directory')

    parser.add_argument('docker_image')
    parser.add_argument('docker_tag', default='latest', nargs='?')
    parser.add_argument('--output')
    parser.add_argument('--skip_fs_dump', action='store_true', help='just remake the manifest')
    parser.add_argument('--no_kml', action='store_true', help='disable KML in the Lupine image')
    parser.add_argument('--envs', default=[], nargs='+', help='environment variables to add to the manifest')
    parser.add_argument('--cmd', help='comma seperated list of args to append to the command')
    parser.add_argument('--init', default=None, nargs='+', help='init options to enable')

    args = parser.parse_args()

    if not os.path.exists(manifest_out):
        os.mkdir(manifest_out)

    output = manifest_out + (args.output or (args.docker_image.replace('/', '-') + '-' + args.docker_tag))

    docker_obj = inspect_docker_image(args.docker_image + ':' + args.docker_tag)
    manifest = build_manifest(docker_obj, args.skip_fs_dump, not args.no_kml, output, args.envs, args.cmd.split(',') if args.cmd else [], args.init)

    with open(output + '.json', 'w') as out_file:
        json.dump(manifest, out_file, default=lambda o: o.__dict__, indent=4,)
        print(output + '.json')
