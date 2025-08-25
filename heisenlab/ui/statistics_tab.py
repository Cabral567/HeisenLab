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
    QSplitter,
    QApplication,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtGui import QFont

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


class ZoomableTextEdit(QTextEdit):
    """QTextEdit with zoom functionality using Ctrl+Mouse Wheel."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_font_size = 17  # Tamanho base da fonte
        # Definir fonte inicial
        font = QFont("monospace")
        font.setPointSize(self.base_font_size)
        self.setFont(font)
        
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            # Zoom com Ctrl + Mouse Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Scroll normal
            super().wheelEvent(event)
    
    def zoom_in(self):
        """Increase font size."""
        current_font = self.font()
        current_size = current_font.pointSize()
        if current_size == -1:  # Se pointSize não funcionar, usar pixelSize
            current_size = current_font.pixelSize()
            if current_size < 30:
                current_font.setPixelSize(current_size + 1)
                self.setFont(current_font)
        else:
            if current_size < 30:  # Limite máximo
                current_font.setPointSize(current_size + 1)
                self.setFont(current_font)
    
    def zoom_out(self):
        """Decrease font size."""
        current_font = self.font()
        current_size = current_font.pointSize()
        if current_size == -1:  # Se pointSize não funcionar, usar pixelSize
            current_size = current_font.pixelSize()
            if current_size > 8:
                current_font.setPixelSize(current_size - 1)
                self.setFont(current_font)
        else:
            if current_size > 8:  # Limite mínimo
                current_font.setPointSize(current_size - 1)
                self.setFont(current_font)
    
    def reset_zoom(self):
        """Reset font size to base size."""
        font = QFont("monospace")
        font.setPointSize(self.base_font_size)
        self.setFont(font)


class ZoomableDataInput(QTextEdit):
    """QTextEdit for data input with zoom functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_font_size = 11  # Tamanho base da fonte para input
        # Definir fonte inicial
        font = QFont("monospace")
        font.setPointSize(self.base_font_size)
        self.setFont(font)
        
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            # Zoom com Ctrl + Mouse Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Scroll normal
            super().wheelEvent(event)
    
    def zoom_in(self):
        """Increase font size."""
        current_font = self.font()
        current_size = current_font.pointSize()
        if current_size == -1:
            current_size = current_font.pixelSize()
            if current_size < 24:
                current_font.setPixelSize(current_size + 1)
                self.setFont(current_font)
        else:
            if current_size < 24:  # Limite máximo
                current_font.setPointSize(current_size + 1)
                self.setFont(current_font)
    
    def zoom_out(self):
        """Decrease font size."""
        current_font = self.font()
        current_size = current_font.pointSize()
        if current_size == -1:
            current_size = current_font.pixelSize()
            if current_size > 8:
                current_font.setPixelSize(current_size - 1)
                self.setFont(current_font)
        else:
            if current_size > 8:  # Limite mínimo
                current_font.setPointSize(current_size - 1)
                self.setFont(current_font)


class ZoomableDialogTextEdit(QTextEdit):
    """QTextEdit for dialogs with zoom functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_font_size = 14  # Tamanho base da fonte para diálogos
        # Definir fonte inicial
        font = QFont("monospace")
        font.setPointSize(self.base_font_size)
        self.setFont(font)
        
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            # Zoom com Ctrl + Mouse Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Scroll normal
            super().wheelEvent(event)
    
    def zoom_in(self):
        """Increase font size."""
        current_font = self.font()
        current_size = current_font.pointSize()
        if current_size < 28:  # Limite máximo
            current_font.setPointSize(current_size + 1)
            self.setFont(current_font)
    
    def zoom_out(self):
        """Decrease font size."""
        current_font = self.font()
        current_size = current_font.pointSize()
        if current_size > 8:  # Limite mínimo
            current_font.setPointSize(current_size - 1)
            self.setFont(current_font)


class StatisticsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Configura a interface principal."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Create main splitter for better layout
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Input and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        # Input section
        input_group = self.create_input_section()
        left_layout.addWidget(input_group)
        
        # Analysis options
        analysis_group = self.create_analysis_section()
        left_layout.addWidget(analysis_group)
        
        # Result options
        options_group = self.create_options_section()
        left_layout.addWidget(options_group)
        
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        
        # Right panel - Results
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # Results section
        results_group = self.create_results_section()
        right_layout.addWidget(results_group)
        
        right_widget.setLayout(right_layout)
        
        # Add to splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 1)  # Left panel
        main_splitter.setStretchFactor(1, 2)  # Right panel (larger)
        
        layout.addWidget(main_splitter)
        self.setLayout(layout)

    def create_input_section(self) -> QGroupBox:
        """Create the input section."""
        group = QGroupBox("Entrada de Dados")
        layout = QFormLayout()
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(15)
        
        # Data input
        self.data_input = ZoomableDataInput()
        self.data_input.setPlaceholderText("Digite os valores separados por vírgula ou quebra de linha")
        self.data_input.setMaximumHeight(100)
        layout.addRow("Dados:", self.data_input)
        
        # Reference value input
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Ex: 5.0")
        self.reference_input.setMinimumHeight(30)
        layout.addRow("Valor de Referência (opcional):", self.reference_input)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("Analisar")
        self.analyze_button.setMinimumHeight(35)
        self.analyze_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.analyze_button.clicked.connect(self.analyze_complete_statistics)
        buttons_layout.addWidget(self.analyze_button)
        
        self.clear_button = QPushButton("Limpar")
        self.clear_button.setMinimumHeight(35)
        self.clear_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.clear_button.clicked.connect(self.clear_inputs)
        buttons_layout.addWidget(self.clear_button)
        
        layout.addRow("", buttons_layout)
        
        group.setLayout(layout)
        return group

    def create_analysis_section(self) -> QGroupBox:
        """Create analysis options section."""
        group = QGroupBox("Análises Específicas")
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Analysis buttons
        analyses = [
            ("Intervalos de Confiança", self.show_confidence_dialog),
            ("Teste t", self.show_t_test_dialog),
            ("Teste F", self.show_f_test_dialog)
        ]
        
        for text, handler in analyses:
            btn = QPushButton(text)
            btn.setMinimumHeight(35)
            btn.setStyleSheet("QPushButton { font-weight: bold; }")
            btn.clicked.connect(handler)
            layout.addWidget(btn)
        
        group.setLayout(layout)
        return group

    def create_options_section(self) -> QGroupBox:
        """Create result options section."""
        group = QGroupBox("Opções de Resultado")
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("Copiar")
        self.copy_button.setMinimumHeight(35)
        self.copy_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.copy_button.clicked.connect(lambda: self.copy_to_clipboard(self.result_text.toPlainText()))
        export_layout.addWidget(self.copy_button)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.setMinimumHeight(35)
        self.save_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.save_button.clicked.connect(lambda: self.save_to_file(self.result_text.toPlainText(), "Análise Estatística"))
        export_layout.addWidget(self.save_button)
        
        layout.addLayout(export_layout)
        
        group.setLayout(layout)
        return group

    def create_results_section(self) -> QGroupBox:
        """Create the results section."""
        group = QGroupBox("Resultados da Análise Estatística")
        layout = QVBoxLayout()
        
        # Results display
        self.result_text = ZoomableTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(500)
        self.result_text.setPlaceholderText("Os resultados da análise estatística aparecerão aqui...")
        layout.addWidget(self.result_text)
        
        group.setLayout(layout)
        return group

    def analyze_complete_statistics(self):
        """Executa análise estatística completa."""
        try:
            # Processar dados
            raw_text = self.data_input.toPlainText()
            data = self.parse_data(raw_text)
            
            if not data:
                self.result_text.setText("Erro: Nenhum dado válido inserido")
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
            
            # Intervalos de confiança
            ci_95 = confidence_interval_mean_small_n(data, 0.95) if len(data) < 30 else confidence_interval_mean_large_n(data, 0.95)
            
            # Formatação dos resultados
            result = f"ANÁLISE ESTATÍSTICA COMPLETA\n"
            result += f"{'='*60}\n\n"
            result += f"DADOS ANALISADOS: {data}\n"
            result += f"{'='*60}\n\n"
            
            result += f"ESTATÍSTICA DESCRITIVA\n"
            result += f"{'-'*30}\n"
            result += f"n (tamanho da amostra): {len(data)}\n"
            result += f"Média (x̄): {mean_val:.6g}\n"
            result += f"Variância amostral (s²): {variance:.6g}\n"
            result += f"Desvio padrão amostral (s): {std_dev:.6g}\n"
            result += f"Desvio médio: {mean_dev:.6g}\n"
            result += f"Coeficiente de variação (CV): {cv:.3f}%\n"
            result += f"Fator de correção: {corr_factor:.6g}\n\n"
            
            if reference is not None:
                result += f"DESVIOS ABSOLUTOS (referência = {reference}):\n"
                for i, dev in enumerate(abs_dev):
                    result += f"  |x{i+1} - ref| = |{data[i]} - {reference}| = {dev:.6g}\n"
            else:
                result += f"DESVIOS ABSOLUTOS (referência = média = {mean_val:.6g}):\n"
                for i, dev in enumerate(abs_dev):
                    result += f"  |x{i+1} - x̄| = |{data[i]} - {mean_val:.6g}| = {dev:.6g}\n"
            
            result += f"\n\nINTERVALO DE CONFIANÇA (95%)\n"
            result += f"{'-'*30}\n"
            method_name = "t de Student" if len(data) < 30 else "Distribuição Normal (z)"
            result += f"Método: {method_name} (n = {len(data)})\n"
            result += f"Margem de erro: ±{ci_95['margin_error']:.6g}\n"
            result += f"Intervalo: [{ci_95['lower_limit']:.6g}, {ci_95['upper_limit']:.6g}]\n"
            
            self.result_text.setText(result)
            
        except Exception as e:
            self.result_text.setText(f"Erro: {str(e)}")

    def calculate_descriptive_stats(self):
        """Calcula apenas estatística descritiva."""
        self.analyze_complete_statistics()

    def show_confidence_dialog(self):
        """Mostra diálogo simples para intervalos de confiança."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Intervalos de Confiança")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Instruções
        instructions = QLabel("Usa os dados do campo principal. Configure o nível de confiança:")
        layout.addWidget(instructions)
        
        # Controles
        form_layout = QFormLayout()
        
        confidence_input = QDoubleSpinBox()
        confidence_input.setRange(0.01, 0.99)
        confidence_input.setValue(0.95)
        confidence_input.setSingleStep(0.01)
        confidence_input.setDecimals(3)
        form_layout.addRow("Nível de confiança:", confidence_input)
        
        layout.addLayout(form_layout)
        
        # Resultado
        result_text = ZoomableDialogTextEdit()
        result_text.setReadOnly(True)
        result_text.setMinimumHeight(250)
        layout.addWidget(result_text)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        calc_btn = QPushButton("Calcular")
        calc_btn.clicked.connect(lambda: self.calculate_confidence_dialog(confidence_input.value(), result_text))
        buttons_layout.addWidget(calc_btn)
        
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(dialog.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def calculate_confidence_dialog(self, confidence, result_widget):
        """Calcula intervalo de confiança no diálogo."""
        try:
            data = self.parse_data(self.data_input.toPlainText())
            if not data:
                result_widget.setText("Erro: Nenhum dado válido inserido no campo principal")
                return
            
            if len(data) < 30:
                result = confidence_interval_mean_small_n(data, confidence)
                method_used = "t de Student"
            else:
                result = confidence_interval_mean_large_n(data, confidence)
                method_used = "Distribuição Normal (z)"
            
            output = f"INTERVALO DE CONFIANÇA\n"
            output += f"{'='*40}\n"
            output += f"Dados: {data}\n"
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
            
            result_widget.setText(output)
            
        except Exception as e:
            result_widget.setText(f"Erro: {str(e)}")

    def show_t_test_dialog(self):
        """Mostra diálogo para teste t."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Teste t - Comparação de Médias")
        dialog.setMinimumSize(500, 500)
        
        layout = QVBoxLayout()
        
        # Entrada de dados
        form_layout = QFormLayout()
        
        data1_input = ZoomableDataInput()
        data1_input.setPlaceholderText("Amostra 1: valores separados por vírgula")
        data1_input.setMaximumHeight(60)
        form_layout.addRow("Dados 1:", data1_input)
        
        data2_input = ZoomableDataInput()
        data2_input.setPlaceholderText("Amostra 2: valores separados por vírgula")
        data2_input.setMaximumHeight(60)
        form_layout.addRow("Dados 2:", data2_input)
        
        confidence_input = QDoubleSpinBox()
        confidence_input.setRange(0.01, 0.99)
        confidence_input.setValue(0.95)
        confidence_input.setSingleStep(0.01)
        confidence_input.setDecimals(3)
        form_layout.addRow("Nível de confiança:", confidence_input)
        
        layout.addLayout(form_layout)
        
        # Resultado
        result_text = ZoomableDialogTextEdit()
        result_text.setReadOnly(True)
        result_text.setMinimumHeight(250)
        layout.addWidget(result_text)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        calc_btn = QPushButton("Calcular Teste t")
        calc_btn.clicked.connect(lambda: self.calculate_t_test_dialog(
            data1_input.toPlainText(), data2_input.toPlainText(), 
            confidence_input.value(), result_text))
        buttons_layout.addWidget(calc_btn)
        
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(dialog.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def calculate_t_test_dialog(self, data1_text, data2_text, confidence, result_widget):
        """Calcula teste t no diálogo."""
        try:
            data1 = self.parse_data(data1_text)
            data2 = self.parse_data(data2_text)
            
            if not data1 or not data2:
                result_widget.setText("Erro: Dados inválidos em uma ou ambas as amostras")
                return
            
            result = t_test_two_means(data1, data2, confidence)
            
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
            
            result_widget.setText(output)
            
        except Exception as e:
            result_widget.setText(f"Erro: {str(e)}")

    def show_f_test_dialog(self):
        """Mostra diálogo para teste F."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Teste F - Comparação de Variâncias")
        dialog.setMinimumSize(500, 500)
        
        layout = QVBoxLayout()
        
        # Entrada de dados
        form_layout = QFormLayout()
        
        data1_input = ZoomableDataInput()
        data1_input.setPlaceholderText("Amostra 1: valores separados por vírgula")
        data1_input.setMaximumHeight(60)
        form_layout.addRow("Dados 1:", data1_input)
        
        data2_input = ZoomableDataInput()
        data2_input.setPlaceholderText("Amostra 2: valores separados por vírgula")
        data2_input.setMaximumHeight(60)
        form_layout.addRow("Dados 2:", data2_input)
        
        confidence_input = QDoubleSpinBox()
        confidence_input.setRange(0.01, 0.99)
        confidence_input.setValue(0.95)
        confidence_input.setSingleStep(0.01)
        confidence_input.setDecimals(3)
        form_layout.addRow("Nível de confiança:", confidence_input)
        
        layout.addLayout(form_layout)
        
        # Resultado
        result_text = ZoomableDialogTextEdit()
        result_text.setReadOnly(True)
        result_text.setMinimumHeight(250)
        layout.addWidget(result_text)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        calc_btn = QPushButton("Calcular Teste F")
        calc_btn.clicked.connect(lambda: self.calculate_f_test_dialog(
            data1_input.toPlainText(), data2_input.toPlainText(), 
            confidence_input.value(), result_text))
        buttons_layout.addWidget(calc_btn)
        
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(dialog.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def calculate_f_test_dialog(self, data1_text, data2_text, confidence, result_widget):
        """Calcula teste F no diálogo."""
        try:
            data1 = self.parse_data(data1_text)
            data2 = self.parse_data(data2_text)
            
            if not data1 or not data2:
                result_widget.setText("Erro: Dados inválidos em uma ou ambas as amostras")
                return
            
            result = f_test_two_variances(data1, data2, confidence)
            
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
            
            result_widget.setText(output)
            
        except Exception as e:
            result_widget.setText(f"Erro: {str(e)}")

    def clear_inputs(self):
        """Limpa os campos de entrada."""
        self.data_input.clear()
        self.reference_input.clear()
        self.result_text.clear()

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
        
        return values

    def copy_to_clipboard(self, text: str):
        """Copia o texto para a área de transferência."""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Feedback visual (opcional)
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
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Sucesso")
                msg.setText(f"💾 Arquivo salvo com sucesso!\n\n{file_path}")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Erro")
            msg.setText(f"Erro ao salvar arquivo:\n{str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
