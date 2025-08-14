from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLineEdit, QLabel, QPushButton, QComboBox, QTextEdit, QFormLayout,
    QSplitter, QSizePolicy, QScrollArea, QDialog
)
from PySide6.QtCore import Qt

from ..calculations import (
    calculate_molar_mass, parse_chemical_formula, PERIODIC_TABLE,
    convert_mass, convert_volume, convert_concentration, convert_pressure,
    celsius_to_kelvin, kelvin_to_celsius, celsius_to_fahrenheit, fahrenheit_to_celsius,
    calculate_density, calculate_molarity, calculate_moles, 
    calculate_mass_concentration, calculate_ppm, calculate_ppb,
    MASS_CONVERSIONS, VOLUME_CONVERSIONS, CONCENTRATION_CONVERSIONS, PRESSURE_CONVERSIONS
)


class PropertiesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Espaçamento entre seções
        layout.setContentsMargins(15, 15, 15, 15)  # Margens da janela
        
        # Create a scroll area for better navigation
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Chemical Formula Section
        formula_group = self.create_formula_section()
        content_layout.addWidget(formula_group)
        
        # Chemical Properties Section  
        properties_group = self.create_properties_section()
        content_layout.addWidget(properties_group)
        
        # Unit Conversions Section
        conversions_group = self.create_conversions_section()
        content_layout.addWidget(conversions_group)
        
        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def create_formula_section(self) -> QGroupBox:
        """Create the chemical formula and molar mass section."""
        group = QGroupBox("Fórmula Química e Massa Molar")
        layout = QFormLayout()
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(15)
        
        # Formula input
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("Ex: H2SO4, Ca(OH)2, K3[Fe(CN)6]")
        self.formula_input.setMinimumHeight(30)
        layout.addRow("Fórmula:", self.formula_input)
        
        # Calculate button
        calc_button = QPushButton("Calcular Massa Molar")
        calc_button.setMinimumHeight(35)
        calc_button.setStyleSheet("QPushButton { font-weight: bold; }")
        calc_button.clicked.connect(self.calculate_molar_mass)
        layout.addRow("", calc_button)
        
        # Results
        self.molar_mass_result = QLineEdit()
        self.molar_mass_result.setReadOnly(True)
        self.molar_mass_result.setMinimumHeight(30)
        self.molar_mass_result.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addRow("Massa Molar (g/mol):", self.molar_mass_result)
        
        self.composition_result = QTextEdit()
        self.composition_result.setReadOnly(True)
        self.composition_result.setMinimumHeight(150)
        # Removido setMaximumHeight para permitir redimensionamento
        self.composition_result.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Permitir expansão
        self.composition_result.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.composition_result.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.composition_result.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addRow("Composição:", self.composition_result)
        
        # Botão de tela cheia para composição
        btn_composition_fullscreen = QPushButton("Ver Composição em Tela Cheia")
        btn_composition_fullscreen.clicked.connect(lambda: self.show_fullscreen_result(self.composition_result, "Composição Química"))
        layout.addRow(btn_composition_fullscreen)
        
        group.setLayout(layout)
        group.setMinimumHeight(350)
        return group
    
    def create_properties_section(self) -> QGroupBox:
        """Create the chemical properties calculations section."""
        group = QGroupBox("Cálculos de Propriedades")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # === DENSIDADE ===
        density_group = QGroupBox("Densidade (ρ = massa ÷ volume)")
        density_layout = QGridLayout()
        density_layout.setVerticalSpacing(8)
        density_layout.setHorizontalSpacing(10)
        
        density_layout.addWidget(QLabel("Massa:"), 0, 0)
        self.density_mass = QLineEdit()
        self.density_mass.setPlaceholderText("Ex: 10")
        self.density_mass.setMinimumHeight(28)
        density_layout.addWidget(self.density_mass, 0, 1)
        
        self.density_mass_unit = QComboBox()
        self.density_mass_unit.addItems(list(MASS_CONVERSIONS.keys()))
        self.density_mass_unit.setCurrentText("g")
        self.density_mass_unit.setMinimumHeight(28)
        density_layout.addWidget(self.density_mass_unit, 0, 2)
        
        density_layout.addWidget(QLabel("Volume:"), 1, 0)
        self.density_volume = QLineEdit()
        self.density_volume.setPlaceholderText("Ex: 5")
        self.density_volume.setMinimumHeight(28)
        density_layout.addWidget(self.density_volume, 1, 1)
        
        self.density_volume_unit = QComboBox()
        self.density_volume_unit.addItems(list(VOLUME_CONVERSIONS.keys()))
        self.density_volume_unit.setCurrentText("mL")
        self.density_volume_unit.setMinimumHeight(28)
        density_layout.addWidget(self.density_volume_unit, 1, 2)
        
        density_calc_btn = QPushButton("Calcular Densidade")
        density_calc_btn.clicked.connect(self.calculate_density)
        density_calc_btn.setMinimumHeight(32)
        density_calc_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        density_layout.addWidget(density_calc_btn, 2, 0, 1, 3)
        
        density_layout.addWidget(QLabel("Resultado:"), 3, 0)
        self.density_result = QLineEdit()
        self.density_result.setReadOnly(True)
        self.density_result.setMinimumHeight(28)
        self.density_result.setStyleSheet("font-weight: bold; font-size: 12px;")
        density_layout.addWidget(self.density_result, 3, 1)
        density_layout.addWidget(QLabel("g/mL"), 3, 2)
        
        density_group.setLayout(density_layout)
        main_layout.addWidget(density_group)
        
        # === MOLARIDADE ===
        molarity_group = QGroupBox("Molaridade (M = mols ÷ volume)")
        molarity_layout = QGridLayout()
        molarity_layout.setVerticalSpacing(8)
        molarity_layout.setHorizontalSpacing(10)
        
        molarity_layout.addWidget(QLabel("Número de mols:"), 0, 0)
        self.molarity_moles = QLineEdit()
        self.molarity_moles.setPlaceholderText("Ex: 0.5")
        self.molarity_moles.setMinimumHeight(28)
        molarity_layout.addWidget(self.molarity_moles, 0, 1)
        molarity_layout.addWidget(QLabel("mol"), 0, 2)
        
        molarity_layout.addWidget(QLabel("Volume da solução:"), 1, 0)
        self.molarity_volume = QLineEdit()
        self.molarity_volume.setPlaceholderText("Ex: 500")
        self.molarity_volume.setMinimumHeight(28)
        molarity_layout.addWidget(self.molarity_volume, 1, 1)
        
        self.molarity_volume_unit = QComboBox()
        self.molarity_volume_unit.addItems(list(VOLUME_CONVERSIONS.keys()))
        self.molarity_volume_unit.setCurrentText("mL")
        self.molarity_volume_unit.setMinimumHeight(28)
        molarity_layout.addWidget(self.molarity_volume_unit, 1, 2)
        
        molarity_calc_btn = QPushButton("Calcular Molaridade")
        molarity_calc_btn.clicked.connect(self.calculate_molarity)
        molarity_calc_btn.setMinimumHeight(32)
        molarity_calc_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        molarity_layout.addWidget(molarity_calc_btn, 2, 0, 1, 3)
        
        molarity_layout.addWidget(QLabel("Resultado:"), 3, 0)
        self.molarity_result = QLineEdit()
        self.molarity_result.setReadOnly(True)
        self.molarity_result.setMinimumHeight(28)
        self.molarity_result.setStyleSheet("font-weight: bold; font-size: 12px;")
        molarity_layout.addWidget(self.molarity_result, 3, 1)
        molarity_layout.addWidget(QLabel("M"), 3, 2)
        
        molarity_group.setLayout(molarity_layout)
        main_layout.addWidget(molarity_group)
        
        # === NÚMERO DE MOLS ===
        moles_group = QGroupBox("Número de Mols (n = massa ÷ massa molar)")
        moles_layout = QGridLayout()
        moles_layout.setVerticalSpacing(8)
        moles_layout.setHorizontalSpacing(10)
        
        moles_layout.addWidget(QLabel("Massa da substância:"), 0, 0)
        self.moles_mass = QLineEdit()
        self.moles_mass.setPlaceholderText("Ex: 18")
        self.moles_mass.setMinimumHeight(28)
        moles_layout.addWidget(self.moles_mass, 0, 1)
        
        self.moles_mass_unit = QComboBox()
        self.moles_mass_unit.addItems(list(MASS_CONVERSIONS.keys()))
        self.moles_mass_unit.setCurrentText("g")
        self.moles_mass_unit.setMinimumHeight(28)
        moles_layout.addWidget(self.moles_mass_unit, 0, 2)
        
        moles_layout.addWidget(QLabel("Massa molar:"), 1, 0)
        self.moles_molar_mass = QLineEdit()
        self.moles_molar_mass.setPlaceholderText("Ex: 18.015 (use a seção acima)")
        self.moles_molar_mass.setMinimumHeight(28)
        moles_layout.addWidget(self.moles_molar_mass, 1, 1)
        moles_layout.addWidget(QLabel("g/mol"), 1, 2)
        
        moles_calc_btn = QPushButton("Calcular Número de Mols")
        moles_calc_btn.clicked.connect(self.calculate_moles)
        moles_calc_btn.setMinimumHeight(32)
        moles_calc_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        moles_layout.addWidget(moles_calc_btn, 2, 0, 1, 3)
        
        moles_layout.addWidget(QLabel("Resultado:"), 3, 0)
        self.moles_result = QLineEdit()
        self.moles_result.setReadOnly(True)
        self.moles_result.setMinimumHeight(28)
        self.moles_result.setStyleSheet("font-weight: bold; font-size: 12px;")
        moles_layout.addWidget(self.moles_result, 3, 1)
        moles_layout.addWidget(QLabel("mol"), 3, 2)
        
        moles_group.setLayout(moles_layout)
        main_layout.addWidget(moles_group)
        
        group.setLayout(main_layout)
        group.setMinimumHeight(500)
        return group
    
    def create_conversions_section(self) -> QGroupBox:
        """Create the unit conversions section."""
        group = QGroupBox("Conversões de Unidades")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # === CONVERSÃO DE MASSA ===
        mass_group = QGroupBox("Conversão de Massa")
        mass_layout = QGridLayout()
        mass_layout.setVerticalSpacing(8)
        mass_layout.setHorizontalSpacing(10)
        
        mass_layout.addWidget(QLabel("Valor:"), 0, 0)
        self.mass_value = QLineEdit()
        self.mass_value.setPlaceholderText("Ex: 1000")
        self.mass_value.setMinimumHeight(28)
        mass_layout.addWidget(self.mass_value, 0, 1)
        
        mass_layout.addWidget(QLabel("De:"), 0, 2)
        self.mass_from = QComboBox()
        self.mass_from.addItems(list(MASS_CONVERSIONS.keys()))
        self.mass_from.setCurrentText("mg")
        self.mass_from.setMinimumHeight(28)
        mass_layout.addWidget(self.mass_from, 0, 3)
        
        mass_layout.addWidget(QLabel("Para:"), 0, 4)
        self.mass_to = QComboBox()
        self.mass_to.addItems(list(MASS_CONVERSIONS.keys()))
        self.mass_to.setCurrentText("g")
        self.mass_to.setMinimumHeight(28)
        mass_layout.addWidget(self.mass_to, 0, 5)
        
        mass_convert_btn = QPushButton("Converter")
        mass_convert_btn.clicked.connect(self.convert_mass)
        mass_convert_btn.setMinimumHeight(32)
        mass_convert_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        mass_layout.addWidget(mass_convert_btn, 1, 0, 1, 2)
        
        mass_layout.addWidget(QLabel("Resultado:"), 1, 2)
        self.mass_result = QLineEdit()
        self.mass_result.setReadOnly(True)
        self.mass_result.setMinimumHeight(28)
        self.mass_result.setStyleSheet("font-weight: bold; font-size: 12px;")
        mass_layout.addWidget(self.mass_result, 1, 3, 1, 3)
        
        mass_group.setLayout(mass_layout)
        main_layout.addWidget(mass_group)
        
        # === CONVERSÃO DE VOLUME ===
        volume_group = QGroupBox("Conversão de Volume")
        volume_layout = QGridLayout()
        volume_layout.setVerticalSpacing(8)
        volume_layout.setHorizontalSpacing(10)
        
        volume_layout.addWidget(QLabel("Valor:"), 0, 0)
        self.volume_value = QLineEdit()
        self.volume_value.setPlaceholderText("Ex: 1000")
        self.volume_value.setMinimumHeight(28)
        volume_layout.addWidget(self.volume_value, 0, 1)
        
        volume_layout.addWidget(QLabel("De:"), 0, 2)
        self.volume_from = QComboBox()
        self.volume_from.addItems(list(VOLUME_CONVERSIONS.keys()))
        self.volume_from.setCurrentText("mL")
        self.volume_from.setMinimumHeight(28)
        volume_layout.addWidget(self.volume_from, 0, 3)
        
        volume_layout.addWidget(QLabel("Para:"), 0, 4)
        self.volume_to = QComboBox()
        self.volume_to.addItems(list(VOLUME_CONVERSIONS.keys()))
        self.volume_to.setCurrentText("L")
        self.volume_to.setMinimumHeight(28)
        volume_layout.addWidget(self.volume_to, 0, 5)
        
        volume_convert_btn = QPushButton("Converter")
        volume_convert_btn.clicked.connect(self.convert_volume)
        volume_convert_btn.setMinimumHeight(32)
        volume_convert_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        volume_layout.addWidget(volume_convert_btn, 1, 0, 1, 2)
        
        volume_layout.addWidget(QLabel("Resultado:"), 1, 2)
        self.volume_result = QLineEdit()
        self.volume_result.setReadOnly(True)
        self.volume_result.setMinimumHeight(28)
        self.volume_result.setStyleSheet("font-weight: bold; font-size: 12px;")
        volume_layout.addWidget(self.volume_result, 1, 3, 1, 3)
        
        volume_group.setLayout(volume_layout)
        main_layout.addWidget(volume_group)
        
        # === CONVERSÃO DE TEMPERATURA ===
        temp_group = QGroupBox("Conversão de Temperatura")
        temp_layout = QGridLayout()
        temp_layout.setVerticalSpacing(8)
        temp_layout.setHorizontalSpacing(10)
        
        temp_layout.addWidget(QLabel("Valor:"), 0, 0)
        self.temp_value = QLineEdit()
        self.temp_value.setPlaceholderText("Ex: 25")
        self.temp_value.setMinimumHeight(28)
        temp_layout.addWidget(self.temp_value, 0, 1)
        
        temp_layout.addWidget(QLabel("De:"), 0, 2)
        self.temp_from = QComboBox()
        self.temp_from.addItems(["°C", "K", "°F"])
        self.temp_from.setCurrentText("°C")
        self.temp_from.setMinimumHeight(28)
        temp_layout.addWidget(self.temp_from, 0, 3)
        
        temp_layout.addWidget(QLabel("Para:"), 0, 4)
        self.temp_to = QComboBox()
        self.temp_to.addItems(["°C", "K", "°F"])
        self.temp_to.setCurrentText("K")
        self.temp_to.setMinimumHeight(28)
        temp_layout.addWidget(self.temp_to, 0, 5)
        
        temp_convert_btn = QPushButton("Converter")
        temp_convert_btn.clicked.connect(self.convert_temperature)
        temp_convert_btn.setMinimumHeight(32)
        temp_convert_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        temp_layout.addWidget(temp_convert_btn, 1, 0, 1, 2)
        
        temp_layout.addWidget(QLabel("Resultado:"), 1, 2)
        self.temp_result = QLineEdit()
        self.temp_result.setReadOnly(True)
        self.temp_result.setMinimumHeight(28)
        self.temp_result.setStyleSheet("font-weight: bold; font-size: 12px;")
        temp_layout.addWidget(self.temp_result, 1, 3, 1, 3)
        
        temp_group.setLayout(temp_layout)
        main_layout.addWidget(temp_group)
        
        group.setLayout(main_layout)
        group.setMinimumHeight(350)
        return group
    
    def calculate_molar_mass(self):
        """Calculate molar mass from chemical formula."""
        try:
            formula = self.formula_input.text().strip()
            if not formula:
                self.molar_mass_result.setText("Digite uma fórmula")
                self.composition_result.setText("")
                return
            
            molar_mass = calculate_molar_mass(formula)
            self.molar_mass_result.setText(f"{molar_mass:.3f}")
            
            # Show detailed composition
            elements = parse_chemical_formula(formula)
            composition_text = f"Composição de {formula}:\n\n"
            
            total_mass = 0.0
            for element, count in elements.items():
                atomic_mass = PERIODIC_TABLE[element]
                element_mass = atomic_mass * count
                total_mass += element_mass
                
                composition_text += f"{element}: {count} × {atomic_mass:.3f} = {element_mass:.3f} g/mol\n"
            
            composition_text += f"\nMassa Molar Total: {total_mass:.3f} g/mol"
            
            # Show percentage composition
            composition_text += f"\n\nComposição Percentual:\n"
            for element, count in elements.items():
                atomic_mass = PERIODIC_TABLE[element]
                element_mass = atomic_mass * count
                percentage = (element_mass / total_mass) * 100
                composition_text += f"{element}: {percentage:.2f}%\n"
            
            self.composition_result.setText(composition_text)
            
        except Exception as e:
            self.molar_mass_result.setText("Erro")
            self.composition_result.setText(f"Erro: {str(e)}")
    
    def calculate_density(self):
        """Calculate density."""
        try:
            mass = float(self.density_mass.text())
            volume = float(self.density_volume.text())
            mass_unit = self.density_mass_unit.currentText()
            volume_unit = self.density_volume_unit.currentText()
            
            density = calculate_density(mass, volume, mass_unit, volume_unit)
            self.density_result.setText(f"{density:.6f}")
            
        except ValueError as e:
            self.density_result.setText(f"Erro: {str(e)}")
        except Exception:
            self.density_result.setText("Erro: Valores inválidos")
    
    def calculate_molarity(self):
        """Calculate molarity."""
        try:
            moles = float(self.molarity_moles.text())
            volume = float(self.molarity_volume.text())
            volume_unit = self.molarity_volume_unit.currentText()
            
            molarity = calculate_molarity(moles, volume, volume_unit)
            self.molarity_result.setText(f"{molarity:.6f}")
            
        except ValueError as e:
            self.molarity_result.setText(f"Erro: {str(e)}")
        except Exception:
            self.molarity_result.setText("Erro: Valores inválidos")
    
    def calculate_moles(self):
        """Calculate number of moles."""
        try:
            mass = float(self.moles_mass.text())
            molar_mass = float(self.moles_molar_mass.text())
            mass_unit = self.moles_mass_unit.currentText()
            
            moles = calculate_moles(mass, molar_mass, mass_unit)
            self.moles_result.setText(f"{moles:.6f}")
            
        except ValueError as e:
            self.moles_result.setText(f"Erro: {str(e)}")
        except Exception:
            self.moles_result.setText("Erro: Valores inválidos")
    
    def convert_mass(self):
        """Convert mass units."""
        try:
            value = float(self.mass_value.text())
            from_unit = self.mass_from.currentText()
            to_unit = self.mass_to.currentText()
            
            result = convert_mass(value, from_unit, to_unit)
            self.mass_result.setText(f"{result:.9f}")
            
        except ValueError as e:
            self.mass_result.setText(f"Erro: {str(e)}")
        except Exception:
            self.mass_result.setText("Erro: Valor inválido")
    
    def convert_volume(self):
        """Convert volume units."""
        try:
            value = float(self.volume_value.text())
            from_unit = self.volume_from.currentText()
            to_unit = self.volume_to.currentText()
            
            result = convert_volume(value, from_unit, to_unit)
            self.volume_result.setText(f"{result:.9f}")
            
        except ValueError as e:
            self.volume_result.setText(f"Erro: {str(e)}")
        except Exception:
            self.volume_result.setText("Erro: Valor inválido")
    
    def convert_temperature(self):
        """Convert temperature units."""
        try:
            value = float(self.temp_value.text())
            from_unit = self.temp_from.currentText()
            to_unit = self.temp_to.currentText()
            
            if from_unit == to_unit:
                result = value
            elif from_unit == "°C":
                if to_unit == "K":
                    result = celsius_to_kelvin(value)
                elif to_unit == "°F":
                    result = celsius_to_fahrenheit(value)
            elif from_unit == "K":
                if to_unit == "°C":
                    result = kelvin_to_celsius(value)
                elif to_unit == "°F":
                    celsius = kelvin_to_celsius(value)
                    result = celsius_to_fahrenheit(celsius)
            elif from_unit == "°F":
                if to_unit == "°C":
                    result = fahrenheit_to_celsius(value)
                elif to_unit == "K":
                    celsius = fahrenheit_to_celsius(value)
                    result = celsius_to_kelvin(celsius)
            
            self.temp_result.setText(f"{result:.3f}")
            
        except Exception:
            self.temp_result.setText("Erro: Valor inválido")

    def show_fullscreen_result(self, source_widget: QTextEdit, title: str):
        """Mostra o resultado em uma janela de tela cheia."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"HeisenLab - {title}")
        dialog.setWindowState(Qt.WindowMaximized)  # Maximizar janela
        
        layout = QVBoxLayout(dialog)
        
        # Título
        title_label = QLabel(f"{title}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Área de texto expandida
        fullscreen_text = QTextEdit()
        fullscreen_text.setReadOnly(True)
        fullscreen_text.setPlainText(source_widget.toPlainText())
        fullscreen_text.setStyleSheet("""
            QTextEdit {
                font-weight: bold; 
                font-family: 'Courier New', monospace; 
                font-size: 12px;
                padding: 15px;
                border: 2px solid #27ae60;
                border-radius: 8px;
            }
        """)
        layout.addWidget(fullscreen_text)
        
        # Botões
        button_layout = QHBoxLayout()
        
        # Botão copiar
        btn_copy = QPushButton("Copiar para Área de Transferência")
        btn_copy.clicked.connect(lambda: self.copy_to_clipboard(fullscreen_text.toPlainText()))
        button_layout.addWidget(btn_copy)
        
        # Botão salvar
        btn_save = QPushButton("Salvar em Arquivo")
        btn_save.clicked.connect(lambda: self.save_to_file(fullscreen_text.toPlainText(), title))
        button_layout.addWidget(btn_save)
        
        button_layout.addStretch()
        
        # Botão fechar
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(dialog.close)
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
        
        dialog.exec()

    def copy_to_clipboard(self, text: str):
        """Copia o texto para a área de transferência."""
        try:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Feedback visual
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Sucesso")
            msg.setText("Resultados copiados para a área de transferência!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
        except Exception as e:
            print(f"Erro ao copiar: {e}")

    def save_to_file(self, text: str, title: str):
        """Salva o texto em um arquivo."""
        try:
            from PySide6.QtWidgets import QFileDialog
            import datetime
            
            # Sugerir nome do arquivo com timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            suggested_name = f"HeisenLab_{title.replace(' ', '_')}_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Salvar {title}",
                suggested_name,
                "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(f"HeisenLab - {title}\n")
                    file.write("=" * 50 + "\n")
                    file.write(f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    file.write("=" * 50 + "\n\n")
                    file.write(text)
                
                # Feedback visual
                from PySide6.QtWidgets import QMessageBox
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Sucesso")
                msg.setText(f"Arquivo salvo com sucesso!\n\n{file_path}")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Erro")
            msg.setText(f"Erro ao salvar arquivo:\n{str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
