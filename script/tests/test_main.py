import pytest
from src.main import hello

def test_print_statement(capfd):
    hello()
    out, err = capfd.readouterr()
    assert "x" in out
