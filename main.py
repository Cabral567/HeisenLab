from heisenlab.ui.main_window import MainWindow
from heisenlab.ui.main_window import run
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import sys
import signal

def signal_handler(signum, frame):
    """Handler para sinais do sistema (Ctrl+C)"""
    print("\nSinal de interrupção recebido (Ctrl+C)")
    print("Fechando aplicação...")
    
    # Tentar fechar a aplicação Qt de forma limpa
    app = QApplication.instance()
    if app:
        print("Fechando QApplication...")
        app.quit()
    
    print("Saindo...")
    sys.exit(0)

def start_main_app():
    """Inicia a aplicação principal"""
    try:
        print("Iniciando função start_main_app()...")
        print("Importando módulos da aplicação principal...")
        
        # Tentar importar os módulos primeiro para detectar problemas
        try:
            print("   - Importando MainWindow...")
            from heisenlab.ui.main_window import MainWindow
            print("   MainWindow importado com sucesso")
        except Exception as e:
            print(f"   Erro ao importar MainWindow: {e}")
            return
            
        print("Executando run()...")
        result = run()
        print(f"run() executado com sucesso! Resultado: {result}")
        return result
        
    except Exception as e:
        print(f"Erro ao iniciar aplicação principal: {e}")
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        print("\nInterrupção por teclado detectada em start_main_app")
        raise

if __name__ == "__main__":
    # Configurar handler para sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=== INICIANDO HEISENLAB ===")
    print("Use Ctrl+C para sair a qualquer momento")
    
    qt_app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    print("Executando loop de eventos da aplicação...")
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)
    exit_code = qt_app.exec()
    print(f"Aplicação finalizada com código: {exit_code}")
    sys.exit(exit_code)
