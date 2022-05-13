#!/usr/bin/env python3.10

from collections import defaultdict
import subprocess
import re

def main():
    source_dir = '/mnt/btr_pool/@/.snapshots'
    dest_dir = '/mnt/backup/btrbk_snapshots'
    snapshot_regex = re.compile(r'(?P<key>\S*)\.(?P<datetime>\d{8}T\d{4})')
    host = 'lap'


    source_content = defaultdict(list)
    for element in subprocess.run(['ls', '-l', source_dir], stdout=subprocess.PIPE, check=True).stdout.decode().split():
        groups = snapshot_regex.search(element)
        if not groups:
            continue


        key = groups['key']
        datetime = groups['datetime']
        source_content[key].append((datetime, element))


    dest_content = defaultdict(set)
    for element in subprocess.run(['ssh', host, 'ls', '-l', dest_dir], stdout=subprocess.PIPE, check=True).stdout.decode().split():
        groups = snapshot_regex.search(element)
        if not groups:
            continue

        key = groups['key']
        datetime = groups['datetime']
        dest_content[key].add((datetime, element))

    for k, v in source_content.items():
        source_content[k] = sorted(v)

    for snap_type, snapshots in source_content.items():
        dest_snapshots = dest_content[snap_type]
        parent = None

        for snapshot in snapshots:
            if snapshot not in dest_snapshots:
                parent_parameter = f'-p {source_dir}/{parent[1]}' if parent is not None else ''
                command = f'sudo btrfs send {parent_parameter} {source_dir}/{snapshot[1]} | pv | ssh {host} "pv -B 1G | sudo btrfs receive {dest_dir}"'
                print(f'Sending {snapshot=} with {parent=} {command=}')
                subprocess.run(command, shell=True, check=True)

            parent = snapshot



if __name__ == '__main__':
    main()
