from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QGroupBox,
    QScrollArea,
    QTextEdit,
    QDialog,
)

from ..calculations import (
    dilution_c1v1_c2v2,
    ph_strong_acid,
    poh_strong_base,
    ph_from_poh,
    absorbance_beer_lambert,
    calculate_ka_from_ph,
    calculate_pka_from_ka,
    calculate_ka_from_pka,
    calculate_kb_from_poh,
    calculate_pkb_from_kb,
    calculate_kb_from_pkb,
    ka_kb_relationship,
)


class CalculationsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface principal."""
        # Scroll area para melhor organização
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget principal
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Seções
        layout.addWidget(self.create_dilution_section())
        layout.addWidget(self.create_ka_kb_section())
        layout.addStretch()
        
        scroll.setWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    def create_dilution_section(self):
        """Seção de cálculos de diluição."""
        group = QGroupBox("Cálculos de Diluição (C₁V₁ = C₂V₂)")
        layout = QVBoxLayout(group)
        
        # Entradas
        form_layout = QFormLayout()
        
        self.c1_input = QLineEdit()
        self.c1_input.setPlaceholderText("Concentração inicial")
        form_layout.addRow("C₁ (mol/L):", self.c1_input)
        
        self.v1_input = QLineEdit()
        self.v1_input.setPlaceholderText("Volume inicial")
        form_layout.addRow("V₁ (L):", self.v1_input)
        
        self.c2_input = QLineEdit()
        self.c2_input.setPlaceholderText("Concentração final")
        form_layout.addRow("C₂ (mol/L):", self.c2_input)
        
        self.v2_input = QLineEdit()
        self.v2_input.setPlaceholderText("Volume final")
        form_layout.addRow("V₂ (L):", self.v2_input)
        
        layout.addLayout(form_layout)
        
        # Nota
        note = QLabel("Informe 3 valores e deixe 1 vazio para calcular")
        note.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        layout.addWidget(note)
        
        # Botão e resultado
        btn_dilution = QPushButton("Calcular Diluição")
        btn_dilution.clicked.connect(self.calculate_dilution)
        layout.addWidget(btn_dilution)
        
        self.dilution_result = QTextEdit()
        self.dilution_result.setMinimumHeight(60)  # Altura mínima em vez de máxima
        self.dilution_result.setStyleSheet("font-weight: bold; font-family: monospace;")
        layout.addWidget(self.dilution_result)
        
        # Botão de tela cheia
        btn_dilution_fullscreen = QPushButton("Ver em Tela Cheia")
        btn_dilution_fullscreen.clicked.connect(lambda: self.show_fullscreen_result(self.dilution_result, "Cálculo de Diluição"))
        layout.addWidget(btn_dilution_fullscreen)
        
        return group
