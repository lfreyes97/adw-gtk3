#!/usr/bin/env python3
"""
Base16 Theme Generator for adw-gtk3
Generates SCSS color overrides from base16 YAML schemes
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Optional


class Base16Generator:
    """Generates GTK theme SCSS from base16 color schemes"""
    
    def __init__(self, scheme_path: Path):
        self.scheme_path = scheme_path
        self.scheme_data = self._load_scheme()
        
    def _load_scheme(self) -> Dict:
        """Load and validate base16 YAML scheme"""
        try:
            with open(self.scheme_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Validate required fields
            required_bases = [f'base{i:02X}' for i in range(16)]
            for base in required_bases:
                if base not in data:
                    raise ValueError(f"Missing required color: {base}")
            
            return data
        except Exception as e:
            print(f"Error loading scheme: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _get_luminance(self, hex_color: str) -> float:
        """Calculate relative luminance of a color"""
        r, g, b = self._hex_to_rgb(hex_color)
        # Convert to 0-1 range
        r, g, b = r/255, g/255, b/255
        # Apply gamma correction
        r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
        g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
        b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
        # Calculate luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def _is_dark_theme(self) -> bool:
        """Determine if theme is dark based on base00 luminance"""
        bg_luminance = self._get_luminance(self.scheme_data['base00'])
        return bg_luminance < 0.5
    
    def _lighten(self, hex_color: str, amount: float) -> str:
        """Lighten a color by a percentage"""
        r, g, b = self._hex_to_rgb(hex_color)
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken(self, hex_color: str, amount: float) -> str:
        """Darken a color by a percentage"""
        r, g, b = self._hex_to_rgb(hex_color)
        r = max(0, int(r * (1 - amount)))
        g = max(0, int(g * (1 - amount)))
        b = max(0, int(b * (1 - amount)))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _mix_colors(self, color1: str, color2: str, ratio: float) -> str:
        """Mix two colors with given ratio (0-1, where 0 is all color1)"""
        r1, g1, b1 = self._hex_to_rgb(color1)
        r2, g2, b2 = self._hex_to_rgb(color2)
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def generate_scss(self, variant: str = 'auto') -> str:
        """Generate SCSS color overrides"""
        
        # Determine variant
        if variant == 'auto':
            is_dark = self._is_dark_theme()
            variant = 'dark' if is_dark else 'light'
        else:
            is_dark = variant == 'dark'
        
        scheme_name = self.scheme_data.get('scheme', 'Base16')
        author = self.scheme_data.get('author', 'Unknown')
        
        # Get base16 colors
        base = {f'{i:02X}': self.scheme_data[f'base{i:02X}'] for i in range(16)}
        
        # Generate derived colors based on variant
        if is_dark:
            window_bg = f"#{base['00']}"
            window_fg = f"#{base['05']}"
            view_bg = self._lighten(base['00'], 0.05)
            view_fg = f"#{base['05']}"
            headerbar_bg = self._lighten(base['00'], 0.1)
            sidebar_bg = headerbar_bg
            card_bg = self._lighten(base['00'], 0.08)
            dialog_bg = self._lighten(base['00'], 0.12)
            popover_bg = dialog_bg
        else:
            window_bg = self._darken(base['07'], 0.02)
            window_fg = f"#{base['02']}"
            view_bg = f"#{base['07']}"
            view_fg = f"#{base['02']}"
            headerbar_bg = self._darken(base['07'], 0.08)
            sidebar_bg = headerbar_bg
            card_bg = f"#{base['07']}"
            dialog_bg = self._darken(base['07'], 0.02)
            popover_bg = f"#{base['07']}"
        
        # Generate SCSS
        scss = f"""// Base16 Theme: {scheme_name}
// Author: {author}
// Variant: {variant}
// Generated automatically by base16-generator.py

// Override palette colors with base16 scheme
$blue_1: #{self._lighten(base['0D'], 0.3)};
$blue_2: #{self._lighten(base['0D'], 0.15)};
$blue_3: #{base['0D']};
$blue_4: #{self._darken(base['0D'], 0.1)};
$blue_5: #{self._darken(base['0D'], 0.2)};

$green_1: #{self._lighten(base['0B'], 0.3)};
$green_2: #{self._lighten(base['0B'], 0.15)};
$green_3: #{base['0B']};
$green_4: #{self._darken(base['0B'], 0.1)};
$green_5: #{self._darken(base['0B'], 0.2)};

$yellow_1: #{self._lighten(base['0A'], 0.3)};
$yellow_2: #{self._lighten(base['0A'], 0.15)};
$yellow_3: #{base['0A']};
$yellow_4: #{self._darken(base['0A'], 0.1)};
$yellow_5: #{self._darken(base['0A'], 0.2)};

$orange_1: #{self._lighten(base['09'], 0.3)};
$orange_2: #{self._lighten(base['09'], 0.15)};
$orange_3: #{base['09']};
$orange_4: #{self._darken(base['09'], 0.1)};
$orange_5: #{self._darken(base['09'], 0.2)};

$red_1: #{self._lighten(base['08'], 0.3)};
$red_2: #{self._lighten(base['08'], 0.15)};
$red_3: #{base['08']};
$red_4: #{self._darken(base['08'], 0.1)};
$red_5: #{self._darken(base['08'], 0.2)};

$purple_1: #{self._lighten(base['0E'], 0.3)};
$purple_2: #{self._lighten(base['0E'], 0.15)};
$purple_3: #{base['0E']};
$purple_4: #{self._darken(base['0E'], 0.1)};
$purple_5: #{self._darken(base['0E'], 0.2)};

$brown_1: #{self._lighten(base['0F'], 0.3)};
$brown_2: #{self._lighten(base['0F'], 0.15)};
$brown_3: #{base['0F']};
$brown_4: #{self._darken(base['0F'], 0.1)};
$brown_5: #{self._darken(base['0F'], 0.2)};

$light_1: #{base['07']};
$light_2: #{self._darken(base['07'], 0.02)};
$light_3: #{self._darken(base['07'], 0.1)};
$light_4: #{self._darken(base['07'], 0.2)};
$light_5: #{self._darken(base['07'], 0.3)};

$dark_1: #{base['04']};
$dark_2: #{base['03']};
$dark_3: #{base['02']};
$dark_4: #{base['01']};
$dark_5: #{base['00']};

// Override default colors
@define-color accent_bg_color #{base['0D']};
@define-color accent_fg_color {"white" if is_dark else f"#{base['00']}"};

@define-color destructive_bg_color #{base['08']};
@define-color destructive_fg_color white;

@define-color success_bg_color #{base['0B']};
@define-color success_fg_color {"white" if is_dark else f"#{base['00']}"};

@define-color warning_bg_color #{base['09']};
@define-color warning_fg_color {"white" if is_dark else f"#{base['00']}"};

@define-color error_bg_color #{base['08']};
@define-color error_fg_color white;

@define-color window_bg_color {window_bg};
@define-color window_fg_color {window_fg};

@define-color view_bg_color {view_bg};
@define-color view_fg_color {view_fg};

@define-color headerbar_bg_color {headerbar_bg};
@define-color headerbar_fg_color {window_fg};

@define-color sidebar_bg_color {sidebar_bg};
@define-color sidebar_fg_color {window_fg};

@define-color card_bg_color {card_bg};
@define-color card_fg_color {view_fg};

@define-color dialog_bg_color {dialog_bg};
@define-color dialog_fg_color {window_fg};

@define-color popover_bg_color {popover_bg};
@define-color popover_fg_color {view_fg};
"""
        
        return scss
    
    def save_scss(self, output_path: Path, variant: str = 'auto'):
        """Generate and save SCSS file"""
        scss_content = self.generate_scss(variant)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(scss_content)
        
        print(f"Generated SCSS: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate GTK theme SCSS from base16 color schemes'
    )
    parser.add_argument(
        'scheme',
        type=Path,
        help='Path to base16 YAML scheme file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('src/sass/_base16-override.scss'),
        help='Output SCSS file path (default: src/sass/_base16-override.scss)'
    )
    parser.add_argument(
        '-v', '--variant',
        choices=['light', 'dark', 'auto'],
        default='auto',
        help='Theme variant (default: auto-detect from scheme)'
    )
    parser.add_argument(
        '--list-colors',
        action='store_true',
        help='List all colors in the scheme and exit'
    )
    
    args = parser.parse_args()
    
    if not args.scheme.exists():
        print(f"Error: Scheme file not found: {args.scheme}", file=sys.stderr)
        sys.exit(1)
    
    generator = Base16Generator(args.scheme)
    
    if args.list_colors:
        print(f"\nScheme: {generator.scheme_data.get('scheme', 'Unknown')}")
        print(f"Author: {generator.scheme_data.get('author', 'Unknown')}")
        print(f"Variant: {'dark' if generator._is_dark_theme() else 'light'}\n")
        print("Colors:")
        for i in range(16):
            base_name = f'base{i:02X}'
            color = generator.scheme_data[base_name]
            print(f"  {base_name}: #{color}")
    else:
        generator.save_scss(args.output, args.variant)


if __name__ == '__main__':
    main()
