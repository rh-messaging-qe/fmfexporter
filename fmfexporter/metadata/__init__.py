import os
import fmf.cli
os.chdir(os.path.dirname(__file__))
PATH = os.getcwd()


def show_scheme():
    fmf.cli.main("fmf show", PATH)



