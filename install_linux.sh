#!/bin/bash

# =============================================================================
# HeisenLab - Script de Instalação para Linux (Padrão FHS)
# =============================================================================
# Este script instala automaticamente o HeisenLab em /opt/heisenlab
# Compatível com: Ubuntu, Debian, Fedora, CentOS, Arch Linux
# =============================================================================

set -e  # Sair se algum comando falhar

# Diretórios de instalação (padrão Linux)
INSTALL_DIR="/opt/heisenlab"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor/256x256/apps"
USER_DATA_DIR="$HOME/.local/share/heisenlab"
USER_CONFIG_DIR="$HOME/.config/heisenlab"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner do HeisenLab
show_banner() {
    echo -e "${BLUE}"
    echo "======================================================="
    echo "  _   _      _                _            _     "
    echo " | | | | ___(_)___  ___ _ __ | |    __ _ | |__  "
    echo " | |_| |/ _ \ / __|/ _ \ '_ \| |   / _\` || '_ \ "
    echo " |  _  |  __/ \__ \  __/ | | | |__| (_| || |_) |"
    echo " |_| |_|\___|_|___/\___|_| |_|_____\__,_||_.__/ "
    echo ""
    echo "         Laboratório Químico Virtual"
    echo "======================================================="
    echo -e "${NC}"
}

# Detectar distribuição Linux
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        DISTRO=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
        VERSION=$(lsb_release -sr)
    else
        DISTRO="unknown"
        VERSION="unknown"
    fi
    
    log_info "Distribuição detectada: $DISTRO $VERSION"
}

# Verificar se está rodando com privilégios adequados
check_privileges() {
    if [[ $EUID -eq 0 ]]; then
        log_error "Este script não deve ser executado como root!"
        log_info "Execute como usuário normal. O script pedirá sudo quando necessário."
        exit 1
    fi
    
    # Verificar se sudo está disponível
    if ! command -v sudo >/dev/null 2>&1; then
        log_error "sudo não encontrado! Este script precisa de sudo para instalar em /opt/"
        exit 1
    fi
    
    # Testar acesso sudo
    if ! sudo -n true 2>/dev/null; then
        log_info "Este script precisa de privilégios sudo para instalar em /opt/"
        log_info "Você será solicitado a inserir sua senha quando necessário."
        sudo -v || exit 1
    fi
}

# Instalar dependências do sistema
install_system_deps() {
    log_info "Instalando dependências do sistema..."
    
    case $DISTRO in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y \
                python3 \
                python3-pip \
                python3-venv \
                python3-dev \
                build-essential \
                git \
                curl \
                wget \
                qt6-base-dev \
                qt6-tools-dev \
                libqt6widgets6 \
                libqt6core6 \
                libqt6gui6 \
                python3-tk \
                libfontconfig1-dev \
                libfreetype6-dev \
                libxrender1 \
                libxext6 \
                desktop-file-utils \
                shared-mime-info \
                hicolor-icon-theme
            ;;
        fedora|centos|rhel)
            if command -v dnf > /dev/null; then
                sudo dnf install -y \
                    python3 \
                    python3-pip \
                    python3-devel \
                    gcc \
                    gcc-c++ \
                    git \
                    curl \
                    wget \
                    qt6-qtbase-devel \
                    qt6-qttools-devel \
                    python3-tkinter \
                    fontconfig-devel \
                    freetype-devel \
                    desktop-file-utils \
                    shared-mime-info \
                    hicolor-icon-theme
            else
                sudo yum install -y \
                    python3 \
                    python3-pip \
                    python3-devel \
                    gcc \
                    gcc-c++ \
                    git \
                    curl \
                    wget \
                    qt6-qtbase-devel \
                    qt6-qttools-devel \
                    tkinter \
                    fontconfig-devel \
                    freetype-devel \
                    desktop-file-utils \
                    shared-mime-info \
                    hicolor-icon-theme
            fi
            ;;
        arch|manjaro)
            sudo pacman -Sy --noconfirm \
                python \
                python-pip \
                base-devel \
                git \
                curl \
                wget \
                qt6-base \
                qt6-tools \
                tk \
                fontconfig \
                freetype2 \
                desktop-file-utils \
                shared-mime-info \
                hicolor-icon-theme
            ;;
        *)
            log_warning "Distribuição não reconhecida. Tentando instalação genérica..."
            log_info "Certifique-se de ter Python 3.8+, pip, git e Qt6 instalados"
            ;;
    esac
    
    log_success "Dependências do sistema instaladas"
}

# Verificar dependências opcionais
check_optional_deps() {
    log_info "Verificando dependências opcionais..."
    
    # Verificar desktop-file-utils
    if ! command -v desktop-file-validate >/dev/null 2>&1; then
        log_warning "desktop-file-utils não encontrado - validação de .desktop será ignorada"
        case $DISTRO in
            ubuntu|debian)
                log_info "Para instalar: sudo apt install desktop-file-utils"
                ;;
            fedora|centos|rhel)
                log_info "Para instalar: sudo dnf install desktop-file-utils"
                ;;
            arch|manjaro)
                log_info "Para instalar: sudo pacman -S desktop-file-utils"
                ;;
        esac
    fi
    
    # Verificar ferramentas de cache
    if ! command -v update-desktop-database >/dev/null 2>&1; then
        log_warning "update-desktop-database não encontrado"
    fi
    
    if ! command -v update-mime-database >/dev/null 2>&1; then
        log_warning "update-mime-database não encontrado"
    fi
    
    if ! command -v gtk-update-icon-cache >/dev/null 2>&1; then
        log_warning "gtk-update-icon-cache não encontrado"
    fi
}
check_python_version() {
    log_info "Verificando versão do Python..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 não encontrado! Instale Python 3.8 ou superior."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        log_success "Python $PYTHON_VERSION encontrado (OK)"
    else
        log_error "Python $PYTHON_VERSION encontrado, mas é necessário Python $REQUIRED_VERSION ou superior"
        exit 1
    fi
}

# Criar diretórios de instalação
create_install_directories() {
    log_info "Criando diretórios de instalação..."
    
    # Criar diretório principal (requer sudo)
    sudo mkdir -p "$INSTALL_DIR"
    sudo mkdir -p "$BIN_DIR"
    sudo mkdir -p "$DESKTOP_DIR"
    sudo mkdir -p "$ICON_DIR"
    
    # Criar diretórios do usuário
    mkdir -p "$USER_DATA_DIR"
    mkdir -p "$USER_CONFIG_DIR"
    
    log_success "Diretórios criados"
}

# Instalar aplicação em /opt/heisenlab
install_application() {
    log_info "Instalando HeisenLab em $INSTALL_DIR..."
    
    # Copiar arquivos do projeto
    sudo cp -r heisenlab/ "$INSTALL_DIR/"
    sudo cp main.py "$INSTALL_DIR/"
    sudo cp requirements.txt "$INSTALL_DIR/"
    
    # Copiar assets se existirem
    if [ -d "assets" ]; then
        sudo cp -r assets/ "$INSTALL_DIR/"
    fi
    
    # Criar ambiente virtual
    sudo python3 -m venv "$INSTALL_DIR/venv"
    
    # Ativar e instalar dependências
    sudo "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    sudo "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    
    # Definir permissões adequadas
    sudo chown -R root:root "$INSTALL_DIR"
    sudo chmod -R 755 "$INSTALL_DIR"
    sudo chmod +x "$INSTALL_DIR/main.py"
    
    log_success "Aplicação instalada em $INSTALL_DIR"
}

# Verificar instalação
verify_installation() {
    log_info "Verificando instalação..."
    
    # Testar imports principais
    sudo "$INSTALL_DIR/venv/bin/python3" -c "
import sys
try:
    import PySide6
    import matplotlib
    import numpy
    import scipy
    import pandas
    import mendeleev
    import sympy
    print('✓ Todas as dependências estão funcionando')
except ImportError as e:
    print(f'✗ Erro na importação: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Verificação concluída com sucesso!"
    else
        log_error "Erro na verificação da instalação"
        exit 1
    fi
}

# Criar script de execução global
create_run_script() {
    log_info "Criando script de execução global..."
    
    sudo tee "$BIN_DIR/heisenlab" > /dev/null << 'EOF'
#!/bin/bash
# HeisenLab Launcher Script

# Definir variáveis de ambiente
export HEISENLAB_HOME="/opt/heisenlab"
export HEISENLAB_DATA_DIR="$HOME/.local/share/heisenlab"
export HEISENLAB_CONFIG_DIR="$HOME/.config/heisenlab"

# Criar diretórios de dados do usuário se não existirem
mkdir -p "$HEISENLAB_DATA_DIR"
mkdir -p "$HEISENLAB_CONFIG_DIR"

# Executar o HeisenLab
cd "$HEISENLAB_HOME"
"$HEISENLAB_HOME/venv/bin/python3" main.py "$@"
EOF
    
    sudo chmod +x "$BIN_DIR/heisenlab"
    log_success "Script de execução criado: $BIN_DIR/heisenlab"
    log_info "Agora você pode executar 'heisenlab' de qualquer lugar no terminal"
}

# Instalar ícone do sistema
install_icon() {
    log_info "Instalando ícone do sistema..."
    
    # Usar logo.png como ícone principal
    if [ -f "assets/logo.png" ]; then
        sudo cp "assets/logo.png" "$ICON_DIR/com.heisenlab.HeisenLab.png"
        log_success "Ícone principal instalado"
    elif [ -f "assets/banner.png" ]; then
        log_warning "Logo não encontrado, usando banner como fallback"
        sudo cp "assets/banner.png" "$ICON_DIR/com.heisenlab.HeisenLab.png"
        log_success "Ícone (banner) instalado"
    else
        log_warning "Nenhum ícone encontrado em assets/"
    fi
    
    # Atualizar cache de ícones se possível
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
    fi
}

# Criar arquivo desktop seguindo padrões FreeDesktop
create_desktop_file() {
    log_info "Criando arquivo .desktop..."
    
    sudo tee "$DESKTOP_DIR/com.heisenlab.HeisenLab.desktop" > /dev/null << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=HeisenLab
Name[pt]=HeisenLab
Name[pt_BR]=HeisenLab
GenericName=Chemistry Laboratory
GenericName[pt]=Laboratório de Química
GenericName[pt_BR]=Laboratório de Química
Comment=Virtual Chemistry Laboratory for analytical calculations and molecular visualization
Comment[pt]=Laboratório Químico Virtual para cálculos analíticos e visualização molecular
Comment[pt_BR]=Laboratório Químico Virtual para cálculos analíticos e visualização molecular
Exec=heisenlab
Icon=com.heisenlab.HeisenLab
Terminal=false
Categories=Education;Science;Chemistry;
Keywords=chemistry;laboratory;analytical;calculations;molecules;periodic;table;elements;
Keywords[pt]=química;laboratório;analítico;cálculos;moléculas;tabela;periódica;elementos;
Keywords[pt_BR]=química;laboratório;analítico;cálculos;moléculas;tabela;periódica;elementos;
StartupNotify=true
StartupWMClass=HeisenLab
MimeType=application/x-heisenlab-project;
EOF
    
    sudo chmod 644 "$DESKTOP_DIR/com.heisenlab.HeisenLab.desktop"
    
    # Validar arquivo desktop se possível
    if command -v desktop-file-validate >/dev/null 2>&1; then
        if desktop-file-validate "$DESKTOP_DIR/com.heisenlab.HeisenLab.desktop"; then
            log_success "Arquivo desktop validado e criado"
        else
            log_warning "Arquivo desktop criado mas com avisos de validação"
        fi
    else
        log_success "Arquivo desktop criado"
    fi
    
    # Atualizar banco de dados de aplicações
    if command -v update-desktop-database >/dev/null 2>&1; then
        sudo update-desktop-database /usr/share/applications 2>/dev/null || true
    fi
}

# Criar tipo MIME personalizado
create_mime_type() {
    log_info "Registrando tipo MIME personalizado..."
    
    MIME_DIR="$HOME/.local/share/mime/packages"
    MIME_FILE="$MIME_DIR/com.heisenlab.HeisenLab.xml"
    
    mkdir -p "$MIME_DIR"
    
    cat > "$MIME_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-heisenlab-project">
    <comment>HeisenLab Project File</comment>
    <comment xml:lang="pt">Arquivo de Projeto HeisenLab</comment>
    <comment xml:lang="pt_BR">Arquivo de Projeto HeisenLab</comment>
    <glob pattern="*.hlab"/>
    <glob pattern="*.heisenlab"/>
  </mime-type>
</mime-info>
EOF
    
    # Atualizar banco de dados MIME
    if command -v update-mime-database >/dev/null 2>&1; then
        update-mime-database "$HOME/.local/share/mime" 2>/dev/null || true
        log_success "Tipo MIME registrado"
    else
        log_warning "update-mime-database não encontrado, tipo MIME pode não funcionar"
    fi
}

# Criar tipo MIME personalizado
create_mime_type() {
    log_info "Registrando tipo MIME personalizado..."
    
    MIME_DIR="$HOME/.local/share/mime/packages"
    MIME_FILE="$MIME_DIR/com.heisenlab.HeisenLab.xml"
    
    mkdir -p "$MIME_DIR"
    
    cat > "$MIME_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-heisenlab-project">
    <comment>HeisenLab Project File</comment>
    <comment xml:lang="pt">Arquivo de Projeto HeisenLab</comment>
    <comment xml:lang="pt_BR">Arquivo de Projeto HeisenLab</comment>
    <glob pattern="*.hlab"/>
    <glob pattern="*.heisenlab"/>
  </mime-type>
</mime-info>
EOF
    
    # Atualizar banco de dados MIME
    if command -v update-mime-database >/dev/null 2>&1; then
        update-mime-database "$HOME/.local/share/mime" 2>/dev/null || true
        log_success "Tipo MIME registrado"
    else
        log_warning "update-mime-database não encontrado, tipo MIME pode não funcionar"
    fi
}

# Configurar variáveis de ambiente
setup_environment() {
    log_info "Configurando diretórios de dados do usuário..."
    
    # Criar diretórios de dados e configuração do usuário
    mkdir -p "$USER_DATA_DIR"
    mkdir -p "$USER_CONFIG_DIR"
    
    log_success "Diretórios de dados configurados"
    log_info "Dados do usuário: $USER_DATA_DIR"
    log_info "Configurações: $USER_CONFIG_DIR"
}

# Criar desinstalador
create_uninstaller() {
# Criar desinstalador
create_uninstaller() {
    log_info "Criando script de desinstalação..."
    
    sudo tee "$BIN_DIR/heisenlab-uninstall" > /dev/null << 'EOF'
#!/bin/bash
# Script de desinstalação do HeisenLab

echo "Desinstalando HeisenLab..."

# Verificar se está sendo executado como usuário normal
if [[ $EUID -eq 0 ]]; then
    echo "❌ Este script não deve ser executado como root!"
    echo "Execute como usuário normal: heisenlab-uninstall"
    exit 1
fi

# Verificar sudo
if ! sudo -n true 2>/dev/null; then
    echo "Este script precisa de privilégios sudo para remover arquivos de /opt/"
    sudo -v || exit 1
fi

# Remover arquivos do sistema (requer sudo)
echo "Removendo instalação do sistema..."
sudo rm -rf "/opt/heisenlab"
sudo rm -f "/usr/local/bin/heisenlab"
sudo rm -f "/usr/share/applications/com.heisenlab.HeisenLab.desktop"
sudo rm -f "/usr/share/icons/hicolor/256x256/apps/com.heisenlab.HeisenLab.png"
sudo rm -f "/usr/share/mime/packages/com.heisenlab.HeisenLab.xml"
echo "✓ Arquivos do sistema removidos"

# Perguntar sobre dados do usuário
echo ""
read -p "Remover dados do usuário? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/.local/share/heisenlab"
    rm -rf "$HOME/.config/heisenlab"
    echo "✓ Dados do usuário removidos"
else
    echo "✓ Dados do usuário preservados"
fi

# Atualizar caches do sistema
echo "Atualizando caches do sistema..."
if command -v update-desktop-database >/dev/null 2>&1; then
    sudo update-desktop-database /usr/share/applications 2>/dev/null || true
fi

if command -v update-mime-database >/dev/null 2>&1; then
    sudo update-mime-database /usr/share/mime 2>/dev/null || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi

# Remover o próprio desinstalador
sudo rm -f "/usr/local/bin/heisenlab-uninstall"

echo ""
echo "🎉 HeisenLab desinstalado com sucesso!"
EOF
    
    sudo chmod +x "$BIN_DIR/heisenlab-uninstall"
    log_success "Script de desinstalação criado: $BIN_DIR/heisenlab-uninstall"
    log_info "Para desinstalar: execute 'heisenlab-uninstall' no terminal"
}
}

# Mostrar instruções finais
show_final_instructions() {
    echo ""
    log_success "🎉 Instalação do HeisenLab concluída com sucesso!"
    echo ""
    echo -e "${GREEN}Como executar o HeisenLab:${NC}"
    echo "  • No terminal: heisenlab"
    echo "  • No menu: Aplicações > Educação > HeisenLab"
    echo "  • Busca do sistema: digite 'HeisenLab'"
    echo ""
    echo -e "${GREEN}Localização dos arquivos:${NC}"
    echo "  • Programa principal: $INSTALL_DIR"
    echo "  • Script executável: $BIN_DIR/heisenlab"
    echo "  • Dados do usuário: $USER_DATA_DIR"
    echo "  • Configurações: $USER_CONFIG_DIR"
    echo "  • Ícone: $ICON_DIR/com.heisenlab.HeisenLab.png"
    echo "  • Menu: $DESKTOP_DIR/com.heisenlab.HeisenLab.desktop"
    echo ""
    echo -e "${YELLOW}Comandos úteis:${NC}"
    echo "  • Para executar: heisenlab"
    echo "  • Para desinstalar: heisenlab-uninstall"
    echo "  • Para reportar bugs: https://github.com/Cabral567/HeisenLab/issues"
    echo ""
    echo -e "${BLUE}Nota:${NC} O programa agora está instalado globalmente no sistema!"
    echo "Você pode executar 'heisenlab' de qualquer diretório."
    echo ""
}

# Função principal
main() {
    show_banner
    
    log_info "Iniciando instalação do HeisenLab..."
    
    check_privileges
    detect_distro
    check_python_version
    check_optional_deps
    install_system_deps
    create_install_directories
    install_application
    verify_installation
    create_run_script
    install_icon
    create_desktop_file
    setup_environment
    create_uninstaller
    
    show_final_instructions
}

# Executar função principal
main "$@"
