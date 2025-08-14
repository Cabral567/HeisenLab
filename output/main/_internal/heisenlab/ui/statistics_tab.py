from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QGroupBox,
    QScrollArea,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox,
    QDialog,
    QHBoxLayout,
)

from ..calculations import (
    absolute_deviation,
    mean_deviation,
    sample_variance,
    sample_standard_deviation,
    coefficient_of_variation,
    correction_factor,
    confidence_interval_mean_small_n,
    confidence_interval_mean_large_n,
    t_test_two_means,
    f_test_two_variances,
)


class StatisticsTab(QWidget):
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
        
        # Seção única integrada de estatística
        layout.addWidget(self.create_integrated_statistics_section())
        layout.addStretch()
        
        scroll.setWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    def create_integrated_statistics_section(self):
        """Cria a seção integrada de estatística com estatística descritiva, intervalos de confiança e testes de hipóteses."""
        section = QGroupBox("Análise Estatística Completa")
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        layout = QVBoxLayout(section)
        
        # Sub-seção: Entrada de dados
        data_group = QGroupBox("Entrada de Dados")
        data_layout = QVBoxLayout(data_group)
        
        # Área de entrada de dados
        form_layout = QFormLayout()
        
        self.data_input = QTextEdit()
        self.data_input.setPlaceholderText("Digite os valores separados por vírgula ou quebra de linha\nExemplo: 1.2, 3.4, 5.6, 7.8")
        self.data_input.setMaximumHeight(80)
        form_layout.addRow("Dados:", self.data_input)
        
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Opcional - para desvio absoluto")
        form_layout.addRow("Valor de referência:", self.reference_input)
        
        data_layout.addLayout(form_layout)
        
        # Botão de análise geral
        analyze_btn = QPushButton("Analisar Dados Completos")
        analyze_btn.clicked.connect(self.analyze_complete_statistics)
        data_layout.addWidget(analyze_btn)
        
        layout.addWidget(data_group)
        
        # Sub-seção: Estatística Descritiva
        desc_group = QGroupBox("1. Estatística Descritiva")
        desc_layout = QVBoxLayout(desc_group)
        
        # Botão específico para estatística descritiva
        desc_btn = QPushButton("Calcular Estatísticas Descritivas")
        desc_btn.clicked.connect(self.calculate_descriptive_stats)
        desc_layout.addWidget(desc_btn)
        
        # Resultado da estatística descritiva
        self.descriptive_result = QTextEdit()
        self.descriptive_result.setMinimumHeight(200)
        self.descriptive_result.setReadOnly(True)
        self.descriptive_result.setStyleSheet("font-family: monospace; font-size: 11px;")
        self.descriptive_result.setPlaceholderText("Os resultados da estatística descritiva aparecerão aqui...")
        desc_layout.addWidget(self.descriptive_result)
        
        # Botão para tela cheia da estatística descritiva
        desc_fullscreen_btn = QPushButton("Ver Estatística Descritiva em Tela Cheia")
        desc_fullscreen_btn.clicked.connect(lambda: self.show_fullscreen_result(
            self.descriptive_result, "Estatística Descritiva"
        ))
        desc_layout.addWidget(desc_fullscreen_btn)
        
        layout.addWidget(desc_group)
        
        # Sub-seção: Intervalos de Confiança (dentro da estatística descritiva)
        conf_group = QGroupBox("2. Intervalos de Confiança")
        conf_layout = QVBoxLayout(conf_group)
        
        # Controles para intervalo de confiança
        conf_controls_layout = QFormLayout()
        
        self.confidence_level = QDoubleSpinBox()
        self.confidence_level.setRange(0.01, 0.99)
        self.confidence_level.setValue(0.95)
        self.confidence_level.setSingleStep(0.01)
        self.confidence_level.setDecimals(3)
        conf_controls_layout.addRow("Nível de confiança:", self.confidence_level)
        
        self.ic_method = QComboBox()
        self.ic_method.addItems(["Auto (n<30: t, n≥30: z)", "t de Student", "Distribuição Normal (z)"])
        conf_controls_layout.addRow("Método:", self.ic_method)
        
        conf_layout.addLayout(conf_controls_layout)
        
        conf_btn = QPushButton("Calcular Intervalo de Confiança")
        conf_btn.clicked.connect(self.calculate_confidence_interval)
        conf_layout.addWidget(conf_btn)
        
        # Resultado do intervalo de confiança
        self.ic_result = QTextEdit()
        self.ic_result.setMinimumHeight(150)
        self.ic_result.setReadOnly(True)
        self.ic_result.setStyleSheet("font-family: monospace; font-size: 11px;")
        self.ic_result.setPlaceholderText("Os resultados do intervalo de confiança aparecerão aqui...")
        conf_layout.addWidget(self.ic_result)
        
        # Botão para tela cheia do intervalo de confiança
        conf_fullscreen_btn = QPushButton("Ver Intervalos de Confiança em Tela Cheia")
        conf_fullscreen_btn.clicked.connect(lambda: self.show_fullscreen_result(
            self.ic_result, "Intervalo de Confiança"
        ))
        conf_layout.addWidget(conf_fullscreen_btn)
        
        layout.addWidget(conf_group)
        
        # Sub-seção: Testes de Hipóteses (dentro da estatística descritiva)
        hyp_group = QGroupBox("3. Testes de Hipóteses")
        hyp_layout = QVBoxLayout(hyp_group)
        
        # Teste t
        t_test_group = QGroupBox("Teste t (Comparar duas médias)")
        t_test_layout = QVBoxLayout(t_test_group)
        
        form_t = QFormLayout()
        self.t_data1_input = QTextEdit()
        self.t_data1_input.setPlaceholderText("Amostra 1: valores separados por vírgula")
        self.t_data1_input.setMaximumHeight(60)
        form_t.addRow("Dados 1:", self.t_data1_input)
        
        self.t_data2_input = QTextEdit()
        self.t_data2_input.setPlaceholderText("Amostra 2: valores separados por vírgula")
        self.t_data2_input.setMaximumHeight(60)
        form_t.addRow("Dados 2:", self.t_data2_input)
        
        self.t_confidence = QDoubleSpinBox()
        self.t_confidence.setRange(0.01, 0.99)
        self.t_confidence.setValue(0.95)
        self.t_confidence.setSingleStep(0.01)
        self.t_confidence.setDecimals(3)
        form_t.addRow("Nível de confiança:", self.t_confidence)
        
        t_test_layout.addLayout(form_t)
        
        btn_t = QPushButton("Realizar Teste t")
        btn_t.clicked.connect(self.calculate_t_test)
        t_test_layout.addWidget(btn_t)
        
        self.t_result = QTextEdit()
        self.t_result.setReadOnly(True)
        self.t_result.setMinimumHeight(120)
        self.t_result.setStyleSheet("font-family: monospace; font-size: 11px;")
        t_test_layout.addWidget(self.t_result)
        
        # Botão para tela cheia do teste t
        t_fullscreen_btn = QPushButton("Ver Teste t em Tela Cheia")
        t_fullscreen_btn.clicked.connect(lambda: self.show_fullscreen_result(
            self.t_result, "Teste t"
        ))
        t_test_layout.addWidget(t_fullscreen_btn)
        
        hyp_layout.addWidget(t_test_group)
        
        # Teste F
        f_test_group = QGroupBox("Teste F (Comparar duas variâncias)")
        f_test_layout = QVBoxLayout(f_test_group)
        
        form_f = QFormLayout()
        self.f_data1_input = QTextEdit()
        self.f_data1_input.setPlaceholderText("Amostra 1: valores separados por vírgula")
        self.f_data1_input.setMaximumHeight(60)
        form_f.addRow("Dados 1:", self.f_data1_input)
        
        self.f_data2_input = QTextEdit()
        self.f_data2_input.setPlaceholderText("Amostra 2: valores separados por vírgula")
        self.f_data2_input.setMaximumHeight(60)
        form_f.addRow("Dados 2:", self.f_data2_input)
        
        self.f_confidence = QDoubleSpinBox()
        self.f_confidence.setRange(0.01, 0.99)
        self.f_confidence.setValue(0.95)
        self.f_confidence.setSingleStep(0.01)
        self.f_confidence.setDecimals(3)
        form_f.addRow("Nível de confiança:", self.f_confidence)
        
        f_test_layout.addLayout(form_f)
        
        btn_f = QPushButton("Realizar Teste F")
        btn_f.clicked.connect(self.calculate_f_test)
        f_test_layout.addWidget(btn_f)
        
        self.f_result = QTextEdit()
        self.f_result.setReadOnly(True)
        self.f_result.setMinimumHeight(120)
        self.f_result.setStyleSheet("font-family: monospace; font-size: 11px;")
        f_test_layout.addWidget(self.f_result)
        
        # Botão para tela cheia do teste F
        f_fullscreen_btn = QPushButton("Ver Teste F em Tela Cheia")
        f_fullscreen_btn.clicked.connect(lambda: self.show_fullscreen_result(
            self.f_result, "Teste F"
        ))
        f_test_layout.addWidget(f_fullscreen_btn)
        
        hyp_layout.addWidget(f_test_group)
        
        layout.addWidget(hyp_group)
        
        return section

    def analyze_complete_statistics(self):
        """Executa análise estatística completa em todos os campos."""
        self.calculate_descriptive_stats()
        self.calculate_confidence_interval()
        # Os testes de hipóteses precisam de dados separados, então não são executados automaticamente

    # Métodos de cálculo
    def calculate_descriptive_stats(self):
        try:
            # Processar dados
            raw_text = self.data_input.toPlainText()
            data = self.parse_data(raw_text)
            
            if not data:
                self.descriptive_result.setText("Erro: Nenhum dado válido inserido")
                return
            
            # Valor de referência opcional
            ref_text = self.reference_input.text().strip()
            reference = float(ref_text) if ref_text else None
            
            # Calcular estatísticas
            mean_val = sum(data) / len(data)
            abs_dev = absolute_deviation(data, reference)
            mean_dev = mean_deviation(data)
            variance = sample_variance(data)
            std_dev = sample_standard_deviation(data)
            cv = coefficient_of_variation(data)
            corr_factor = correction_factor(len(data))
            
            # Formatação dos resultados
            result = f"ESTATÍSTICA DESCRITIVA\n"
            result += f"{'='*50}\n"
            result += f"DADOS ANALISADOS: {data}\n"
            result += f"{'='*50}\n"
            result += f"n (tamanho da amostra): {len(data)}\n"
            result += f"Média (x̄): {mean_val:.6g}\n"
            result += f"Variância amostral (s²): {variance:.6g}\n"
            result += f"Desvio padrão amostral (s): {std_dev:.6g}\n"
            result += f"Desvio médio: {mean_dev:.6g}\n"
            result += f"Coeficiente de variação (CV): {cv:.3f}%\n"
            result += f"Fator de correção: {corr_factor:.6g}\n"
            result += f"{'='*50}\n"
            
            if reference is not None:
                result += f"DESVIOS ABSOLUTOS (referência = {reference}):\n"
                for i, dev in enumerate(abs_dev):
                    result += f"  |x{i+1} - ref| = |{data[i]} - {reference}| = {dev:.6g}\n"
            else:
                result += f"DESVIOS ABSOLUTOS (referência = média = {mean_val:.6g}):\n"
                for i, dev in enumerate(abs_dev):
                    result += f"  |x{i+1} - x̄| = |{data[i]} - {mean_val:.6g}| = {dev:.6g}\n"
            
            self.descriptive_result.setText(result)
            
        except Exception as e:
            self.descriptive_result.setText(f"Erro: {str(e)}")
            import traceback
            print(f"Debug - Erro detalhado: {traceback.format_exc()}")

    def calculate_confidence_interval(self):
        try:
            # Usar os mesmos dados da estatística descritiva
            data = self.parse_data(self.data_input.toPlainText())
            if not data:
                self.ic_result.setText("Erro: Nenhum dado válido inserido")
                return
            
            confidence = self.confidence_level.value()
            method = self.ic_method.currentText()
            
            # Escolher método
            if method.startswith("Auto"):
                if len(data) < 30:
                    result = confidence_interval_mean_small_n(data, confidence)
                    method_used = "t de Student"
                else:
                    result = confidence_interval_mean_large_n(data, confidence)
                    method_used = "Distribuição Normal (z)"
            elif "Student" in method:
                result = confidence_interval_mean_small_n(data, confidence)
                method_used = "t de Student"
            else:
                result = confidence_interval_mean_large_n(data, confidence)
                method_used = "Distribuição Normal (z)"
            
            # Formatação dos resultados
            output = f"INTERVALO DE CONFIANÇA\n"
            output += f"{'='*40}\n"
            output += f"Método: {method_used}\n"
            output += f"Nível de confiança: {confidence*100:.1f}%\n"
            output += f"n: {result['n']}\n"
            output += f"Média: {result['mean']:.6g}\n"
            output += f"Desvio padrão: {result['std_dev']:.6g}\n"
            
            if 't_critical' in result:
                output += f"t crítico: ±{result['t_critical']:.4f}\n"
                output += f"Graus de liberdade: {result['df']}\n"
            else:
                output += f"z crítico: ±{result['z_critical']:.4f}\n"
            
            output += f"Margem de erro: ±{result['margin_error']:.6g}\n"
            output += f"\nINTERVALO: [{result['lower_limit']:.6g}, {result['upper_limit']:.6g}]"
            
            self.ic_result.setText(output)
            
        except Exception as e:
            self.ic_result.setText(f"Erro: {str(e)}")

    def calculate_t_test(self):
        try:
            # Processar dados
            data1 = self.parse_data(self.t_data1_input.toPlainText())
            data2 = self.parse_data(self.t_data2_input.toPlainText())
            
            if not data1 or not data2:
                self.t_result.setText("Erro: Dados inválidos em uma ou ambas as amostras")
                return
            
            confidence = self.t_confidence.value()
            result = t_test_two_means(data1, data2, confidence)
            
            # Formatação dos resultados
            output = f"TESTE t (DUAS AMOSTRAS)\n"
            output += f"{'='*40}\n"
            output += f"H₀: μ₁ = μ₂\n"
            output += f"H₁: μ₁ ≠ μ₂\n\n"
            output += f"Amostra 1: n₁ = {result['n1']}, x̄₁ = {result['mean1']:.6g}, s₁ = {result['std1']:.6g}\n"
            output += f"Amostra 2: n₂ = {result['n2']}, x̄₂ = {result['mean2']:.6g}, s₂ = {result['std2']:.6g}\n\n"
            output += f"Estatística t: {result['t_statistic']:.6g}\n"
            output += f"t crítico: ±{result['t_critical']:.4f}\n"
            output += f"Graus de liberdade: {result['df']:.1f}\n"
            output += f"p-valor: {result['p_value']:.6g}\n"
            output += f"Nível de confiança: {confidence*100:.1f}%\n\n"
            output += f"DECISÃO: {'Rejeitar H₀' if result['reject_h0'] else 'Não rejeitar H₀'}\n"
            output += f"CONCLUSÃO: {result['conclusion']}"
            
            self.t_result.setText(output)
            
        except Exception as e:
            self.t_result.setText(f"Erro: {str(e)}")

    def calculate_f_test(self):
        try:
            # Processar dados
            data1 = self.parse_data(self.f_data1_input.toPlainText())
            data2 = self.parse_data(self.f_data2_input.toPlainText())
            
            if not data1 or not data2:
                self.f_result.setText("Erro: Dados inválidos em uma ou ambas as amostras")
                return
            
            confidence = self.f_confidence.value()
            result = f_test_two_variances(data1, data2, confidence)
            
            # Formatação dos resultados
            output = f"TESTE F (DUAS VARIÂNCIAS)\n"
            output += f"{'='*40}\n"
            output += f"H₀: σ₁² = σ₂²\n"
            output += f"H₁: σ₁² ≠ σ₂²\n\n"
            output += f"Variância 1: s₁² = {result['var1']:.6g}\n"
            output += f"Variância 2: s₂² = {result['var2']:.6g}\n"
            output += f"Maior variância: Amostra {result['larger_variance_sample']}\n\n"
            output += f"Estatística F: {result['f_statistic']:.6g}\n"
            output += f"F crítico: {result['f_critical']:.4f}\n"
            output += f"Graus de liberdade: ({result['df1']}, {result['df2']})\n"
            output += f"p-valor: {result['p_value']:.6g}\n"
            output += f"Nível de confiança: {confidence*100:.1f}%\n\n"
            output += f"DECISÃO: {'Rejeitar H₀' if result['reject_h0'] else 'Não rejeitar H₀'}\n"
            output += f"CONCLUSÃO: {result['conclusion']}"
            
            self.f_result.setText(output)
            
        except Exception as e:
            self.f_result.setText(f"Erro: {str(e)}")

    def parse_data(self, text: str) -> list[float]:
        """Converte texto em lista de números."""
        if not text.strip():
            return []
        
        # Limpar o texto
        text = text.strip()
        
        # Substituir quebras de linha por vírgulas
        text = text.replace('\n', ',').replace('\r', ',')
        
        # Dividir por vírgulas e filtrar valores válidos
        values = []
        raw_items = text.split(',')
        
        for item in raw_items:
            item = item.strip()
            if item:  # Se não estiver vazio
                try:
                    value = float(item)
                    values.append(value)
                except ValueError:
                    # Tentar substituir vírgula decimal por ponto
                    try:
                        item_with_dot = item.replace(',', '.')
                        value = float(item_with_dot)
                        values.append(value)
                    except ValueError:
                        print(f"Debug - Não foi possível converter '{item}' para número")
                        continue
        
        print(f"Debug - Texto original: '{text}'")
        print(f"Debug - Itens encontrados: {raw_items}")
        print(f"Debug - Valores convertidos: {values}")
        print(f"Debug - Número de valores: {len(values)}")
        
        return values

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
                border: 2px solid #3498db;
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
            
            # Feedback visual (opcional)
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
            msg.setText(f"Erro ao salvar arquivo:\n{str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
