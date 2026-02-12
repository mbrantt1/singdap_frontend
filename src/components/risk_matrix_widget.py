from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QComboBox, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QBrush


class RiskMatrixWidget(QWidget):
    def __init__(self, parent=None, read_only=False):
        super().__init__(parent)
        self.read_only = read_only
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
        
        # Connect click for description preview
        self.table.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.table)

    def _on_item_clicked(self, item):
        """Show full description in a dialog if the description column is clicked."""
        if item.column() == 1: # Descripción column
            text = item.text()
            if text:
                msg = QMessageBox(self)
                msg.setWindowTitle("Descripción del Ámbito")
                msg.setText(text)
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                    }
                    QLabel {
                        color: #1e293b;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #3b82f6;
                        color: white;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-weight: bold;
                    }
                """)
                msg.exec()

    # --------------------------------------------------
    # Precargar los 9 ámbitos (desde EIPD)
    # --------------------------------------------------
    def preload_ambitos(self, ambitos: list[str], descriptions: dict = None):
        self.table.setRowCount(len(ambitos))
        descriptions = descriptions or {}
        
        # UI Tweak: Stylesheet for Table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #1e293b;
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
        row_height = 60 # Reduced back to standard height
        header_height = self.table.horizontalHeader().height() if self.table.horizontalHeader().height() > 0 else 40
        total_height = (row_height * len(ambitos)) + header_height + 40 
        self.table.setMinimumHeight(total_height)
        
        self.table.verticalHeader().setDefaultSectionSize(row_height) 
        self.table.setWordWrap(False) # Disable word wrap for cleaner look, use elide
        
        # Column Widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(1, header.ResizeMode.Stretch) # Description takes space
        header.setSectionResizeMode(3, header.ResizeMode.Stretch) # Risk takes space
        
        # Fixed widths
        self.table.setColumnWidth(2, 140) # Nivel desarrollo
        self.table.setColumnWidth(4, 130) # Prob
        self.table.setColumnWidth(5, 130) # Impacto
        self.table.setColumnWidth(6, 140) # Nivel Riesgo

        for row, ambito in enumerate(ambitos):
            # 0: Ámbito (Static Title)
            item_ambito = QTableWidgetItem(ambito)
            item_ambito.setFlags(item_ambito.flags() & ~Qt.ItemIsEditable)
            item_ambito.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft) 
            item_ambito.setFont(self._bold_font())
            item_ambito.setForeground(QColor("#0f172a")) # Darker
            self.table.setItem(row, 0, item_ambito)

            # 1: Descripción (Static text from eipd.json)
            desc_text = descriptions.get(ambito, "")
            item_desc = QTableWidgetItem(desc_text)
            item_desc.setFlags(item_desc.flags() & ~Qt.ItemIsEditable)
            item_desc.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            item_desc.setForeground(QColor("#475569")) # Slate 600
            item_desc.setToolTip("Haga clic para ver descripción completa")
            self.table.setItem(row, 1, item_desc)

            # 2: Nivel desarrollo - ALWAYS INTERACTIVE (Not in Section 1)
            nivel_combo = QComboBox()
            nivel_combo.addItems(["Inicial", "Intermedio", "Avanzado"])
            nivel_combo.setStyleSheet(self._combo_style())
            self.table.setCellWidget(row, 2, nivel_combo)

            # 3: Riesgo transversal - ALWAYS INTERACTIVE (Not in Section 1)
            riesgo_edit = QTextEdit()
            riesgo_edit.setPlaceholderText("Describa riesgos...")
            riesgo_edit.setStyleSheet(self._input_custom_style())
            self.table.setCellWidget(row, 3, riesgo_edit)

            # 4: Probabilidad - SYNCED (Read-only if read_only=True)
            if self.read_only:
                item = QTableWidgetItem("...")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#1e293b"))
                self.table.setItem(row, 4, item)
            else:
                prob_combo = QComboBox()
                prob_combo.addItems(["Despreciable", "Limitado", "Significativo", "Máximo"])
                prob_combo.setStyleSheet(self._combo_style())
                self.table.setCellWidget(row, 4, prob_combo)

            # 5: Impacto - SYNCED
            if self.read_only:
                item = QTableWidgetItem("...")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#1e293b"))
                self.table.setItem(row, 5, item)
            else:
                impact_combo = QComboBox()
                impact_combo.addItems(["Despreciable", "Limitado", "Significativo", "Máximo"])
                impact_combo.setStyleSheet(self._combo_style())
                self.table.setCellWidget(row, 5, impact_combo)

            # 6: Nivel de riesgo - SYNCED
            if self.read_only:
                self._apply_risk_color(row, "Pendiente")
            else:
                riesgo_combo = QComboBox()
                riesgo_combo.addItems(["Bajo", "Medio", "Alto", "Muy Alto"])
                riesgo_combo.setStyleSheet(self._combo_style())
                self.table.setCellWidget(row, 6, riesgo_combo)
        

    def update_row(self, row_index, data):
        """Update a row with fresh data from Section 1."""
        if row_index < 0 or row_index >= self.table.rowCount():
            return

        if self.read_only:
            # Update items directly (textual summary)
            # Probabilidad
            val_prob = data.get("probabilidad") or "..."
            item_prob = QTableWidgetItem(str(val_prob))
            item_prob.setTextAlignment(Qt.AlignCenter)
            item_prob.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_prob.setForeground(QColor("#1e293b"))
            self.table.setItem(row_index, 4, item_prob)

            # Impacto
            val_imp = data.get("impacto") or "..."
            item_imp = QTableWidgetItem(str(val_imp))
            item_imp.setTextAlignment(Qt.AlignCenter)
            item_imp.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_imp.setForeground(QColor("#1e293b"))
            self.table.setItem(row_index, 5, item_imp)

            # Nivel Riesgo - Use the Label Widget via _apply_risk_color
            val_risk = data.get("nivel_riesgo") or "Pendiente"
            self._apply_risk_color(row_index, val_risk)
            
        else:
            # Update widgets (standard editable mode)
            # (Leaving original logic here for completeness)
            widget_prob = self.table.cellWidget(row_index, 4)
            if isinstance(widget_prob, QComboBox):
                self._set_combo_text(widget_prob, data.get("probabilidad"))

            widget_imp = self.table.cellWidget(row_index, 5)
            if isinstance(widget_imp, QComboBox):
                self._set_combo_text(widget_imp, data.get("impacto"))

            widget_risk = self.table.cellWidget(row_index, 6)
            if isinstance(widget_risk, QComboBox):
                self._set_combo_text(widget_risk, data.get("nivel_riesgo"))

    def _apply_risk_color(self, row, level):
        """Creates a styled QLabel for the risk level cell to ensure visibility on macOS."""
        colors = {
            "Bajo": "#22c55e", # Green
            "Medio": "#eab308", # Yellow
            "Alto": "#f97316", # Orange
            "Muy Alto": "#ef4444" # Red
        }
        
        bg_color = colors.get(level, "#ffffff")
        text_color = "white" if level in colors else "#64748b"
        border_color = bg_color if level in colors else "#e2e8f0"
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        
        lbl = QLabel(str(level))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                padding: 2px;
            }}
        """)
        layout.addWidget(lbl)
        self.table.setCellWidget(row, 6, container)

    def _bold_font(self):
        f = QFont()
        f.setBold(True)
        return f

    def _read_only_style(self):
        return """
            QTextEdit {
                border: 0px;
                background-color: transparent;
                color: #475569;
            }
        """

    def _input_custom_style(self):
        return """
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 4px;
                background-color: #ffffff;
                font-size: 12px;
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
