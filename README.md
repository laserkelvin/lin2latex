# lin2latex.py

## Script for converting `.lin` files into LaTeX tables.

This is a command line tool written in Python 3 and click that will take
a formatted `.lin` file used in SPFIT, and format it into a TeX `tabular`
environment or a `deluxetable`.

# Installation

1. Install the required Python packages by typing

`pip install .`

1. Optional: if you want the script accessible from anywhere, add it to a directory
in your path. The simplest way would be with `sudo` access:

`sudo cp scripts/lin2latex.py /usr/local/bin/`

# Usage

The following prompt is given when launching with the `--help` flag:

```
Usage: lin2latex.py [OPTIONS] FILEPATH LABELS

  lin2latex.py

  This script will take a .lin file and convert it into a formatted LaTeX
  table. Aside from the minimum input below there are options to only print
  specific quantum numbers, and to use deluxe or normal LaTeX table
  environments.

  Spin can be specified by: --spin "0, 0, 0.5" for example, where the final
  quantum number is subtracted by half.

  Required input:

  ------------------

  filepath - path to the .lin file you want to convert

  labels - A series of labels to use for the quantum numbers in quote marks
  separated by commas, e.g.

           "J, N, F"

Options:
  --spins TEXT   Specifies a shift corresponding to spin to each quantum
                 number
  --deluxe       Specifies deluxe tables to be used instead of regular LaTeX
                 tables.
  --select TEXT  Labels for the quantum numbers that you wish to include in
                 the table.
  --output TEXT  Target file to output the table to.
  --help         Show this message and exit.
```

