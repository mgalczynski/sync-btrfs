#!/usr/bin/env python3.10

from collections import defaultdict
import subprocess

def main():
    source_dir = '/mnt/backup/btrbk_snapshots'
    dest_dir = '/mnt/backup/btrbk_snapshots'
    host = 'lap'


    source_content = defaultdict(list)
    for element in subprocess.run(['ls', '-l', source_dir], stdout=subprocess.PIPE, check=True).stdout.decode().split():
        elements = element.split('.')
        if len(elements) != 2:
            continue
        key, dt = elements
        source_content[key].append((dt, element))


    dest_content = defaultdict(set)
    for element in subprocess.run(['ssh', host, 'ls', '-l', dest_dir], stdout=subprocess.PIPE, check=True).stdout.decode().split():
        elements = element.split('.')
        if len(elements) != 2:
            continue
        key, dt = elements
        dest_content[key].add((dt, element))

    for k, v in source_content.items():
        source_content[k] = sorted(v)

    for snap_type, snapshots in source_content.items():
        dest_snapshots = dest_content[snap_type]
        parent = None

        for snapshot in snapshots:
            if snapshot not in dest_snapshots:
                parent_parameter = f'-p {source_dir}/{parent[1]}' if parent is not None else ''
                command = f'sudo btrfs send {parent_parameter} {source_dir}/{snapshot[1]} | ssh {host} sudo btrfs receive {dest_dir}'
                print(f'Sending {snapshot=} with {parent=} {command=}')
                subprocess.run(command, shell=True, check=True)

            parent = snapshot



if __name__ == '__main__':
    main()