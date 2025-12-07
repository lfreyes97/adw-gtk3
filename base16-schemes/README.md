# Base16 Schemes for adw-gtk3

This directory contains base16 color schemes in YAML format that can be used to generate custom GTK themes.

## Format

Each scheme file should follow the base16 YAML format:

```yaml
scheme: "Scheme Name"
author: "Author Name"
base00: "RRGGBB"  # Hex color without #
base01: "RRGGBB"
# ... base02 through base0F
```

## Available Schemes

- **gruvbox-dark.yaml** - Gruvbox Dark color scheme
- **nord.yaml** - Nord color scheme
- **catppuccin-mocha.yaml** - Catppuccin Mocha color scheme

## Usage

Use these schemes with the build script:

```bash
./build-theme.sh --base16 gruvbox-dark --all --install
```

## Adding Custom Schemes

1. Create a new `.yaml` file in this directory
2. Follow the base16 format shown above
3. Use the scheme with `--base16 <scheme-name>`

## Base16 Color Mapping

| Base | Purpose | GTK Usage |
|------|---------|-----------|
| base00 | Default Background | Dark theme background |
| base01 | Lighter Background | Surfaces, cards |
| base02 | Selection Background | Selected items |
| base03 | Comments, Secondary | Borders, separators |
| base04 | Dark Foreground | Secondary text |
| base05 | Default Foreground | Primary text |
| base06 | Light Foreground | Highlighted text |
| base07 | Light Background | Light theme background |
| base08 | Red | Errors, destructive actions |
| base09 | Orange | Warnings |
| base0A | Yellow | Caution, highlights |
| base0B | Green | Success states |
| base0C | Cyan | Info, links |
| base0D | Blue | Accent color, primary actions |
| base0E | Purple | Special highlights |
| base0F | Brown | Alternative accents |

## Resources

- [Base16 Project](https://github.com/chriskempson/base16)
- [Base16 Gallery](http://chriskempson.com/projects/base16/)
- [Base16 Builder](https://github.com/base16-project/base16)
