
from pathlib import Path
from string import Template


class LinFile:
    def __init__(self, path, mol_type, labels, **kwargs):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist.")
        implemented_types = [
            "symmetric",
            "linear",
            "asymmetric",
            "hfs"
        ]
        if mol_type not in implemented_types:
            raise Exception(f"Molecule type {mol_type} not implemented.")
        self.mol_type = mol_type
        self.contents = path.read_text().split("\n")
        self.out_path = path.with_suffix(".tex")
        self.data = list()
        self.full_labels = [f"{label}'" for label in labels]
        self.full_labels.extend([f"""{label}''""" for label in labels])
        self.full_labels.extend(["Frequency", "Uncertainty"])
        self.template_path = Path(__file__).parent.joinpath("template.tex")
        self.template = ""
        self.__dict__.update(**kwargs)
        
    def parse_lin(self):
        """
        Function to parse the .lin file into a dictionary, which is subsequently
        fed into a Pandas DataFrame for LaTeX conversion.
        
        Raises
        ------
        ValueError
            If the number of quantum numbers expected for the molecule does not
            match the number found in the .lin file, including frequency and
            uncertainty columns.            
        """
        for line in self.contents:
            comment = comment_check(line)
            split_line = line.split()
            # Ignore the scan number or any other comment
            if comment is not None:
                split_line = split_line[:comment]
            expected = len(self.full_labels)
            if expected != len(split_line):
                raise ValueError(
                    f"Got {len(split_line)} values, not matching expected for {self.mol_type} ({expected})."
                    )
            transition = {
                self.full_labels[index]: value for index, value in enumerate(split_line)
                }
            for label in ["Frequency", "Uncertainty"]:
                transition[label] = float(transition[label])
            self.data.append(transition)

    def write_data(self, filepath=None):
        header = ["Transition", "Frequency", "Uncertainty"]
        header = " & ".join(header) + "\\\\ \n"
        try:
            self.template = Template(self.template_path.read_text())
        except FileNotFoundError:
            raise FileNotFoundError(f"Template was not found at {self.template_path}")
        if filepath is None:
            filepath = self.out_path
        if self.mol_type == "asymmetric":
            format_str = """${J'}_{{ {K_a'}, {K_c'} }} \\rightarrow {J''}_{{ {K_a''}, {K_c''} }}$ & {Frequency:,.4f} & {Uncertainty:,.4f} \\\\ \n"""
        elif self.mol_type == "symmetric":
            format_str = """${J'}_{{ {K'} }} \\rightarrow {J''}_{{ {K''} }}$ & {Frequency:,.4f} & {Uncertainty:,.4f} \\\\ \n"""
        elif self.mol_type == "linear":
            format_str = """${J'} \\rightarrow {J''}$ & {Frequency:,.4f} & {Uncertainty:,.4f} \\\\ \n"""
        else:
            raise ValueError(f"{self.mol_type} not a recognized format!")
        data = [format_str.format(**line) for line in self.data]
        filepath.write_text(
            self.template.safe_substitute({"data": "".join(data), "header": header})
        )


class AsymmetricTop(LinFile):
    def __init__(self, path, **kwargs):
        labels = ["J", "K_a", "K_c"]
        super().__init__(path, mol_type="asymmetric", labels=labels, **kwargs)
        

class SymmetricTop(LinFile):
    def __init__(self, path, **kwargs):
        labels = ["J", "K"]
        super().__init__(path, mol_type="symmetric", labels=labels, **kwargs)


class LinearTop(LinFile):
    def __init__(self, path, **kwargs):
        labels = ["J"]
        super().__init__(path, mol_type="linear", labels=labels, **kwargs)


def comment_check(line):
    for index, item in enumerate(line.split()):
        if "/" in item:
            return index
    else:
        return None
