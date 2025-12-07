# Theme Manager GUI

Aplicación gráfica para gestionar, compilar y personalizar temas GTK.

## Características

- **Gestión de Temas**: Lista, aplica y elimina temas instalados
- **Generador Base16**: Crea temas desde esquemas de colores base16 con previsualización
- **Compilador**: Compila temas personalizados con opciones flexibles

## Requisitos

```bash
# Debian/Ubuntu
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 python3-yaml

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita python3-pyyaml

# Arch
sudo pacman -S python-gobject gtk4 libadwaita python-yaml
```

## Uso

### Ejecutar directamente

```bash
./gui/theme-manager.py
```

### Instalar lanzador

```bash
# Copiar archivo desktop
cp gui/theme-manager.desktop ~/.local/share/applications/

# Actualizar base de datos de aplicaciones
update-desktop-database ~/.local/share/applications/
```

Luego busca "Theme Manager" en tu menú de aplicaciones.

## Vistas

### 1. Temas

- Lista todos los temas instalados en `~/.local/share/themes/`
- Muestra el tema actualmente aplicado
- Permite aplicar cualquier tema con un clic
- Opción para eliminar temas

### 2. Base16

- Lista todos los esquemas base16 disponibles
- Muestra previsualización de la paleta de colores
- Permite generar e instalar temas base16
- Campo para personalizar el nombre del tema

### 3. Compilar

- Compila el tema adw-gtk3 base
- Opciones: claro, oscuro o ambos
- Campo para nombre personalizado
- Instalación automática opcional
- Barra de progreso durante compilación

## Capturas de Pantalla

La aplicación usa Libadwaita para una apariencia moderna y consistente con GNOME.

## Desarrollo

La aplicación está escrita en Python usando GTK4 y Libadwaita:

- `theme-manager.py` - Aplicación principal
- Integración con `build-theme.sh`
- Integración con `base16-generator.py`
