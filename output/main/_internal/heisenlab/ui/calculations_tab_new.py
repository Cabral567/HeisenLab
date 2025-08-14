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
        self.dilution_result.setMinimumHeight(60)
        self.dilution_result.setStyleSheet("font-weight: bold; font-family: monospace;")
        layout.addWidget(self.dilution_result)
        
        # Botão de tela cheia
        btn_dilution_fullscreen = QPushButton("Ver em Tela Cheia")
        btn_dilution_fullscreen.clicked.connect(lambda: self.show_fullscreen_result(self.dilution_result, "Cálculo de Diluição"))
        layout.addWidget(btn_dilution_fullscreen)
        
        return group

    def create_ka_kb_section(self):
        """Seção de cálculos de Ka e Kb."""
        group = QGroupBox("Cálculos de Ka e Kb")
        layout = QVBoxLayout(group)
        
        # Sub-seções usando abas (QTabWidget seria ideal, mas vou usar grupos separados)
        
        # Seção Ka
        ka_group = QGroupBox("Cálculos de Ka")
        ka_layout = QVBoxLayout(ka_group)
        
        # Ka inputs
        ka_form = QFormLayout()
        
        self.ph_input_ka = QLineEdit()
        self.ph_input_ka.setPlaceholderText("pH da solução")
        ka_form.addRow("pH:", self.ph_input_ka)
        
        self.initial_conc_ka = QLineEdit()
        self.initial_conc_ka.setPlaceholderText("Concentração inicial do ácido")
        ka_form.addRow("Concentração inicial (mol/L):", self.initial_conc_ka)
        
        ka_layout.addLayout(ka_form)
        
        # Botões Ka
        btn_ka = QPushButton("Calcular Ka")
        btn_ka.clicked.connect(self.calculate_ka)
        ka_layout.addWidget(btn_ka)
        
        btn_pka = QPushButton("Calcular pKa")
        btn_pka.clicked.connect(self.calculate_pka)
        ka_layout.addWidget(btn_pka)
        
        layout.addWidget(ka_group)
        
        # Seção Kb
        kb_group = QGroupBox("Cálculos de Kb")
        kb_layout = QVBoxLayout(kb_group)
        
        # Kb inputs
        kb_form = QFormLayout()
        
        self.poh_input_kb = QLineEdit()
        self.poh_input_kb.setPlaceholderText("pOH da solução")
        kb_form.addRow("pOH:", self.poh_input_kb)
        
        self.initial_conc_kb = QLineEdit()
        self.initial_conc_kb.setPlaceholderText("Concentração inicial da base")
        kb_form.addRow("Concentração inicial (mol/L):", self.initial_conc_kb)
        
        kb_layout.addLayout(kb_form)
        
        # Botões Kb
        btn_kb = QPushButton("Calcular Kb")
        btn_kb.clicked.connect(self.calculate_kb)
        kb_layout.addWidget(btn_kb)
        
        btn_pkb = QPushButton("Calcular pKb")
        btn_pkb.clicked.connect(self.calculate_pkb)
        kb_layout.addWidget(btn_pkb)
        
        layout.addWidget(kb_group)
        
        # Seção relação Ka-Kb
        relation_group = QGroupBox("Relação Ka × Kb = Kw")
        relation_layout = QVBoxLayout(relation_group)
        
        relation_form = QFormLayout()
        
        self.ka_input_relation = QLineEdit()
        self.ka_input_relation.setPlaceholderText("Valor de Ka")
        relation_form.addRow("Ka:", self.ka_input_relation)
        
        self.kb_input_relation = QLineEdit()
        self.kb_input_relation.setPlaceholderText("Valor de Kb")
        relation_form.addRow("Kb:", self.kb_input_relation)
        
        relation_layout.addLayout(relation_form)
        
        btn_relation = QPushButton("Calcular Relação Ka-Kb")
        btn_relation.clicked.connect(self.calculate_ka_kb_relation)
        relation_layout.addWidget(btn_relation)
        
        layout.addWidget(relation_group)
        
        # Resultado geral para Ka/Kb
        self.ka_kb_relation_result = QTextEdit()
        self.ka_kb_relation_result.setMinimumHeight(120)
        self.ka_kb_relation_result.setStyleSheet("font-weight: bold; font-family: monospace;")
        layout.addWidget(self.ka_kb_relation_result)
        
        # Botão de tela cheia para Ka/Kb
        btn_ka_kb_fullscreen = QPushButton("Ver em Tela Cheia")
        btn_ka_kb_fullscreen.clicked.connect(lambda: self.show_fullscreen_result(self.ka_kb_relation_result, "Cálculos de Ka e Kb"))
        layout.addWidget(btn_ka_kb_fullscreen)
        
        return group

    # Métodos de cálculo
    def calculate_dilution(self):
        """Calcula diluição usando C1V1 = C2V2."""
        try:
            # Coleta valores, converte vírgulas em pontos
            c1_text = self.c1_input.text().replace(',', '.').strip()
            v1_text = self.v1_input.text().replace(',', '.').strip()
            c2_text = self.c2_input.text().replace(',', '.').strip()
            v2_text = self.v2_input.text().replace(',', '.').strip()
            
            # Converte para float ou None se vazio
            c1 = float(c1_text) if c1_text else None
            v1 = float(v1_text) if v1_text else None
            c2 = float(c2_text) if c2_text else None
            v2 = float(v2_text) if v2_text else None
            
            # Chama função de cálculo
            result = dilution_c1v1_c2v2(c1, v1, c2, v2)
            
            # Formata resultado
            output = "CÁLCULO DE DILUIÇÃO (C₁V₁ = C₂V₂)\n"
            output += "="*50 + "\n"
            output += f"C₁ = {result['c1']:.6g} mol/L\n"
            output += f"V₁ = {result['v1']:.6g} L\n"
            output += f"C₂ = {result['c2']:.6g} mol/L\n"
            output += f"V₂ = {result['v2']:.6g} L\n"
            output += "="*50 + "\n"
            output += f"Equação: C₁V₁ = C₂V₂\n"
            output += f"Verificação: {result['c1']:.6g} × {result['v1']:.6g} = {result['c2']:.6g} × {result['v2']:.6g}\n"
            output += f"Produto: {result['c1'] * result['v1']:.6g} = {result['c2'] * result['v2']:.6g}"
            
            self.dilution_result.setText(output)
            
        except Exception as e:
            error_msg = f"Erro no cálculo de diluição: {str(e)}\n\n"
            error_msg += "Certifique-se de:\n"
            error_msg += "• Inserir exatamente 3 valores\n"
            error_msg += "• Deixar 1 campo vazio para calcular\n"
            error_msg += "• Usar números válidos (ponto ou vírgula como decimal)"
            self.dilution_result.setText(error_msg)

    def calculate_ka(self):
        """Calcula Ka a partir do pH."""
        try:
            ph = float(self.ph_input_ka.text().replace(',', '.'))
            conc = float(self.initial_conc_ka.text().replace(',', '.'))
            
            ka = calculate_ka_from_ph(ph, conc)
            pka = calculate_pka_from_ka(ka)
            
            output = f"CÁLCULO DE Ka\n"
            output += "="*30 + "\n"
            output += f"pH = {ph}\n"
            output += f"Concentração inicial = {conc} mol/L\n"
            output += f"Ka = {ka:.2e}\n"
            output += f"pKa = {pka:.4f}\n"
            
            self.ka_kb_relation_result.setText(output)
            
        except Exception as e:
            self.ka_kb_relation_result.setText(f"Erro no cálculo de Ka: {str(e)}")

    def calculate_pka(self):
        """Calcula pKa a partir de Ka."""
        try:
            ka_text = self.ka_input_relation.text().replace(',', '.')
            if not ka_text:
                raise ValueError("Insira o valor de Ka")
            
            ka = float(ka_text)
            pka = calculate_pka_from_ka(ka)
            
            output = f"CÁLCULO DE pKa\n"
            output += "="*30 + "\n"
            output += f"Ka = {ka:.2e}\n"
            output += f"pKa = {pka:.4f}\n"
            
            self.ka_kb_relation_result.setText(output)
            
        except Exception as e:
            self.ka_kb_relation_result.setText(f"Erro no cálculo de pKa: {str(e)}")

    def calculate_kb(self):
        """Calcula Kb a partir do pOH."""
        try:
            poh = float(self.poh_input_kb.text().replace(',', '.'))
            conc = float(self.initial_conc_kb.text().replace(',', '.'))
            
            kb = calculate_kb_from_poh(poh, conc)
            pkb = calculate_pkb_from_kb(kb)
            
            output = f"CÁLCULO DE Kb\n"
            output += "="*30 + "\n"
            output += f"pOH = {poh}\n"
            output += f"Concentração inicial = {conc} mol/L\n"
            output += f"Kb = {kb:.2e}\n"
            output += f"pKb = {pkb:.4f}\n"
            
            self.ka_kb_relation_result.setText(output)
            
        except Exception as e:
            self.ka_kb_relation_result.setText(f"Erro no cálculo de Kb: {str(e)}")

    def calculate_pkb(self):
        """Calcula pKb a partir de Kb."""
        try:
            kb_text = self.kb_input_relation.text().replace(',', '.')
            if not kb_text:
                raise ValueError("Insira o valor de Kb")
            
            kb = float(kb_text)
            pkb = calculate_pkb_from_kb(kb)
            
            output = f"CÁLCULO DE pKb\n"
            output += "="*30 + "\n"
            output += f"Kb = {kb:.2e}\n"
            output += f"pKb = {pkb:.4f}\n"
            
            self.ka_kb_relation_result.setText(output)
            
        except Exception as e:
            self.ka_kb_relation_result.setText(f"Erro no cálculo de pKb: {str(e)}")

    def calculate_ka_kb_relation(self):
        """Calcula a relação Ka × Kb = Kw."""
        try:
            ka_text = self.ka_input_relation.text().replace(',', '.')
            kb_text = self.kb_input_relation.text().replace(',', '.')
            
            if not ka_text and not kb_text:
                raise ValueError("Insira ao menos um valor (Ka ou Kb)")
            
            ka = float(ka_text) if ka_text else None
            kb = float(kb_text) if kb_text else None
            
            result = ka_kb_relationship(ka, kb)
            
            output = f"RELAÇÃO Ka × Kb = Kw\n"
            output += "="*40 + "\n"
            output += f"Ka = {result['ka']:.2e}\n"
            output += f"Kb = {result['kb']:.2e}\n"
            output += f"Kw = {result['kw']:.2e}\n"
            output += f"Produto Ka × Kb = {result['ka'] * result['kb']:.2e}\n"
            output += f"pKa = {-result['pka']:.4f}\n" if 'pka' in result else ""
            output += f"pKb = {-result['pkb']:.4f}\n" if 'pkb' in result else ""
            output += f"pKw = {result['pkw']:.1f}\n"
            
            self.ka_kb_relation_result.setText(output)
            
        except Exception as e:
            self.ka_kb_relation_result.setText(f"Erro no cálculo da relação Ka-Kb: {str(e)}")

    def show_fullscreen_result(self, source_widget: QTextEdit, title: str):
        """Mostra o resultado em uma janela de tela cheia."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setWindowState(Qt.WindowMaximized)
        
        layout = QVBoxLayout(dialog)
        
        # Título
        title_label = QLabel(f"{title}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Área de texto expandida
        fullscreen_text = QTextEdit()
        fullscreen_text.setPlainText(source_widget.toPlainText())
        fullscreen_text.setReadOnly(True)
        fullscreen_text.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                font-size: 12px;
                border: 2px solid #ff4444;
                border-radius: 5px;
                padding: 10px;
                background-color: #ffffff;
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
            
            # Mensagem de confirmação
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Sucesso")
            msg.setText("Resultados copiados para a área de transferência!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Erro")
            msg.setText(f"Erro ao copiar para área de transferência: {str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def save_to_file(self, content: str, title: str):
        """Salva o conteúdo em um arquivo."""
        try:
            from PySide6.QtWidgets import QFileDialog, QMessageBox
            from datetime import datetime
            
            # Nome padrão do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"HeisenLab_{title.replace(' ', '_')}_{timestamp}.txt"
            
            # Dialog para salvar arquivo
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Salvar {title}",
                default_name,
                "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"HeisenLab - {title}\n")
                    f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
                    f.write("="*60 + "\n\n")
                    f.write(content)
                    f.write(f"\n\n{'='*60}\n")
                    f.write("Arquivo gerado pelo HeisenLab - Software de Química Analítica\n")
                
                # Mensagem de sucesso
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Sucesso")
                msg.setText(f"Arquivo salvo com sucesso!\n\n{file_path}")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Erro")
            msg.setText(f"Erro ao salvar arquivo:\n{str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
