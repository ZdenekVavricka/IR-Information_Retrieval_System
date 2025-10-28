import sys

from eval.evaluate import run_evaluation
from gui.gui import run_gui
from utils.utils import PrintSave

# Main function
def main(argv):
    if "-test" in argv:
        run_evaluation()
    else:
        run_gui()

if __name__ == '__main__':
    sys.stdout = PrintSave("../log/log.txt")

    main(sys.argv)

    sys.stdout = sys.stdout.stdout
