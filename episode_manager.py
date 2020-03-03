#!/usr/bin/python3

import os
import re
import string
import argparse
from pathlib import Path

dry_run_flag = False

dummy_files = ['Ep. 21 - The State-[720p].mkv',
               'Ep. 26 - The Blind -[720p].mkv',
               'Ep. 31 - The Desert-[720p].mkv',
               'Ep. 36 - A Days-[720p].mkv',
               'Ep. 22 - The Cave-[720p].mkv',
               'Ep. 27 - Alone-[720p].mkv',
               'Ep. 32 - Journey Part 1-[720p].mkv',
               'Ep. 37 - Lake -[720p].mkv',
               'Ep. 23 - Return -[720p].mkv',
               'Ep. 28 - The Chase-[720p].mkv',
               'Ep. 33 - Journey Part 2-[720p].mkv',
               'Ep. 38 - The Earth -[720p].mkv',
               'Ep. 24 - The Swamp-[720p].mkv',
               'Ep. 29 - Bitter -[720p].mkv',
               'Ep. 34 - Secrets-[720p].mkv',
               'Ep. 39 - The Guru-[720p].mkv',
               'Ep. 25 - Day-[720p].mkv',
               'Ep. 30 - The Library-[720p].mkv',
               'Ep. 35 - Tales-[720p].mkv',
               'Ep. 40 - The Crossroads-[720p].mkv']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help='File or Directory to work on')
    parser.add_argument("show_name", help='Name of show')
    parser.add_argument('-d', '--dry-run', action='store_true', default=False,
                        dest='dry_run',
                        help='Do a try run')
    parser.add_argument('-s', '--season-break', action='append', dest='season_break',
                        default=[],
                        help='Last episode of each season. ex: -s 13 -s 26')
    parser.add_argument('-S', '--shift', action='store_true', dest='shift',
                        default=False,
                        help='Shift a season to start at episode 1')

    # create_dummy_files(dummy_files2)
    args = parser.parse_args()
    global dry_run_flag
    season_break = args.season_break
    season_break.append('0')
    dry_run_flag = args.dry_run
    show_name = args.show_name
    ep_dict, dir_path = parse_target(args.target)

    if args.shift:
        print('Doing Season Shift...')
        shift_season(ep_dict, dir_path)
        print("Season shift complete.")
        exit(0)

    if is_target_dir(args.target):
        rename_files(ep_dict, dir_path, show_name, season_break)
    else:
        rename_single_file(ep_dict, dir_path, show_name)


def shift_season(ep_dict, dir_path):
    rename_map = []
    shift_list = sorted(ep_dict.items())
    for ep in shift_list:
        shifted_ep_num = shift_list.index(ep)+1
        shifted_ep = ep[1].replace(str(ep[0]), str(shifted_ep_num), 1)
        old_name = ep_dict[ep[0]]
        new_name = shifted_ep
        rename_map.append((os.path.join(dir_path, old_name), os.path.join(dir_path, new_name)))
    do_rename(rename_map)


def create_dummy_files(files):
    for item in files:

        with open(os.path.join("Season 3", item), "w") as f:
            f.write("This is my first line of code")
            f.write("\nThis is my second line of code with {} the first item in my list".format(item))
            f.write("\nAnd this is my last line of code")
            f.flush()
            f.close()
    exit()


def rename_single_file(ep_dict, dir_path, show_name):
    print('Renaming single file')
    work = []

    for ep, old_name in ep_dict.items():
        extension = old_name[old_name.rfind('.'):]
        new_name = '{} - {:02d}{}'.format(show_name, ep, extension)
        work.append((os.path.join(dir_path, old_name), os.path.join(dir_path, new_name)))

    do_rename(work)


def rename_files(ep_dict, dir_path, show_name, season_break):
    print('Renaming directory contents')
    seasons = []

    for break_point in reversed(sorted(season_break)):
        season = []
        for ep in reversed(sorted(ep_dict.items())[int(break_point)::]):
            season.append(ep)
            del(ep_dict[ep[0]])
        seasons.append(season)

    i = 0
    work = []
    for season in reversed(seasons):
        i = i + 1
        directory = "Season {:02d}".format(i)
        if not dry_run_flag:
            try:
                os.mkdir(os.path.join(dir_path, directory))
            except FileExistsError:
                # Directory exists...who cares?
                pass
        x = 0
        for ep, old_name in reversed(season):
            x = x + 1
            extension = old_name[old_name.rfind('.'):]
            new_name = '{} - {:02d}{}'.format(show_name, x, extension)
            work.append((os.path.join(dir_path, old_name), os.path.join(dir_path, directory, new_name)))

    do_rename(work)


def do_rename(file_map):
    if dry_run_flag:
        print("\n!! Doing dry-run. No files will be changed !!\n")
    for old, new in sorted(file_map, key=lambda ep: ep[1]):
        print("{} => {}".format(old, new))
        if not dry_run_flag:
            os.rename(old, new)
    if dry_run_flag:
        print('\nDry run complete.')


def parse_target(target):
    if is_target_dir(target):
        ep_dict, dir_path = parse_target_dir(target)

    else:
        dir_path = os.path.dirname(target)
        name = os.path.basename(target)
        ep_dict = parse_target_file(dir_path, name)

    return ep_dict, dir_path


def parse_target_dir(target):
    files = []
    filenames = None
    dirpath = None
    ep_dict = {}

    for (dirpath, dirnames, filenames) in os.walk(target):
        files.extend(filenames)
        break

    if not files:
        print('oh shit no files')
        exit(3)

    for f in files:
        ep_dict.update(parse_target_file(dirpath, f))

    return ep_dict, dirpath


def parse_target_file(dirpath, target):
    if not os.path.isfile(os.path.join(dirpath, target)):
        print("Error: {} is not a valid file".format(target))
        return False

    episode = get_episode_num2(target)
    if not episode:
        print("Rogue file found. No episode number found in {}".format(target))
        return dict()

    return dict([(int(episode), target)])


# added mar '20, old method broke, too lazy to fix
def get_episode_num2(target):
    ep = re.findall(r"(?:e|ep. |x|episode|\n)(\d{2})", target, re.I)
    return ep[0]


def get_episode_num(target):
    work = re.sub("[\(\[].*?[\)\]]", "", target)
    while any((c in string.ascii_letters) for c in work):
        work = work.strip(string.ascii_letters + string.punctuation+string.whitespace + string.punctuation)
    return work


def is_target_dir(target):
    if not target:
        print('must provide target')
        exit(1)
    target = Path(target)
    if target.is_dir():
        return True
    elif target.is_file():
        return False
    else:
        print('target not valid')
        exit(2)


if __name__ == '__main__':
    main()


