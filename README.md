**Multi-processes search binaries**

search-binaries.py is a fast command line program for searching fast binaries inside bin files.

There are few limitations you should be aware of:

* the program fully load the binary file, which by law mean its all on your RAM memory.
* the program is multi-processes (changeable), the program using by default all your cores for the search process.
    if you wish to change that, you may use --processes argument.

One big advantage of this script is that it's can have regex patterns.
wait what?
Yes, you may use regex patterns to search for binaries (although its much slower).
Examples:
* (00){50,} # At least 50 time \x00
* (AA)+ - # one or more \xAA

**HOW TO USE:**

search-binaries.py --bin <file-path> --pattern <file-path>

--bin -> path to a the file you wish to search in.

--pattern -> path to a json pattern file, with a very specific format (described below).

OPTIONAL:

--processes -> processes number, by default equal to the number of cores on the machine.

--verbose -> output progress steps lines.

Pattern file need to contain json list format string of containing the patterns you want to search for.
Each pattern need to be in hex string format (expect the regex special chars).

Example:
[
    "00AABBCC", 
    "1F8B[08AB]+", 
    "00{100,}"
]

_Extra notes:_
* Requires python 3.
* Output is in json format
