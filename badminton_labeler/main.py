"""
Entry point — wires View + Presenter and launches the app.
"""
import sys
from PyQt5.QtWidgets import QApplication

from badminton_labeler.views.main_window import MainWindow
from badminton_labeler.presenters.main_presenter import MainPresenter


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    view      = MainWindow()
    presenter = MainPresenter(view)
    view.set_presenter(presenter)

    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
