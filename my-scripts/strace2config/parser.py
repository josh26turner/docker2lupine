from typing import NamedTuple


class SysCall(NamedTuple):
    name: str
    args: list[str or int]
    res: int or str
    res_str: str
    data: list[str or int]


def find_index(buffer: list[chr], char: chr, match: chr = None) -> int:
    skip = 0
    quote = False
    delim = False

    for i, c in enumerate(buffer):
        if c == '"' and not delim:
            quote = not quote

        delim = c == '\\'

        if quote:
            continue

        if c == char and skip == 0:
            return i

        skip += 1 if c == match else -1 if c == char else 0

    return len(buffer)


def read_to(buffer: list[chr], char: chr, match: chr = None) -> list[chr]:
    index = find_index(buffer, char, match)
    ret = buffer[:index]
    del buffer[:index + 1]

    return ret


def try_int(x: str) -> str or int:
    try:
        return int(x)
    except ValueError:
        return x


def parse_res(x: str) -> (int or str, str):
    try:
        res = x if x[:2] == '0x' else 0 if x == '?' else int(x)
        return res, ''
    except ValueError:
        res, res_str = x.split(' ')
        res = int(res)

        return res, res_str


def parse_list(arg_string: str) -> list:
    return list(map(try_int, arg_string.split(',')))


def parse_line(strace_line: str) -> SysCall or None:
    try:
        strace_list = list(strace_line)

        if strace_line[:3] == '---' or strace_line[:3] == '+++':
            return None

        call = ''.join(read_to(strace_list, '('))

        args = parse_list(''.join(read_to(strace_list, ')', '(')))

        read_to(strace_list, '=')

        res, res_str = parse_res(''.join(read_to(strace_list, '(')).strip())

        read_to(strace_list, '[')
        read_to(strace_list, '{')

        data = parse_list(''.join(read_to(strace_list, '}', '{')))

        read_to(strace_list, '\n')

        return SysCall(call, args, res, res_str, data)

    except ValueError:
        return None


def parse_file(strace_file_name: str) -> list[SysCall]:
    with open(strace_file_name, 'r') as strace_file:
        return list(filter(lambda x: x is not None, map(parse_line, strace_file.readlines())))


def parse_files(strace_file_names: list[str]) -> list[SysCall]:
    lines: list[str] = list()

    for strace_file_name in strace_file_names:
        with open(strace_file_name, 'r') as strace_file:
            lines.extend(strace_file.readlines())

    return list(filter(lambda x: x is not None, map(parse_line, lines)))


def get_files(syscalls: list[SysCall]) -> list[str]:
    return sorted(set(map(lambda x: x.args[0].replace('\"', ''), filter(lambda x: x.name == 'open' and x.res != -1, syscalls))))


def get_syscall_names(syscalls: list[SysCall]) -> list[str]:
    return sorted(set(map(lambda x: x.name, syscalls)))


def get_socket_types(syscalls: list[SysCall]) -> list[str]:
    return sorted(set(x.args[0] for x in filter(lambda x: x.name == 'socket', syscalls)))
