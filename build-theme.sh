#!/bin/bash

# Script de compilación de temas personalizados para adw-gtk3
# Autor: Script generado para compilar temas GTK personalizados
# Uso: ./build-theme.sh [opciones]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

# Directorios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
SASS_DIR="$SRC_DIR/sass"
BUILD_DIR="$SCRIPT_DIR/build"
INSTALL_DIR="$HOME/.local/share/themes"
BASE16_DIR="$SCRIPT_DIR/base16-schemes"
BASE16_GENERATOR="$SCRIPT_DIR/scripts/base16-generator.py"

# Nombre del tema
THEME_NAME="adw-gtk3"

# Variables de control
COMPILE_LIGHT=false
COMPILE_DARK=false
INSTALL=false
CLEAN=false
BASE16_SCHEME=""
LIST_SCHEMES=false
CUSTOM_NAME=""

# Función para mostrar ayuda
show_help() {
    cat << EOF
${BLUE}Script de Compilación de Temas adw-gtk3${NC}

${YELLOW}Uso:${NC}
    $0 [opciones]

${YELLOW}Opciones:${NC}
    -l, --light       Compilar solo tema claro
    -d, --dark        Compilar solo tema oscuro
    -a, --all         Compilar ambos temas (por defecto)
    -i, --install     Instalar en ~/.local/share/themes/
    -c, --clean       Limpiar archivos compilados
    -h, --help        Mostrar esta ayuda
    
${YELLOW}Opciones Base16:${NC}
    --base16 <scheme>     Usar esquema de colores base16
    --list-schemes        Listar esquemas base16 disponibles

${YELLOW}Opciones de Personalización:${NC}
    --name <nombre>       Nombre personalizado para el tema

${YELLOW}Ejemplos:${NC}
    $0 --all --install                          # Compilar ambos temas e instalar
    $0 --light                                  # Compilar solo tema claro
    $0 --base16 gruvbox-dark --all              # Compilar con esquema base16
    $0 --base16 nord --name my-nord --install   # Tema base16 con nombre custom
    $0 --name my-theme --all --install          # Tema con nombre personalizado
    $0 --list-schemes                           # Ver esquemas disponibles
    $0 --clean                                  # Limpiar archivos compilados

${YELLOW}Dependencias:${NC}
    - sass (Dart Sass)
    - python3 (para temas base16)
    - python3-yaml (para temas base16)

EOF
}

# Función para verificar dependencias
check_dependencies() {
    echo -e "${BLUE}Verificando dependencias...${NC}"
    
    if ! command -v sass &> /dev/null; then
        echo -e "${RED}Error: sass no está instalado.${NC}"
        echo -e "${YELLOW}Instala sass con:${NC}"
        echo "  npm install -g sass"
        echo "  o"
        echo "  sudo apt install dart-sass (Debian/Ubuntu)"
        echo "  sudo dnf install dart-sass (Fedora)"
        echo "  sudo pacman -S dart-sass (Arch)"
        exit 1
    fi
    
    # Verificar dependencias de base16 si se usa
    if [ -n "$BASE16_SCHEME" ]; then
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}Error: python3 no está instalado (requerido para base16).${NC}"
            exit 1
        fi
        
        if ! python3 -c "import yaml" &> /dev/null; then
            echo -e "${RED}Error: python3-yaml no está instalado.${NC}"
            echo -e "${YELLOW}Instala con:${NC}"
            echo "  pip3 install pyyaml"
            echo "  o"
            echo "  sudo apt install python3-yaml (Debian/Ubuntu)"
            echo "  sudo dnf install python3-pyyaml (Fedora)"
            echo "  sudo pacman -S python-yaml (Arch)"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✓ Todas las dependencias están instaladas${NC}"
}

# Función para listar esquemas base16 disponibles
list_base16_schemes() {
    echo -e "${BLUE}Esquemas Base16 Disponibles:${NC}\n"
    
    if [ ! -d "$BASE16_DIR" ] || [ -z "$(ls -A "$BASE16_DIR"/*.yaml 2>/dev/null)" ]; then
        echo -e "${YELLOW}No se encontraron esquemas base16.${NC}"
        echo -e "${YELLOW}Agrega archivos .yaml en: $BASE16_DIR${NC}"
        return
    fi
    
    for scheme_file in "$BASE16_DIR"/*.yaml; do
        if [ -f "$scheme_file" ]; then
            local scheme_name=$(basename "$scheme_file" .yaml)
            local scheme_title=$(grep '^scheme:' "$scheme_file" | sed 's/scheme: *"\?\([^"]*\)"\?/\1/')
            local scheme_author=$(grep '^author:' "$scheme_file" | sed 's/author: *"\?\([^"]*\)"\?/\1/')
            
            echo -e "  ${GREEN}$scheme_name${NC}"
            [ -n "$scheme_title" ] && echo -e "    Nombre: $scheme_title"
            [ -n "$scheme_author" ] && echo -e "    Autor: $scheme_author"
            echo ""
        fi
    done
    
    echo -e "${YELLOW}Uso:${NC} $0 --base16 <nombre-esquema> --all --install"
}

# Función para generar SCSS desde base16
generate_base16_scss() {
    local scheme_name=$1
    local scheme_file="$BASE16_DIR/${scheme_name}.yaml"
    local output_file="$SASS_DIR/_base16-override.scss"
    
    if [ ! -f "$scheme_file" ]; then
        echo -e "${RED}Error: Esquema base16 no encontrado: $scheme_name${NC}"
        echo -e "${YELLOW}Esquemas disponibles:${NC}"
        list_base16_schemes
        exit 1
    fi
    
    echo -e "${BLUE}Generando SCSS desde esquema base16: $scheme_name${NC}"
    
    python3 "$BASE16_GENERATOR" "$scheme_file" -o "$output_file"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ SCSS base16 generado exitosamente${NC}"
        # Actualizar nombre del tema para incluir el esquema
        THEME_NAME="adw-gtk3-${scheme_name}"
    else
        echo -e "${RED}Error al generar SCSS base16${NC}"
        exit 1
    fi
}

# Función para limpiar archivos base16
clean_base16() {
    local override_file="$SASS_DIR/_base16-override.scss"
    if [ -f "$override_file" ]; then
        rm "$override_file"
        echo -e "${GREEN}✓ Archivo base16 override eliminado${NC}"
    fi
}

# Función para limpiar archivos compilados
clean_build() {
    echo -e "${BLUE}Limpiando archivos compilados...${NC}"
    
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
        echo -e "${GREEN}✓ Directorio build eliminado${NC}"
    fi
    
    # Limpiar archivos CSS generados en src
    find "$SRC_DIR" -name "*.css" -type f -delete 2>/dev/null || true
    
    # Limpiar archivos base16
    clean_base16
    
    echo -e "${GREEN}✓ Limpieza completada${NC}"
}

# Función para crear directorios de build
create_build_dirs() {
    local theme_variant=$1
    local theme_dir="$BUILD_DIR/$theme_variant"
    
    mkdir -p "$theme_dir/gtk-3.0"
    mkdir -p "$theme_dir/gtk-4.0/assets"
}

# Función para compilar SASS a CSS
compile_sass() {
    local input=$1
    local output=$2
    local description=$3
    
    echo -e "${BLUE}Compilando $description...${NC}"
    sass --no-source-map "$input" "$output"
    echo -e "${GREEN}✓ $description compilado${NC}"
}

# Función para copiar assets
copy_assets() {
    local theme_variant=$1
    local theme_dir="$BUILD_DIR/$theme_variant"
    
    echo -e "${BLUE}Copiando assets para $theme_variant...${NC}"
    
    # Copiar assets GTK3
    if [ -d "$SRC_DIR/assets" ]; then
        cp -r "$SRC_DIR/assets" "$theme_dir/gtk-3.0/"
    fi
    
    # Copiar assets GTK4
    local gtk4_assets=(
        "bullet-symbolic.svg"
        "check-symbolic.svg"
        "dash-symbolic.svg"
        "devel-symbolic.svg"
    )
    
    for asset in "${gtk4_assets[@]}"; do
        if [ -f "$SRC_DIR/assets/$asset" ]; then
            cp "$SRC_DIR/assets/$asset" "$theme_dir/gtk-4.0/assets/"
        fi
    done
    
    echo -e "${GREEN}✓ Assets copiados${NC}"
}

# Función para copiar archivos CSS estáticos de GTK4
copy_gtk4_static() {
    local theme_variant=$1
    local theme_dir="$BUILD_DIR/$theme_variant"
    local src_theme_dir=""
    
    if [ "$theme_variant" = "$THEME_NAME" ]; then
        src_theme_dir="$SRC_DIR/theme-light/gtk4"
    else
        src_theme_dir="$SRC_DIR/theme-dark/gtk4"
    fi
    
    echo -e "${BLUE}Copiando archivos GTK4 estáticos...${NC}"
    
    # Copiar archivos CSS estáticos si existen
    if [ -f "$src_theme_dir/gtk.css" ]; then
        cp "$src_theme_dir/gtk.css" "$theme_dir/gtk-4.0/"
    fi
    
    if [ -f "$src_theme_dir/gtk-dark.css" ]; then
        cp "$src_theme_dir/gtk-dark.css" "$theme_dir/gtk-4.0/"
    fi
    
    if [ -f "$src_theme_dir/libadwaita.css" ]; then
        cp "$src_theme_dir/libadwaita.css" "$theme_dir/gtk-4.0/"
    fi
    
    echo -e "${GREEN}✓ Archivos GTK4 copiados${NC}"
}

# Función para crear index.theme
create_index_theme() {
    local theme_variant=$1
    local theme_dir="$BUILD_DIR/$theme_variant"
    local display_name=$2
    
    echo -e "${BLUE}Creando index.theme para $theme_variant...${NC}"
    
    cat > "$theme_dir/index.theme" << EOF
[Desktop Entry]
Type=X-GNOME-Metatheme
Name=$display_name
Comment=An unofficial GTK3 port of libadwaita
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=$theme_variant
MetacityTheme=$theme_variant
IconTheme=Adwaita
CursorTheme=Adwaita
ButtonLayout=close,minimize,maximize:menu
EOF
    
    echo -e "${GREEN}✓ index.theme creado${NC}"
}

# Función para copiar thumbnail
copy_thumbnail() {
    local theme_variant=$1
    local theme_dir="$BUILD_DIR/$theme_variant"
    local src_theme_dir=""
    
    if [ "$theme_variant" = "$THEME_NAME" ]; then
        src_theme_dir="$SRC_DIR/theme-light"
    else
        src_theme_dir="$SRC_DIR/theme-dark"
    fi
    
    if [ -f "$src_theme_dir/thumbnail-light.png" ]; then
        cp "$src_theme_dir/thumbnail-light.png" "$theme_dir/gtk-3.0/thumbnail.png"
    elif [ -f "$src_theme_dir/thumbnail-dark.png" ]; then
        cp "$src_theme_dir/thumbnail-dark.png" "$theme_dir/gtk-3.0/thumbnail.png"
    fi
}

# Función para compilar tema claro
compile_light_theme() {
    echo -e "\n${YELLOW}=== Compilando Tema Claro ===${NC}\n"
    
    local theme_dir="$BUILD_DIR/$THEME_NAME"
    create_build_dirs "$THEME_NAME"
    
    # Compilar GTK3 CSS
    compile_sass "$SASS_DIR/gtk.scss" "$theme_dir/gtk-3.0/gtk.css" "GTK3 Light"
    compile_sass "$SASS_DIR/gtk-dark.scss" "$theme_dir/gtk-3.0/gtk-dark.css" "GTK3 Dark variant"
    
    # Compilar GTK4 libadwaita tweaks
    if [ -f "$SASS_DIR/gtk4/libadwaita-tweaks.scss" ]; then
        compile_sass "$SASS_DIR/gtk4/libadwaita-tweaks.scss" "$theme_dir/gtk-4.0/libadwaita-tweaks.css" "GTK4 Libadwaita tweaks"
    fi
    
    # Copiar archivos estáticos
    copy_gtk4_static "$THEME_NAME"
    copy_assets "$THEME_NAME"
    copy_thumbnail "$THEME_NAME"
    create_index_theme "$THEME_NAME" "adw-gtk3"
    
    echo -e "\n${GREEN}✓ Tema claro compilado exitosamente${NC}\n"
}

# Función para compilar tema oscuro
compile_dark_theme() {
    echo -e "\n${YELLOW}=== Compilando Tema Oscuro ===${NC}\n"
    
    local theme_variant="${THEME_NAME}-dark"
    local theme_dir="$BUILD_DIR/$theme_variant"
    create_build_dirs "$theme_variant"
    
    # Compilar GTK3 CSS (usando los mismos archivos SASS)
    compile_sass "$SASS_DIR/gtk.scss" "$theme_dir/gtk-3.0/gtk.css" "GTK3 Dark"
    compile_sass "$SASS_DIR/gtk-dark.scss" "$theme_dir/gtk-3.0/gtk-dark.css" "GTK3 Dark variant"
    
    # Compilar GTK4 libadwaita tweaks
    if [ -f "$SASS_DIR/gtk4/libadwaita-tweaks.scss" ]; then
        compile_sass "$SASS_DIR/gtk4/libadwaita-tweaks.scss" "$theme_dir/gtk-4.0/libadwaita-tweaks.css" "GTK4 Libadwaita tweaks"
    fi
    
    # Copiar archivos estáticos
    copy_gtk4_static "$theme_variant"
    copy_assets "$theme_variant"
    copy_thumbnail "$theme_variant"
    create_index_theme "$theme_variant" "adw-gtk3-dark"
    
    echo -e "\n${GREEN}✓ Tema oscuro compilado exitosamente${NC}\n"
}

# Función para instalar temas
install_themes() {
    echo -e "\n${YELLOW}=== Instalando Temas ===${NC}\n"
    
    mkdir -p "$INSTALL_DIR"
    
    if [ "$COMPILE_LIGHT" = true ] || [ "$COMPILE_LIGHT" = false -a "$COMPILE_DARK" = false ]; then
        if [ -d "$BUILD_DIR/$THEME_NAME" ]; then
            echo -e "${BLUE}Instalando tema claro...${NC}"
            rm -rf "$INSTALL_DIR/$THEME_NAME"
            cp -r "$BUILD_DIR/$THEME_NAME" "$INSTALL_DIR/"
            echo -e "${GREEN}✓ Tema claro instalado en $INSTALL_DIR/$THEME_NAME${NC}"
        fi
    fi
    
    if [ "$COMPILE_DARK" = true ] || [ "$COMPILE_LIGHT" = false -a "$COMPILE_DARK" = false ]; then
        if [ -d "$BUILD_DIR/${THEME_NAME}-dark" ]; then
            echo -e "${BLUE}Instalando tema oscuro...${NC}"
            rm -rf "$INSTALL_DIR/${THEME_NAME}-dark"
            cp -r "$BUILD_DIR/${THEME_NAME}-dark" "$INSTALL_DIR/"
            echo -e "${GREEN}✓ Tema oscuro instalado en $INSTALL_DIR/${THEME_NAME}-dark${NC}"
        fi
    fi
    
    echo -e "\n${GREEN}✓ Instalación completada${NC}"
    echo -e "${YELLOW}Para activar el tema, usa:${NC}"
    echo -e "  gsettings set org.gnome.desktop.interface gtk-theme '$THEME_NAME'"
    echo -e "  o"
    echo -e "  gsettings set org.gnome.desktop.interface gtk-theme '${THEME_NAME}-dark'"
}

# Parsear argumentos
if [ $# -eq 0 ]; then
    # Sin argumentos, compilar todo por defecto
    COMPILE_LIGHT=false
    COMPILE_DARK=false
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--light)
            COMPILE_LIGHT=true
            shift
            ;;
        -d|--dark)
            COMPILE_DARK=true
            shift
            ;;
        -a|--all)
            COMPILE_LIGHT=false
            COMPILE_DARK=false
            shift
            ;;
        -i|--install)
            INSTALL=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        --base16)
            BASE16_SCHEME="$2"
            shift 2
            ;;
        --list-schemes)
            LIST_SCHEMES=true
            shift
            ;;
        --name)
            CUSTOM_NAME="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Opción desconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Listar esquemas si se solicitó
if [ "$LIST_SCHEMES" = true ]; then
    list_base16_schemes
    exit 0
fi

# Ejecutar limpieza si se solicitó
if [ "$CLEAN" = true ]; then
    clean_build
    exit 0
fi

# Verificar dependencias
check_dependencies

# Generar SCSS base16 si se especificó un esquema
if [ -n "$BASE16_SCHEME" ]; then
    generate_base16_scss "$BASE16_SCHEME"
fi

# Aplicar nombre personalizado si se especificó
if [ -n "$CUSTOM_NAME" ]; then
    THEME_NAME="$CUSTOM_NAME"
    echo -e "${BLUE}Usando nombre personalizado: $THEME_NAME${NC}"
elif [ -z "$BASE16_SCHEME" ]; then
    # Solo usar nombre por defecto si no hay base16 ni custom name
    THEME_NAME="adw-gtk3"
fi

# Crear directorio de build
mkdir -p "$BUILD_DIR"

# Compilar temas según las opciones
if [ "$COMPILE_LIGHT" = true ]; then
    compile_light_theme
elif [ "$COMPILE_DARK" = true ]; then
    compile_dark_theme
else
    # Compilar ambos por defecto
    compile_light_theme
    compile_dark_theme
fi

# Instalar si se solicitó
if [ "$INSTALL" = true ]; then
    install_themes
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Compilación completada exitosamente  ${NC}"
echo -e "${GREEN}========================================${NC}\n"

if [ "$INSTALL" = false ]; then
    echo -e "${YELLOW}Los temas compilados están en: $BUILD_DIR${NC}"
    echo -e "${YELLOW}Para instalar, ejecuta: $0 --install${NC}\n"
fi
