import argparse
import json
import multiprocessing
import os
import re
import string
import sys

# Global Vars
file_bytes = ""
regex_chars_supported = "^*+?[](),"

def convert_hex_string_pattern_to_bytes_pattern(hex_pattern):
    """
    :param hex_pattern: hex string pattern, might contain special regex chars. e.g AABB(CC)+
    :return: valid bytes string pattern e.g b'\xaa\xbb(\xcc)+'
    """
    bytes_pattern = b''
    pattern_chars = re.findall("(\w\w|[\%s]|\{.+\})" % "\\".join(regex_chars_supported), hex_pattern)

    for i in pattern_chars:
        if len(i) != 2:
            bytes_pattern += i.encode("ascii")
        else:
            bytes_pattern += bytes.fromhex(i)
    return bytes_pattern


def search_pattern(hex_string_pattern):
    """
    Search pattern inside files_bytes
    :param pattern: e.g AA1258
    :return: {pattern: [(start,end),...]}
    """
    matches = []
    bytes_pattern = convert_hex_string_pattern_to_bytes_pattern(hex_string_pattern)

    for m in re.finditer(bytes_pattern, file_bytes):
        matches.append(list(map(hex, m.span())))

    return (hex_string_pattern, matches) if matches else None


def verify_files_exists(args):
    assert os.path.isfile(args.bin_file), "--bin file path does not pointing to a file"
    assert os.path.isfile(args.p_file), "--pattern file path does not pointing to a file"


def get_args():
    parser = argparse.ArgumentParser(description="Search list of strings/regex-like patterns in a bin file",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--bin', dest='bin_file', required=True,
                        help='Path of a binary file you wish to search in.')
    parser.add_argument('--pattern', dest='p_file', required=True,
                        help='Path of a json file containing dictionary of patterns (keys) and their label (values).')
    parser.add_argument("-v", '--verbose', dest='verbose', action='store_true',
                        help="Output progress steps")
    parser.add_argument("-p", '--processes', dest='processes', type=int, default=0,
                        help="define processes number, if default value (0) is set,"\
                             "number of processes would be same as the number of cores on the machine")
    args = parser.parse_args()

    return args


def load_patterns(path):
    """
        Checks if pattern file data format is valid.
        returns: list [pattern, pattern, ...]
    """
    try:
        json_patterns = json.load(open(path, 'r'))
    except json.decoder.JSONDecodeError:
        print(f"[-] Error: Invalid json format string in pattern file {path}")
        sys.exit(1)

    # Validate object format
    assert type(json_patterns) == list, "[-] Invalid json format, for more information read run with -h"
    for pattern in json_patterns:
        i = 0

        # Check all chars pairs in the pattern represent a valid byte (expect regex special chars)

        # Remove {.+} first to ignore the numbers inside
        tmp_pattern = re.sub("\{.+\}", '', pattern)

        while i < len(tmp_pattern):
            if tmp_pattern[i] in string.hexdigits:
                assert tmp_pattern[i+1] in string.hexdigits, f"[-] Pattern invalid format -> ({pattern})"
                i += 2
            else:
                assert tmp_pattern[i] in regex_chars_supported, f"[-] Pattern invalid format -> ({pattern})"
                i += 1

        # Check the whole pattern regex-like format
        try:
            re.compile(pattern)
        except re.error:
            print(f"Invalid regex pattern -> {pattern}")
            sys.exit(1)

    return json_patterns


def main():
    global file_bytes

    # Handle args
    args = get_args()
    verify_files_exists(args)
    verbose = args.verbose
    processes = args.processes if args.processes else multiprocessing.cpu_count()

    if verbose:
        print("[+] load patterns file...")

    # load pattern dict
    patterns = load_patterns(args.p_file)

    if verbose:
        print("[+] reading binary file")

    file_bytes = open(args.bin_file, "rb").read()

    if verbose:
        print(f"[+] Multi-Processes number {processes}")
        print(f"[+] {len(patterns)} patterns total")
        print(f"[+] starting search...\n")


    p = multiprocessing.Pool(processes)
    results = p.map(search_pattern, patterns)
    p.close()

    # Concatenate dict items into dict
    results_dict = dict([res_pair for res_pair in results if res_pair])

    print(json.dumps(results_dict))


if __name__ == "__main__":
    main()