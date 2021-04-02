from parser import parse_files
import json

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('strace_files', nargs='+')
    args = parser.parse_args()

    syscalls = parse_files(args.strace_files)

    print(json.dumps(sorted(set(map(lambda x: x.name, syscalls)))))

    print(json.dumps(sorted(set(map(lambda x: x.args[0].replace('\"', ''), filter(lambda x: x.name == 'open', syscalls))))))
