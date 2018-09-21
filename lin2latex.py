#!/usr/bin/env python

"""
    lin2latex.py

    Functions that will read in a .lin file, and format them
    into LaTeX tables.

    This script will be built with click!
"""

import pandas as pd
import click
import numpy as np


def lin2latex(dataframe, spins, labels=None, deluxe=False):
    """ Function that will convert a dataframe into a LaTeX
        formatted table. Optionally, you can select specific
        quantum numbers to include in the table.
        
        The formatting follows the "house style",
        which groups rows by J, followed by N and F.
        
        The labels should be supplied without indication of
        upper or lower state, i.e. J and not J''. Also, labels
        should be in the order you want them!!!
        
        Requires:
        ------------
        dataframe - dataframe read in the format from `read_lin`
        labels - optional tuple-like which lists out which quantum
        numbers to include. Defaults to printing all the quantum
        numbers.
    """
    if labels is None:
        # Take all the keys except the weird column
        columns = [key for key in dataframe.keys() if key != "_"]
        labels = [key for key in dataframe.keys()]
        for label in ["Frequency", "Uncertainty", "_"]:
            labels.remove(label)
        quant_types = [label.replace("'", "") for label in labels]
        group, upper, lower = generate_labels(labels)
    else:
        # Generate the labeling
        group, upper, lower = generate_labels(labels)
        labels = group.copy()
        columns = group
        columns.extend(["Frequency", "Uncertainty"])
    # Accommodate for spin
    spins = np.repeat(spins, 2)
    for index, label in enumerate(labels):
        dataframe[label]-=spins[index]
    # Template for a deluxe table used by ApJ and others
    if deluxe is True:
        template = """
        \\begin{{deluxetable}}{colformat}
            \\tablecaption{{Something intelligent}}
            \\tablehead{{header}}
            
            \\startdata
                {data}
            \\enddata
        \\end{{deluxetable}}
        """
    # Template for a normal LaTeX table
    elif deluxe is False:
        template = """
        \\begin{{table}}
            \\begin{{center}}
                \\caption{{Something intelligent}}
                \\begin{{tabular}}{colformat}
                {header}
                \\toprule
                
                {data}
                \\bottomrule
                \\end{{tabular}}
            \\end{{center}}
        \\end{{table}}
        """
    data_str = ""
    # Take only what we want
    filtered_df = dataframe[columns]
    # Sort the dataframe by J
    filtered_df.sort_values(["J'", "J''"])
    # Build up the table data
    for index, row in filtered_df.iterrows():
        line = list()
        for up, low in zip(upper, lower):
            pair = row[[up, low]]
            # Check if quantum numbers can be integers
            check = [value.is_integer() for value in pair]
            if all(check) is True:
                format_type = int
            else:
                format_type = float
            pair = list(pair.astype(format_type))
            line.append(
                "${0} \\rightarrow {1} $".format(*pair)
                )
        values = list(row.astype(str))
        # We want to skip printing J transitions if they're the same
        if index == 0:
            Jlast = values[:2]
        else:
            Jcurr = values[:2]
            # If the current values of J match the previous, then
            # set them to blank so we don't print them
            if Jcurr == Jlast:
                line[0] = " $\\dots$ "
            Jlast = Jcurr
        last = row[["Frequency", "Uncertainty"]].map("{:,.4f}".format)
        last = last.astype(str)
        last[-1]+="\\\\\n"
        line.extend(last)
        data_str+= " & ".join(line)
    # Write out the column formatting in the table
    # Half the total number of columns, and another two for freq/unc
    column_format = ["c"] * int((len(columns) / 2) + 1)
    column_format = "{" + " ".join(column_format) + "}"
    header = ""
    for up, low in zip(upper, lower):
        header+="${0} \\rightarrow {1}$ & ".format(*[up, low])
    header+="Frequency & Uncertainty \\\\"
    data_dict = {
        "colformat": column_format,    # centered
        "data": data_str,
        "header": header 
    }
    return template.format_map(data_dict)


def generate_labels(labels):
    """ Function that will generate the quantum number
        labelling for upper and lower states.
        
        Requires:
        ------------
        labels - tuple-like containing quantum number labels
        without indication of upper or lower state
        
        Returns:
        ------------
        grouped, upper, lower - lists corresponding to the
        labels groups by quantum number (rather than upper/lower),
        and the upper and lower state quantum numbers respectively.
    """
    grouped_labels = list()
    lower_labels = list()
    upper_labels = list()
    for label in labels:
        for index, symbol in enumerate(["""'""", """''"""]):
            header = label + symbol
            grouped_labels.append(header)
            if index == 0:
                upper_labels.append(header)
            else:
                lower_labels.append(header)
    return grouped_labels, upper_labels, lower_labels


def read_lin(filepath, labels, spins):
    """ Function that will read in a .lin file and quantum number
        labeling, and return a formatted LaTeX table.
        
        The labels should be supplied without indication of
        upper or lower state, i.e. J and not J''.
        
        Requires:
        ------------
        filepath - path to the .lin file
        labels - tuple-like, lists the quantum number labels
    """
    df = pd.read_csv(filepath, delim_whitespace=True, header=None)
    grouped_labels, upper_labels, lower_labels = generate_labels(labels)
    # Tack on the remaining three columns after the quantum numbers
    col_headings = upper_labels + lower_labels
    col_headings.extend(["Frequency", "Uncertainty", "_"])
    df.columns = col_headings
    df = df[grouped_labels + ["Frequency", "Uncertainty", "_"]]
    hyperfine_labels = [value for value in df.keys() if "F" in value]
    # Get rid of frequency
    hyperfine_labels.remove("Frequency")
    return df


@click.command()
@click.argument(
    "filepath",
    )
@click.argument(
    "labels",
    )
@click.option(
    "--spins",
    default=None,
    help="Specifies a shift corresponding to spin to each quantum number"
    )
@click.option(
    "--deluxe",
    is_flag=True,
    help="Specifies deluxe tables to be used instead of regular LaTeX tables."
    )
@click.option(
    "--select",
    default=None,
    help="Labels for the quantum numbers that you wish to include in the table."
    )
@click.option(
    "--output",
    default="table.tex",
    help="Target file to output the table to."
    )
def run_lin2latex(filepath, labels, spins, deluxe, select, output):
    """ lin2latex.py

        This script will take a .lin file and convert it into a formatted
        LaTeX table. Aside from the minimum input below there are options
        to only print specific quantum numbers, and to use deluxe or normal
        LaTeX table environments.

        Spin can be specified by: --spin "0, 0, 0.5" for example, where the
        final quantum number is subtracted by half.

        Required input:

        ------------------

        filepath - path to the .lin file you want to convert

        labels - A series of labels to use for the quantum numbers in quote marks
        separated by commas, e.g.

                 "J, N, F"
    """
    labels = labels.split(",")
    if select:
        # Split the selected labels
        select = select.split(",")
    else:
        select = labels
    if spins:
        # If (hyper)fine structure is specified
        spins = spins.split(",")
        print(spins)
        # Check that the length of spins list is
        # the same as the selected quantum numbers
        assert len(spins) == len(select)
        # Convert offset values to floats
        spins = [float(value) for value in spins]
    else:
        # If no spins are specified
        spins = [0] * len(select)
    print("Read in the following labels")
    print(labels)
    print("----------------------------")
    if select:
        print("Only these labels will be included")
        print(select)
    df = read_lin(filepath, labels, spins)
    # Deluxe table flag
    if deluxe:
        deluxe = True
    else:
        deluxe = False
    table_str = lin2latex(df, spins, select, deluxe)
    with open(output, "w+") as write_file:
        write_file.write(table_str)

if __name__ == "__main__":
    run_lin2latex()

