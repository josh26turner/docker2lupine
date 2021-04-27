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


def get_linux_options(app_conf_file_name):
    conf_file_name = app_conf_file_name or 'configs/general.config'
    with open(conf_file_name, 'r') as conf_file:
        confs = []
        for line in conf_file.readlines():
            if len(line) > 1:
                confs.append(line.replace('=y', '').replace('\n', ''))
        return confs


def dump_fs(image_name, skip_fs_dump) -> str:
    tar = image_name.replace(':', '-').replace('/', '-') + '.tar'
    if not skip_fs_dump:
        docker_id = subprocess.check_output(['docker', 'create', image_name]).decode('utf-8').replace('\n', '')
        os.system('docker export {id} > {manifest_out}{tarball}'.format(id=docker_id, tarball=tar, manifest_out=manifest_out))
        os.system('docker rm {} > /dev/null'.format(docker_id))
    return manifest_out + tar


def build_manifest(docker_obj, app_conf_file_name, skip_fs_dump, kml) -> Manifest:
    manifest = Manifest()

    manifest.runtime.entry = docker_obj['Config']['Entrypoint'] or [] + docker_obj['Config']['Cmd'] or []
    manifest.runtime.envs = docker_obj['Config']['Env']
    manifest.runtime.working_directory = docker_obj['Config']['WorkingDir']

    manifest.runtime.enabled_init_options = ['PROC_FS', 'NET_SETUP', 'ENTROPY_GEN', 'TMP_FS']

    manifest.linux_configuration.kml = kml
    manifest.linux_configuration.options = get_linux_options(app_conf_file_name)

    manifest.filesystem = dump_fs(docker_obj['RepoTags'][0], skip_fs_dump)

    return manifest
    

if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser(epilog='Run from the Lupine root directory')

    parser.add_argument('docker_image')
    parser.add_argument('docker_tag', default='latest', nargs='?')
    parser.add_argument('--output')
    parser.add_argument('--skip_fs_dump', action='store_true', help='just remake the manifest')
    parser.add_argument('--no_kml', action='store_true', help='disable KML in the Lupine image')
    parser.add_argument('--app_conf', help='path to app config file')

    args = parser.parse_args()

    if not os.path.exists(manifest_out):
        os.mkdir(manifest_out)

    out_file_name = manifest_out + (args.output or args.docker_image.replace('/', '-') + '-' + args.docker_tag + '.json')

    docker_obj = inspect_docker_image(args.docker_image + ':' + args.docker_tag)
    manifest = build_manifest(docker_obj, args.app_conf, args.skip_fs_dump, not args.no_kml)

    with open(out_file_name, 'w') as out_file:
        json.dump(manifest, out_file, default=lambda o: o.__dict__, indent=4,)
        print(out_file_name)
