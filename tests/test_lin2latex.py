from lin2latex import __version__
from lin2latex.main import LinearTop, AsymmetricTop


def test_version():
    assert __version__ == '0.1.0'


def run_linear_top():
    print("Running LinearTop test.")
    molecule = LinearTop("linear.lin")
    molecule.parse_lin()
    molecule.write_data()
    
def run_asymmetric_top():
    print("Running AsymmetricTop test.")
    molecule = AsymmetricTop("asymmetric.lin")
    molecule.parse_lin()
    molecule.write_data()


if __name__ == "__main__":
    run_linear_top()
    run_asymmetric_top()
    