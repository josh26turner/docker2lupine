import json
import sys
import os
import tempfile

from shutil import copyfile

#TODO: musl libc setup
#TODO: direct init insert w/o recreating whole rootfs

def read_manifest(file_name):
    try:
        with open(file_name, 'r') as manifest:
            manifest_data = json.load(manifest)
            if all(k in ['linux_configuration', "runtime", "filesystem"] for k in manifest_data):
                return manifest_data
            else:
                print("Error in manifest", file=sys.stderr)
                return None
    except:
        print("Error opening or reading manifest", file=sys.stderr)
        return None

def build_linux(linux_config, app_name):
    base_file_path = ""
    if (linux_config['kml']):
        print("Patching linux")
        os.system("make patch-linux 2>/dev/null >/dev/null")
        base_file_path = "./configs/lupine-djw-kml.config"
    else:
        print("Unpatching linux")
        os.system("make unpatch-linux 2>/dev/null >/dev/null")
        base_file_path = "./configs/lupine-djw-nokml.config"

    print("Loading config")

    linux_dir = "./linux/"
    linux_conf = linux_dir + "/.config"
    build_dir = "./kernelbuild/"

    copyfile(base_file_path, linux_conf)

    with open(linux_conf, 'a') as linux_conf_file:
        for opt in linux_config['options']:
            linux_conf_file.write(opt + "=y\n")

    print("Building kernel")

    if not os.path.exists(build_dir + app_name):
        os.mkdir(build_dir + app_name)

    os.system("yes no | make -C " + linux_dir + " oldconfig")
    os.system("make build-linux")
    copyfile(linux_dir + "vmlinux", build_dir + app_name + "/" + "vmlinux")

    return

def build_init(init_options, app_name):
    open('./init/env.sh'.format(app_name=app_name), 'w+') .close()
    with open('./init/env.sh'.format(app_name=app_name), 'w+') as env_file:
        for env in init_options['envs']:
            env_file.write("export '" + env + "'\n")

        env_file.write('WORKING_DIR="' + init_options['working_directory'] + '"\n')
        env_file.write('CMD="' + init_options['entry_command'] + '"\n')
        env_file.write('NAME="' + app_name + '"\n')

        for opt in init_options['enabled_init_options']:
            env_file.write(opt + "=1" + '\n')
        
    os.system('make -C init out=build/{app_name}'.format(app_name=app_name))

    return

def build_fs(fs_path, app_name):
    rootfsbuild = 'rootfsbuild'
    if not os.path.exists(rootfsbuild):
        os.mkdir(rootfsbuild)
    
    os.system('dd if=/dev/zero of={rootfsbuild}/{app_name}.ext2 bs=1 count=0 seek=20G'.format(app_name=app_name, rootfsbuild=rootfsbuild))
    os.system('yes | mkfs.ext2 {rootfsbuild}/{app_name}.ext2'.format(app_name=app_name, rootfsbuild=rootfsbuild))

    with tempfile.TemporaryDirectory() as target_dir:
        print(target_dir)
        os.system('sudo mount {rootfsbuild}/{app_name}.ext2 {target_dir}'.format(app_name=app_name, target_dir=target_dir, rootfsbuild=rootfsbuild))

        os.system('sudo tar -xvf {fs} -C {target} > /dev/null'.format(fs=fs_path, target=target_dir))

        nodes = [
            ["/dev/null", "666", "c 1 3"],
            ["/dev/zero", "666", "c 1 5"],
            ["/dev/ptmx", "666", "c 5 2"],
            ["/dev/tty",  "666", "c 5 0"],
            ["/dev/random", "444", "c 1 8"],
            ["/dev/urandom", "444", "c 1 9"],
            ["/dev/null", "660", "c 1 3"],
        ]
        for node in nodes:
            os.system('sudo mknod -m {mode} {fs}{pathname} {dev}'.format(
                pathname=node[0],
                mode=node[1],
                dev=node[2],
                fs=target_dir))

        os.system('make -C load_entropy install')
        os.system('sudo cp -r ./my-scripts/guest/* {target}'.format(target=target_dir))
        os.system('sudo cp ./my-scripts/guest/libc.so {target}/lib/ld-musl-x86_64.so.1'.format(target=target_dir))

        os.system('sudo cp ./init/build/{app_name}/* {target}'.format(target=target_dir, app_name=app_name))

        os.system('sudo umount {target}'.format(target=target_dir))
    return
    
if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser(epilog="Run from the Lupine root directory")

    parser.add_argument("manifest")
    parser.add_argument("--name")
    parser.add_argument("--kernel", action="store_true", help="build the kernel")
    parser.add_argument("--filesystem", action="store_true", help="create the filesystem")

    args = parser.parse_args()
    build_all = not (args.kernel or args.filesystem)

    name = args.name or os.path.splitext(os.path.split(args.manifest)[-1])[0]
    print(name)

    data = read_manifest(args.manifest)
    if args.filesystem or build_all:
        build_init(data['runtime'], name)
        build_fs(data['filesystem'], name)

    if args.kernel or build_all:
        build_linux(data['linux_configuration'], name)
