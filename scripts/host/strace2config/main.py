import json
import fnmatch

from collections.abc import Iterable

from strace2config.parser import parse_files, get_files, get_syscall_names
from strace2config.load_options import get_options, get_all_options, Config


def check_file_opt(opt: Config, file: str) -> bool:
    if opt.catalyst.files is not None:
        for opt_file in opt.catalyst.files:
            if fnmatch.fnmatch(file, opt_file):
                return True
    
    return False


def get_min_config(strace_files: list[str]) -> (list[str], list[str]):
    syscalls = parse_files(strace_files)

    options = get_all_options()

    enabled_kernel_configs = set()
    enabled_init_configs = set()

    for file in get_files(syscalls):
        for opt in options:
            if opt.catalyst.files is not None and check_file_opt(opt, file):
                if opt.product.kernel is not None:
                    enabled_kernel_configs.update(opt.product.kernel)
                if opt.product.init is not None:
                    enabled_init_configs.update(opt.product.init)

                options.remove(opt)

    for syscall in get_syscall_names(syscalls):
        for opt in options:
            if opt.catalyst.syscalls is not None and syscall in opt.catalyst.syscalls:
                if opt.product.kernel is not None:
                    enabled_kernel_configs.update(opt.product.kernel)
                if opt.product.init is not None:
                    enabled_init_configs.update(opt.product.init)

                options.remove(opt)

    for call in syscalls:
        for opt in options:
            if opt.catalyst.sys_args is not None:
                for arg in opt.catalyst.sys_args:
                    if arg.call == call.name and len(call.args) > arg.arg_pos:
                        for arg_val in arg.arg_vals:
                            if arg_val == call.args[arg.arg_pos] or \
                                    (isinstance(call.args, Iterable) and arg_val in call.args[arg.arg_pos]):
                                if opt.product.kernel is not None:
                                    enabled_kernel_configs.update(opt.product.kernel)
                                if opt.product.init is not None:
                                    enabled_init_configs.update(opt.product.init)

                                options.remove(opt)

    return (sorted(enabled_init_configs), sorted(enabled_kernel_configs))


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('strace_files', nargs='+')
    args = parser.parse_args()

    init, kernel = get_min_config(args.strace_files)
    print(init, kernel)
