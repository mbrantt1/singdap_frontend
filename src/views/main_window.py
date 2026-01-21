from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from src.views.sidebar import Sidebar
from src.views.activos.activos_view import ActivosView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SINGDAP - Sistema de Inventario")
        self.setMinimumSize(1200, 720)

        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.activos_view = ActivosView()

        # 🔴 ORDEN IMPORTANTE
        layout.addWidget(self.sidebar)
        layout.addWidget(self.activos_view)

        # 🔴 FIX CLAVE: stretch controlado
        layout.setStretch(0, 0)  # sidebar NO se estira
        layout.setStretch(1, 1)  # contenido sí

        container.setLayout(layout)
        self.setCentralWidget(container)
