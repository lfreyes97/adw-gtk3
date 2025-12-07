# Script de Compilación de Temas adw-gtk3

## Descripción

Script bash para compilar temas personalizados de adw-gtk3. Permite compilar temas claros, oscuros o ambos, con opciones para instalación local y limpieza de archivos compilados.

## Uso

```bash
./build-theme.sh [opciones]
```

### Opciones Disponibles

| Opción | Descripción |
|--------|-------------|
| `-l, --light` | Compilar solo tema claro |
| `-d, --dark` | Compilar solo tema oscuro |
| `-a, --all` | Compilar ambos temas (por defecto) |
| `-i, --install` | Instalar en `~/.local/share/themes/` |
| `-c, --clean` | Limpiar archivos compilados |
| `-h, --help` | Mostrar ayuda |

**Opciones Base16:**

| Opción | Descripción |
|--------|-------------|
| `--base16 <scheme>` | Usar esquema de colores base16 |
| `--list-schemes` | Listar esquemas base16 disponibles |

**Opciones de Personalización:**

| Opción | Descripción |
|--------|-------------|
| `--name <nombre>` | Nombre personalizado para el tema |

### Ejemplos de Uso

**Compilación básica:**
```bash
# Compilar ambos temas e instalar
./build-theme.sh --all --install

# Compilar solo tema claro
./build-theme.sh --light

# Compilar solo tema oscuro
./build-theme.sh --dark

# Compilar ambos temas sin instalar
./build-theme.sh --all

# Limpiar archivos compilados
./build-theme.sh --clean
```

**Temas Base16:**
```bash
# Listar esquemas base16 disponibles
./build-theme.sh --list-schemes

# Compilar con esquema base16
./build-theme.sh --base16 gruvbox-dark --all --install

# Compilar base16 con nombre personalizado
./build-theme.sh --base16 nord --name my-nord-theme --install
```

**Nombres personalizados:**
```bash
# Tema con nombre personalizado
./build-theme.sh --name my-custom-theme --all --install

# Compilar tema claro con nombre personalizado
./build-theme.sh --light --name my-light-theme --install
```

## Dependencias

- **sass** (Dart Sass) - Requerido para compilar archivos SCSS a CSS

### Instalación de Dependencias

**Debian/Ubuntu:**
```bash
sudo apt install dart-sass
```

**Fedora:**
```bash
sudo dnf install dart-sass
```

**Arch Linux:**
```bash
sudo pacman -S dart-sass
```

**NPM (cualquier sistema):**
```bash
npm install -g sass
```

## Estructura de Compilación

El script realiza las siguientes acciones:

1. **Verificación de dependencias**: Comprueba que `sass` esté instalado
2. **Compilación de SASS**: Convierte archivos `.scss` a `.css`
   - GTK3: `gtk.css` y `gtk-dark.css`
   - GTK4: `libadwaita-tweaks.css`
3. **Copia de assets**: Copia iconos y recursos necesarios
4. **Copia de archivos estáticos**: Copia archivos CSS de GTK4
5. **Generación de metadatos**: Crea `index.theme` para cada tema
6. **Instalación** (opcional): Copia temas a `~/.local/share/themes/`

## Directorio de Salida

Los temas compilados se generan en el directorio `build/`:

```
build/
├── adw-gtk3/              # Tema claro
│   ├── gtk-3.0/
│   │   ├── gtk.css
│   │   ├── gtk-dark.css
│   │   ├── assets/
│   │   └── thumbnail.png
│   ├── gtk-4.0/
│   │   ├── gtk.css
│   │   ├── gtk-dark.css
│   │   ├── libadwaita.css
│   │   ├── libadwaita-tweaks.css
│   │   └── assets/
│   └── index.theme
└── adw-gtk3-dark/         # Tema oscuro
    ├── gtk-3.0/
    ├── gtk-4.0/
    └── index.theme
```

## Activar el Tema

Después de instalar, puedes activar el tema con:

**Tema claro:**
```bash
gsettings set org.gnome.desktop.interface gtk-theme 'adw-gtk3'
gsettings set org.gnome.desktop.interface color-scheme 'default'
```

**Tema oscuro:**
```bash
gsettings set org.gnome.desktop.interface gtk-theme 'adw-gtk3-dark'
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
```

**O usando GNOME Tweaks:**
1. Abre `gnome-tweaks`
2. Ve a *Apariencia > Aplicaciones Heredadas*
3. Selecciona `adw-gtk3` o `adw-gtk3-dark`

## Notas

- El script usa colores en la terminal para mejor legibilidad
- Los archivos compilados se generan en `build/` y no afectan los archivos fuente
- La opción `--clean` elimina completamente el directorio `build/`
- Si no se especifica ninguna opción, se compilan ambos temas por defecto
