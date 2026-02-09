from PySide6.QtWidgets import (
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QTextEdit,
    QVBoxLayout
)
from PySide6.QtCore import Qt


class RiskMatrixWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(9, 7, self)
        self.table.setHorizontalHeaderLabels([
            "Ámbito",
            "Descripción",
            "Nivel desarrollo",
            "Riesgo transversal",
            "Probabilidad",
            "Impacto",
            "Nivel de riesgo"
        ])

        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

    # --------------------------------------------------
    # Precargar los 9 ámbitos (desde EIPD)
    # --------------------------------------------------
    def preload_ambitos(self, ambitos: list[str]):
        self.table.setRowCount(len(ambitos))
        
        # UI Tweak: Stylesheet for Table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e2e8f0;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                selection-background-color: #f1f5f9;
                selection-color: #0f172a;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                border: 0px;
                border-bottom: 2px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                font-weight: bold;
                color: #475569;
            }
            QTableCornerButton::section {
                background-color: #f8fafc;
                border: 0px;
                border-bottom: 2px solid #e2e8f0;
            }
        """)

        # Dimensions
        row_height = 70
        header_height = self.table.horizontalHeader().height() if self.table.horizontalHeader().height() > 0 else 40
        total_height = (row_height * len(ambitos)) + header_height + 20 # +20 buffer
        self.table.setMinimumHeight(total_height)
        
        self.table.verticalHeader().setDefaultSectionSize(row_height) 
        self.table.setWordWrap(True)
        
        # Column Widths
        # 0: Ambito, 1: Desc, 2: Nivel, 3: Riesgo, 4: Prob, 5: Imp, 6: Nivel Riesgo
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(1, header.ResizeMode.Stretch) # Description takes space
        header.setSectionResizeMode(3, header.ResizeMode.Stretch) # Risk takes space
        
        # Fixed widths for combos/status
        self.table.setColumnWidth(2, 140) # Nivel desarrollo
        self.table.setColumnWidth(4, 130) # Prob
        self.table.setColumnWidth(5, 130) # Impacto
        self.table.setColumnWidth(6, 140) # Nivel Riesgo - Wider for "Muy Alto"

        for row, ambito in enumerate(ambitos):
            item = QTableWidgetItem(ambito)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            # Center vertically
            item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft) 
            self.table.setItem(row, 0, item)

            # Descripción
            desc_edit = QTextEdit()
            desc_edit.setPlaceholderText("Describa la situación...")
            desc_edit.setStyleSheet(self._input_style())
            self.table.setCellWidget(row, 1, desc_edit)

            # Nivel desarrollo
            nivel_combo = QComboBox()
            nivel_combo.addItems(["Inicial", "Intermedio", "Avanzado"])
            nivel_combo.setStyleSheet(self._combo_style())
            self.table.setCellWidget(row, 2, nivel_combo)

            # Riesgo transversal
            riesgo_edit = QTextEdit()
            riesgo_edit.setPlaceholderText("Describa riesgos...")
            riesgo_edit.setStyleSheet(self._input_style())
            self.table.setCellWidget(row, 3, riesgo_edit)

            # Probabilidad
            prob_combo = QComboBox()
            prob_combo.addItems(["Despreciable", "Limitado", "Significativo", "Máximo"])
            prob_combo.setStyleSheet(self._combo_style())
            self.table.setCellWidget(row, 4, prob_combo)

            # Impacto
            impact_combo = QComboBox()
            impact_combo.addItems(["Despreciable", "Limitado", "Significativo", "Máximo"])
            impact_combo.setStyleSheet(self._combo_style())
            self.table.setCellWidget(row, 5, impact_combo)

            # Nivel de riesgo - Ahora editable
            riesgo_combo = QComboBox()
            riesgo_combo.addItems(["Bajo", "Medio", "Alto", "Muy Alto"])
            riesgo_combo.setStyleSheet(self._combo_style())
            self.table.setCellWidget(row, 6, riesgo_combo)

    def _input_style(self):
        return """
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 4px;
                background-color: #ffffff;
            }
            QTextEdit:focus {
                border: 1px solid #3b82f6;
            }
        """

    def _combo_style(self):
        return """
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 2px 4px;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: 0px;
            }
        """

    # --------------------------------------------------
    # Obtener data (para POST más adelante)
    # --------------------------------------------------
    def get_data(self):
        data = []

        for row in range(self.table.rowCount()):
            row_data = {
                "ambito": self.table.item(row, 0).text() if self.table.item(row, 0) else None,
                "descripcion": self._get_text(row, 1),
                "nivel_desarrollo": self._get_combo(row, 2),
                "riesgo_transversal": self._get_text(row, 3),
                "probabilidad": self._get_combo(row, 4),
                "impacto": self._get_combo(row, 5),
                "nivel_riesgo": self._get_combo(row, 6), # Now a combo
            }
            data.append(row_data)

        return data

    def set_data(self, data):
        if not data or not isinstance(data, list):
            return

        # Map by ambito name for easy lookup
        data_map = {item.get("ambito"): item for item in data if item.get("ambito")}

        for row in range(self.table.rowCount()):
            item_ambito = self.table.item(row, 0)
            if not item_ambito:
                continue
            
            # Reset combos to -1 first? Or just let them be default (0) if not found?
            # Default is 0 (first item). Let's keep it safe.

            ambito_name = item_ambito.text()
            if ambito_name in data_map:
                row_data = data_map[ambito_name]
                
                # Descripcion
                widget_desc = self.table.cellWidget(row, 1)
                if isinstance(widget_desc, QTextEdit):
                    widget_desc.setText(row_data.get("descripcion", ""))

                # Nivel desarrollo
                widget_nivel = self.table.cellWidget(row, 2)
                if isinstance(widget_nivel, QComboBox):
                    self._set_combo_text(widget_nivel, row_data.get("nivel_desarrollo"))

                # Riesgo transversal
                widget_riesgo = self.table.cellWidget(row, 3)
                if isinstance(widget_riesgo, QTextEdit):
                    widget_riesgo.setText(row_data.get("riesgo_transversal", ""))

                # Probabilidad
                widget_prob = self.table.cellWidget(row, 4)
                if isinstance(widget_prob, QComboBox):
                    self._set_combo_text(widget_prob, row_data.get("probabilidad"))

                # Impacto
                widget_imp = self.table.cellWidget(row, 5)
                if isinstance(widget_imp, QComboBox):
                    self._set_combo_text(widget_imp, row_data.get("impacto"))
                    
                # Nivel Riesgo
                widget_risk = self.table.cellWidget(row, 6)
                if isinstance(widget_risk, QComboBox):
                   self._set_combo_text(widget_risk, row_data.get("nivel_riesgo"))

    def _set_combo_text(self, combo, text):
        if not text:
            combo.setCurrentIndex(-1)
            return
        index = combo.findText(str(text))
        if index != -1:
            combo.setCurrentIndex(index)
        else:
            # Try setting as currentText if editable (default combos usually aren't but good fallback)
            # Or just ignore if not found
            pass

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def _get_text(self, row, col):
        widget = self.table.cellWidget(row, col)
        if isinstance(widget, QTextEdit):
            return widget.toPlainText()
        return None

    def _get_combo(self, row, col):
        widget = self.table.cellWidget(row, col)
        if isinstance(widget, QComboBox):
            return widget.currentText()
        return None
