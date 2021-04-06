import json
import fnmatch

from parser import parse_files, get_files, get_syscall_names
from load_options import get_options, get_all_options, Product


KERNEL_NOT_CONFIGURED = [
    "CONFIG_AIO",
    "CONFIG_EVENTFD",
    "CONFIG_INET",
    "CONFIG_NET_CORE",
    "CONFIG_NETDEVICES",
    "CONFIG_NET",
    "CONFIG_RT_MUTEXES",
    "CONFIG_SECCOMP",
    "CONFIG_SIGNALFD",
    "CONFIG_SYSVIPC",
    "CONFIG_UNIX",
    "CONFIG_VIRTIO_NET",
    "CONFIG_VIRTIO",
]

INIT_NOT_CONFIGURED = [
    "NET_SETUP"
]


def check_file_opt(opt, file):
    if hasattr(opt.catalyst, 'files'):
        for opt_file in opt.catalyst.files:
            if fnmatch.fnmatch(file, opt_file):
                return True
    
    return False

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('strace_files', nargs='+')
    args = parser.parse_args()

    syscalls = parse_files(args.strace_files)

    print(json.dumps(get_syscall_names(syscalls)))
    # print(json.dumps(get_files(syscalls)))

    options = get_all_options()

    enabled_kernel_configs = set()
    enabled_init_configs = set()

    for file in get_files(syscalls):
        for opt in options:
            if hasattr(opt.catalyst, 'files') and check_file_opt(opt, file):
                if hasattr(opt.product, 'kernel'):
                    enabled_kernel_configs.update(opt.product.kernel)
                if hasattr(opt.product, 'init'):
                    enabled_init_configs.update(opt.product.init)

                options.remove(opt)

    for syscall in get_syscall_names(syscalls):
        for opt in options:
            if hasattr(opt.catalyst, 'syscalls') and syscall in opt.catalyst.syscalls:
                if hasattr(opt.product, 'kernel'):
                    enabled_kernel_configs.update(opt.product.kernel)
                if hasattr(opt.product, 'init'):
                    enabled_init_configs.update(opt.product.init)

                options.remove(opt)

    print(json.dumps(sorted(enabled_init_configs)))
    print(json.dumps(sorted(enabled_kernel_configs)))
