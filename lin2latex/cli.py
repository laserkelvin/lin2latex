
#!/usr/bin/env python

import click
from lin2latex.main import LinearTop, AsymmetricTop, SymmetricTop


@click.option(
    "-m", "--mol_type", prompt=True, 
    type=click.Choice(["asymmetric", "symmetric", "linear"])
    )
@click.option("-o", "--outpath", default=None)
@click.argument("filepath", type=click.Path(exists=True))
@click.command()
def run_lin2latex(filepath, mol_type, outpath, **kwargs):
    if mol_type == "asymmetric":
        func = AsymmetricTop
    elif mol_type == "symmetric":
        func = SymmetricTop
    elif mol_type == "linear":
        func = LinearTop
    else:
        raise Exception(f"{mol_type} is not implemented!")
    molecule = func(filepath, **kwargs)
    molecule.parse_lin()
    molecule.write_data(outpath)


if __name__ == "__main__":
    run_lin2latex()
