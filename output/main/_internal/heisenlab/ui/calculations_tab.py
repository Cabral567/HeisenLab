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
    def calculate_beer_lambert(self):
        """Calcula absorbância usando a Lei de Beer-Lambert e exibe o resultado."""
        try:
            conc = float(self.beer_conc_input.text().strip())
            epsilon = float(self.beer_epsilon_input.text().strip())
            path = float(self.beer_path_input.text().strip())
            absorbance = absorbance_beer_lambert(conc, epsilon, path)
            self.beer_result.setText(f"Absorbância = {absorbance:.3f}")
        except Exception as e:
            self.beer_result.setText(f"Erro: {e}")
    def calculate_ka_kb_relation(self):
        """Calcula a relação Ka × Kb = Kw e exibe o resultado."""
        valor = self.ka_kb_input.text().strip()
        tipo = self.ka_kb_type.currentText()
        try:
            num = float(valor)
            kw = 1e-14
            if tipo == "Ka":
                kb = kw / num
                resultado = f"Kb = Kw / Ka = {kw} / {num} = {kb:.3e}"
            else:
                ka = kw / num
                resultado = f"Ka = Kw / Kb = {kw} / {num} = {ka:.3e}"
            self.ka_kb_relation_result.setText(resultado)
        except Exception as e:
            self.ka_kb_relation_result.setText(f"Erro: {e}")
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
        layout.addWidget(self.create_ph_section())
        layout.addWidget(self.create_acid_base_section())
        layout.addWidget(self.create_spectrophotometry_section())
        layout.addStretch()
        
        scroll.setWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    def create_dilution_section(self):
        """Seção de cálculos de diluição."""
        group = QGroupBox("Diluição (C₁V₁ = C₂V₂)")
        layout = QVBoxLayout(group)

        # Formulário
        form_layout = QFormLayout()

        self.c1_input = QLineEdit()
        self.c1_input.setPlaceholderText("mol/L (deixe vazio para calcular)")
        self.c1_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("C₁:", self.c1_input)

        self.v1_input = QLineEdit()
        self.v1_input.setPlaceholderText("L (deixe vazio para calcular)")
        self.v1_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("V₁:", self.v1_input)

        self.c2_input = QLineEdit()
        self.c2_input.setPlaceholderText("mol/L (deixe vazio para calcular)")
        self.c2_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("C₂:", self.c2_input)

        self.v2_input = QLineEdit()
        self.v2_input.setPlaceholderText("L (deixe vazio para calcular)")
        self.v2_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("V₂:", self.v2_input)

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
        btn_dilution_fullscreen.clicked.connect(lambda: self.show_fullscreen_result(self.dilution_result, "Cálculos de Diluição"))
        layout.addWidget(btn_dilution_fullscreen)

        return group

    def create_ph_section(self):
        """Seção de cálculos de pH."""
        group = QGroupBox("Cálculos de pH/pOH")
        layout = QVBoxLayout(group)
        
        # pH ácido forte
        form1 = QFormLayout()
        self.acid_conc_input = QLineEdit()
        self.acid_conc_input.setPlaceholderText("mol/L")
        self.acid_conc_input.setStyleSheet("font-weight: bold;")
        form1.addRow("Concentração do ácido forte:", self.acid_conc_input)
        
        btn_ph_acid = QPushButton("Calcular pH")
        form1.addRow(btn_ph_acid)
        btn_ph_acid.clicked.connect(self.calculate_ph_acid)
        
        self.ph_acid_result = QLineEdit()
        self.ph_acid_result.setReadOnly(True)
        self.ph_acid_result.setStyleSheet("font-weight: bold;")
        form1.addRow("pH:", self.ph_acid_result)
        
        layout.addLayout(form1)
        
        # Separador
        layout.addWidget(QLabel("─" * 50))
        
        # pOH base forte
        form2 = QFormLayout()
        self.base_conc_input = QLineEdit()
        self.base_conc_input.setPlaceholderText("mol/L")
        self.base_conc_input.setStyleSheet("font-weight: bold;")
        form2.addRow("Concentração da base forte:", self.base_conc_input)
        
        btn_ph_base = QPushButton("Calcular pOH e pH")
        form2.addRow(btn_ph_base)
        btn_ph_base.clicked.connect(self.calculate_ph_base)
        
        self.ph_base_result = QLineEdit()
        self.ph_base_result.setReadOnly(True)
        self.ph_base_result.setStyleSheet("font-weight: bold;")
        form2.addRow("pOH e pH:", self.ph_base_result)
        
        layout.addLayout(form2)
        
        return group

    def create_acid_base_section(self):
        """Seção de constantes ácido-base."""
        group = QGroupBox("Constantes de Ionização (Ka, Kb, pKa, pKb)")
        layout = QVBoxLayout(group)
        
        # Ka a partir de pH
        form1 = QFormLayout()
        self.ka_ph_input = QLineEdit()
        self.ka_ph_input.setPlaceholderText("0-14")
        self.ka_ph_input.setStyleSheet("font-weight: bold;")
        form1.addRow("pH:", self.ka_ph_input)
        
        self.ka_conc_input = QLineEdit()
        self.ka_conc_input.setPlaceholderText("mol/L")
        self.ka_conc_input.setStyleSheet("font-weight: bold;")
        form1.addRow("Concentração inicial:", self.ka_conc_input)
        
        btn_ka = QPushButton("Calcular Ka e pKa")
        form1.addRow(btn_ka)
        btn_ka.clicked.connect(self.calculate_ka)
        
        self.ka_result = QLineEdit()
        self.ka_result.setReadOnly(True)
        self.ka_result.setStyleSheet("font-weight: bold;")
        form1.addRow("Ka e pKa:", self.ka_result)
        
        layout.addLayout(form1)
        layout.addWidget(QLabel("─" * 50))
        
        # Kb a partir de pOH
        form2 = QFormLayout()
        self.kb_poh_input = QLineEdit()
        self.kb_poh_input.setPlaceholderText("0-14")
        self.kb_poh_input.setStyleSheet("font-weight: bold;")
        form2.addRow("pOH:", self.kb_poh_input)
        
        self.kb_conc_input = QLineEdit()
        self.kb_conc_input.setPlaceholderText("mol/L")
        self.kb_conc_input.setStyleSheet("font-weight: bold;")
        form2.addRow("Concentração inicial:", self.kb_conc_input)
        
        btn_kb = QPushButton("Calcular Kb e pKb")
        form2.addRow(btn_kb)
        btn_kb.clicked.connect(self.calculate_kb)
        
        self.kb_result = QLineEdit()
        self.kb_result.setReadOnly(True)
        self.kb_result.setStyleSheet("font-weight: bold;")
        form2.addRow("Kb e pKb:", self.kb_result)
        
        layout.addLayout(form2)
        layout.addWidget(QLabel("─" * 50))
        
        # Conversões entre Ka/Kb
        form3 = QFormLayout()
        self.ka_kb_input = QLineEdit()
        self.ka_kb_input.setPlaceholderText("Digite Ka OU Kb")
        self.ka_kb_input.setStyleSheet("font-weight: bold;")
        form3.addRow("Ka ou Kb:", self.ka_kb_input)
        
        self.ka_kb_type = QComboBox()
        self.ka_kb_type.addItems(["Ka", "Kb"])
        form3.addRow("Tipo:", self.ka_kb_type)
        
        btn_ka_kb = QPushButton("Calcular relação Ka×Kb=Kw")
        form3.addRow(btn_ka_kb)
        btn_ka_kb.clicked.connect(self.calculate_ka_kb_relation)
        
        self.ka_kb_relation_result = QTextEdit()
        self.ka_kb_relation_result.setMinimumHeight(60)  # Altura mínima em vez de máxima
        self.ka_kb_relation_result.setStyleSheet("font-weight: bold; font-family: monospace;")
        form3.addRow("Resultado:", self.ka_kb_relation_result)
        
        # Botão de tela cheia para Ka/Kb
        btn_ka_kb_fullscreen = QPushButton("📺 Ver em Tela Cheia")
        btn_ka_kb_fullscreen.clicked.connect(lambda: self.show_fullscreen_result(self.ka_kb_relation_result, "Relação Ka×Kb"))
        form3.addRow(btn_ka_kb_fullscreen)
        
        layout.addLayout(form3)
        
        return group

    def create_spectrophotometry_section(self):
        """Seção de espectrofotometria."""
        group = QGroupBox("Lei de Beer-Lambert")
        layout = QVBoxLayout(group)
        
        form_layout = QFormLayout()
        
        self.epsilon_input = QLineEdit()
        self.epsilon_input.setPlaceholderText("L·mol⁻¹·cm⁻¹")
        self.epsilon_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("ε (absortividade molar):", self.epsilon_input)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("cm")
        self.path_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("b (caminho óptico):", self.path_input)
        
        self.conc_beer_input = QLineEdit()
        self.conc_beer_input.setPlaceholderText("mol/L")
        self.conc_beer_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("C (concentração):", self.conc_beer_input)
        
        layout.addLayout(form_layout)
        
        # Fórmula
        formula = QLabel("A = ε × b × C")
        formula.setStyleSheet("font-weight: bold; color: #2c3e50; margin: 10px;")
        layout.addWidget(formula)
        
        # Botão e resultado
        btn_beer = QPushButton("Calcular Absorbância")
        btn_beer.clicked.connect(self.calculate_beer_lambert)
        layout.addWidget(btn_beer)
        
        self.beer_result = QLineEdit()
        self.beer_result.setReadOnly(True)
        self.beer_result.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.beer_result)
        
        return group

    # Métodos de cálculo
    def calculate_dilution(self):
        try:
            c1 = self._float_or_none(self.c1_input.text())
            v1 = self._float_or_none(self.v1_input.text())
            c2 = self._float_or_none(self.c2_input.text())
            v2 = self._float_or_none(self.v2_input.text())
            
            result = dilution_c1v1_c2v2(c1, v1, c2, v2)
            
            output = f"C₁ = {result['c1']:.6g} mol/L\n"
            output += f"V₁ = {result['v1']:.6g} L\n"
            output += f"C₂ = {result['c2']:.6g} mol/L\n"
            output += f"V₂ = {result['v2']:.6g} L"
            
            self.dilution_result.setText(output)
            
        except Exception as e:
            self.dilution_result.setText(f"Erro: {str(e)}")

    def calculate_ph_acid(self):
        try:
            conc = float(self.acid_conc_input.text())
            ph = ph_strong_acid(conc)
            self.ph_acid_result.setText(f"{ph:.3f}")
        except Exception as e:
            self.ph_acid_result.setText(f"Erro: {str(e)}")

    def calculate_ph_base(self):
        try:
            conc = float(self.base_conc_input.text())
            poh = poh_strong_base(conc)
            ph = ph_from_poh(poh)
            self.ph_base_result.setText(f"pOH = {poh:.3f}, pH = {ph:.3f}")
        except Exception as e:
            self.ph_base_result.setText(f"Erro: {str(e)}")

    def calculate_ka(self):
        try:
            ph = float(self.ka_ph_input.text())
            conc = float(self.ka_conc_input.text())
            ka = calculate_ka_from_ph(ph, conc)
            pka = calculate_pka_from_ka(ka)
            self.ka_result.setText(f"Ka = {ka:.3e}, pKa = {pka:.3f}")
        except Exception as e:
            self.ka_result.setText(f"Erro: {str(e)}")

    def calculate_kb(self):
        try:
            poh = float(self.kb_poh_input.text())
            conc = float(self.kb_conc_input.text())
            kb = calculate_kb_from_poh(poh, conc)
            pkb = calculate_pkb_from_kb(kb)
            self.kb_result.setText(f"Kb = {kb:.3e}, pKb = {pkb:.3f}")
        except Exception as e:
            self.kb_result.setText(f"Erro: {str(e)}")

    def create_dilution_section(self):
        group = QGroupBox("Diluição (C₁V₁ = C₂V₂)")
        layout = QVBoxLayout(group)

        # Formulário
        form_layout = QFormLayout()

        self.c1_input = QLineEdit()
        self.c1_input.setPlaceholderText("mol/L (deixe vazio para calcular)")
        self.c1_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("C₁:", self.c1_input)

        self.v1_input = QLineEdit()
        self.v1_input.setPlaceholderText("L (deixe vazio para calcular)")
        self.v1_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("V₁:", self.v1_input)

        self.c2_input = QLineEdit()
        self.c2_input.setPlaceholderText("mol/L (deixe vazio para calcular)")
        self.c2_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("C₂:", self.c2_input)

        self.v2_input = QLineEdit()
        self.v2_input.setPlaceholderText("L (deixe vazio para calcular)")
        self.v2_input.setStyleSheet("font-weight: bold;")
        form_layout.addRow("V₂:", self.v2_input)

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
        btn_dilution_fullscreen.clicked.connect(lambda: self.show_fullscreen_result(self.dilution_result, "Cálculos de Diluição"))
        layout.addWidget(btn_dilution_fullscreen)

        return group
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
                border: 2px solid #e74c3c;
                border-radius: 8px;
            }
        """)
        layout.addWidget(fullscreen_text)
        
        # Botões
        button_layout = QHBoxLayout()
        
        # Botão copiar
        btn_copy = QPushButton("📋 Copiar para Área de Transferência")
        btn_copy.clicked.connect(lambda: self.copy_to_clipboard(fullscreen_text.toPlainText()))
        button_layout.addWidget(btn_copy)
        
        # Botão salvar
        btn_save = QPushButton("💾 Salvar em Arquivo")
        btn_save.clicked.connect(lambda: self.save_to_file(fullscreen_text.toPlainText(), title))
        button_layout.addWidget(btn_save)
        
        button_layout.addStretch()
        
        # Botão fechar
        btn_close = QPushButton("❌ Fechar")
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
            msg.setText("📋 Resultados copiados para a área de transferência!")
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
                msg.setText(f"💾 Arquivo salvo com sucesso!\n\n{file_path}")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Erro")
            msg.setText(f"❌ Erro ao salvar arquivo:\n{str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
