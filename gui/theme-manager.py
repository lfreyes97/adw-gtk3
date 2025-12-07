#!/usr/bin/env python3
"""
ADW GTK3 Theme Manager
A GUI application for managing, compiling, and customizing GTK themes
"""

import gi
import sys
import os
import subprocess
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib


class ThemeManagerWindow(Adw.ApplicationWindow):
    """Main application window"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.set_title("Theme Manager")
        self.set_default_size(800, 600)
        
        # Get project paths
        self.project_dir = Path(__file__).parent.parent
        self.themes_dir = Path.home() / ".local/share/themes"
        self.base16_dir = self.project_dir / "base16-schemes"
        self.build_script = self.project_dir / "build-theme.sh"
        
        # Create main layout
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header bar
        header = Adw.HeaderBar()
        
        # Main content
        self.navigation_view = Adw.NavigationView()
        
        # Create main page with view switcher
        main_page = self.create_main_page()
        self.navigation_view.add(main_page)
        
        # Toolbar view to combine header and content
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(self.navigation_view)
        
        self.set_content(toolbar_view)
    
    def create_main_page(self):
        """Create the main page with view switcher"""
        page = Adw.NavigationPage()
        page.set_title("Theme Manager")
        
        # View stack
        self.view_stack = Adw.ViewStack()
        
        # Add views
        self.themes_view = self.create_themes_view()
        self.view_stack.add_titled(self.themes_view, "themes", "Temas")
        
        self.base16_view = self.create_base16_view()
        self.view_stack.add_titled(self.base16_view, "base16", "Base16")
        
        self.compile_view = self.create_compile_view()
        self.view_stack.add_titled(self.compile_view, "compile", "Compilar")
        
        # View switcher bar
        view_switcher_bar = Adw.ViewSwitcherBar()
        view_switcher_bar.set_stack(self.view_stack)
        
        # View switcher title
        view_switcher_title = Adw.ViewSwitcherTitle()
        view_switcher_title.set_stack(self.view_stack)
        view_switcher_title.set_title("Theme Manager")
        
        # Layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(view_switcher_title)
        box.append(self.view_stack)
        box.append(view_switcher_bar)
        
        page.set_child(box)
        return page
    
    def create_themes_view(self):
        """Create the installed themes view"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        # Preferences page
        prefs_page = Adw.PreferencesPage()
        
        # Installed themes group
        themes_group = Adw.PreferencesGroup()
        themes_group.set_title("Temas Instalados")
        themes_group.set_description("Temas disponibles en tu sistema")
        
        # Get current theme
        settings = Gio.Settings.new("org.gnome.desktop.interface")
        current_theme = settings.get_string("gtk-theme")
        
        # List installed themes
        if self.themes_dir.exists():
            for theme_path in sorted(self.themes_dir.iterdir()):
                if theme_path.is_dir() and (theme_path / "gtk-3.0").exists():
                    row = Adw.ActionRow()
                    row.set_title(theme_path.name)
                    
                    # Check if it's the current theme
                    if theme_path.name == current_theme:
                        row.set_subtitle("✓ Tema activo")
                        
                        # Add checkmark icon
                        icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                        row.add_suffix(icon)
                    
                    # Apply button
                    apply_btn = Gtk.Button()
                    apply_btn.set_label("Aplicar")
                    apply_btn.set_valign(Gtk.Align.CENTER)
                    apply_btn.add_css_class("suggested-action")
                    apply_btn.connect("clicked", self.on_apply_theme, theme_path.name)
                    row.add_suffix(apply_btn)
                    
                    # Delete button
                    delete_btn = Gtk.Button()
                    delete_btn.set_icon_name("user-trash-symbolic")
                    delete_btn.set_valign(Gtk.Align.CENTER)
                    delete_btn.add_css_class("destructive-action")
                    delete_btn.connect("clicked", self.on_delete_theme, theme_path.name)
                    row.add_suffix(delete_btn)
                    
                    themes_group.add(row)
        
        # Refresh button
        refresh_row = Adw.ActionRow()
        refresh_row.set_title("Actualizar lista")
        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_valign(Gtk.Align.CENTER)
        refresh_btn.connect("clicked", self.on_refresh_themes)
        refresh_row.add_suffix(refresh_btn)
        themes_group.add(refresh_row)
        
        prefs_page.add(themes_group)
        scrolled.set_child(prefs_page)
        
        return scrolled
    
    def create_base16_view(self):
        """Create the base16 schemes view"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        prefs_page = Adw.PreferencesPage()
        
        # Base16 schemes group
        schemes_group = Adw.PreferencesGroup()
        schemes_group.set_title("Esquemas Base16")
        schemes_group.set_description("Genera temas desde esquemas de colores base16")
        
        # List base16 schemes
        if self.base16_dir.exists():
            for scheme_file in sorted(self.base16_dir.glob("*.yaml")):
                scheme_name = scheme_file.stem
                
                # Read scheme info
                try:
                    import yaml
                    with open(scheme_file) as f:
                        scheme_data = yaml.safe_load(f)
                    
                    row = Adw.ExpanderRow()
                    row.set_title(scheme_data.get('scheme', scheme_name))
                    row.set_subtitle(f"Por {scheme_data.get('author', 'Desconocido')}")
                    
                    # Color preview box
                    colors_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                    colors_box.set_margin_top(8)
                    colors_box.set_margin_bottom(8)
                    colors_box.set_margin_start(12)
                    colors_box.set_margin_end(12)
                    
                    # Show first 8 colors
                    for i in range(8):
                        color_key = f'base{i:02X}'
                        if color_key in scheme_data:
                            color_box = Gtk.DrawingArea()
                            color_box.set_size_request(30, 30)
                            color_box.set_content_width(30)
                            color_box.set_content_height(30)
                            
                            color_hex = f"#{scheme_data[color_key]}"
                            color_box.set_draw_func(self.draw_color_box, color_hex)
                            
                            colors_box.append(color_box)
                    
                    row.add_row(colors_box)
                    
                    # Name entry
                    name_row = Adw.EntryRow()
                    name_row.set_title("Nombre del tema")
                    name_row.set_text(f"adw-gtk3-{scheme_name}")
                    row.add_row(name_row)
                    
                    # Generate button
                    gen_row = Adw.ActionRow()
                    gen_btn = Gtk.Button()
                    gen_btn.set_label("Generar e Instalar")
                    gen_btn.set_valign(Gtk.Align.CENTER)
                    gen_btn.add_css_class("suggested-action")
                    gen_btn.connect("clicked", self.on_generate_base16, scheme_name, name_row)
                    gen_row.add_suffix(gen_btn)
                    row.add_row(gen_row)
                    
                    schemes_group.add(row)
                    
                except Exception as e:
                    print(f"Error loading scheme {scheme_file}: {e}")
        
        prefs_page.add(schemes_group)
        scrolled.set_child(prefs_page)
        
        return scrolled
    
    def create_compile_view(self):
        """Create the compile theme view"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        prefs_page = Adw.PreferencesPage()
        
        # Compile options group
        compile_group = Adw.PreferencesGroup()
        compile_group.set_title("Compilar Tema")
        compile_group.set_description("Compila el tema adw-gtk3 con opciones personalizadas")
        
        # Theme name
        self.name_entry = Adw.EntryRow()
        self.name_entry.set_title("Nombre del tema")
        self.name_entry.set_text("adw-gtk3")
        compile_group.add(self.name_entry)
        
        # Variant selection
        variant_row = Adw.ActionRow()
        variant_row.set_title("Variante")
        
        self.variant_combo = Gtk.DropDown.new_from_strings(["Ambos", "Claro", "Oscuro"])
        self.variant_combo.set_valign(Gtk.Align.CENTER)
        variant_row.add_suffix(self.variant_combo)
        compile_group.add(variant_row)
        
        # Install option
        self.install_switch = Adw.SwitchRow()
        self.install_switch.set_title("Instalar automáticamente")
        self.install_switch.set_active(True)
        compile_group.add(self.install_switch)
        
        # Compile button
        compile_row = Adw.ActionRow()
        compile_btn = Gtk.Button()
        compile_btn.set_label("Compilar Tema")
        compile_btn.set_valign(Gtk.Align.CENTER)
        compile_btn.add_css_class("suggested-action")
        compile_btn.connect("clicked", self.on_compile_theme)
        compile_row.add_suffix(compile_btn)
        compile_group.add(compile_row)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_margin_top(12)
        self.progress_bar.set_margin_bottom(12)
        self.progress_bar.set_margin_start(12)
        self.progress_bar.set_margin_end(12)
        self.progress_bar.set_visible(False)
        compile_group.add(self.progress_bar)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_margin_top(6)
        self.status_label.set_margin_bottom(12)
        self.status_label.set_visible(False)
        compile_group.add(self.status_label)
        
        prefs_page.add(compile_group)
        scrolled.set_child(prefs_page)
        
        return scrolled
    
    def draw_color_box(self, area, cr, width, height, color_hex):
        """Draw a colored box"""
        # Parse color
        try:
            from gi.repository import Gdk
            rgba = Gdk.RGBA()
            rgba.parse(color_hex)
            cr.set_source_rgb(rgba.red, rgba.green, rgba.blue)
            cr.rectangle(0, 0, width, height)
            cr.fill()
        except:
            pass
    
    def on_apply_theme(self, button, theme_name):
        """Apply a theme"""
        try:
            settings = Gio.Settings.new("org.gnome.desktop.interface")
            settings.set_string("gtk-theme", theme_name)
            
            # Show toast
            toast = Adw.Toast.new(f"Tema '{theme_name}' aplicado")
            toast.set_timeout(2)
            
            # Refresh view
            self.on_refresh_themes(None)
            
        except Exception as e:
            self.show_error(f"Error al aplicar tema: {e}")
    
    def on_delete_theme(self, button, theme_name):
        """Delete a theme"""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("¿Eliminar tema?")
        dialog.set_body(f"¿Estás seguro de que quieres eliminar '{theme_name}'?")
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("delete", "Eliminar")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self.on_delete_confirmed, theme_name)
        dialog.present()
    
    def on_delete_confirmed(self, dialog, response, theme_name):
        """Handle delete confirmation"""
        if response == "delete":
            try:
                import shutil
                theme_path = self.themes_dir / theme_name
                if theme_path.exists():
                    shutil.rmtree(theme_path)
                    self.on_refresh_themes(None)
            except Exception as e:
                self.show_error(f"Error al eliminar tema: {e}")
    
    def on_refresh_themes(self, button):
        """Refresh the themes list"""
        # Recreate themes view
        old_view = self.themes_view
        self.themes_view = self.create_themes_view()
        
        # Replace in stack
        self.view_stack.remove(old_view)
        self.view_stack.add_titled_with_icon(
            self.themes_view, "themes", "Temas", "preferences-desktop-theme-symbolic"
        )
    
    def on_generate_base16(self, button, scheme_name, name_entry):
        """Generate theme from base16 scheme"""
        theme_name = name_entry.get_text().strip()
        if not theme_name:
            self.show_error("Por favor ingresa un nombre para el tema")
            return
        
        self.run_build_script([
            "--base16", scheme_name,
            "--name", theme_name,
            "--all", "--install"
        ])
    
    def on_compile_theme(self, button):
        """Compile theme"""
        theme_name = self.name_entry.get_text().strip()
        if not theme_name:
            self.show_error("Por favor ingresa un nombre para el tema")
            return
        
        # Build command
        args = ["--name", theme_name]
        
        # Variant
        variant = self.variant_combo.get_selected()
        if variant == 1:  # Claro
            args.append("--light")
        elif variant == 2:  # Oscuro
            args.append("--dark")
        else:  # Ambos
            args.append("--all")
        
        # Install
        if self.install_switch.get_active():
            args.append("--install")
        
        self.run_build_script(args)
    
    def run_build_script(self, args):
        """Run the build script with given arguments"""
        self.progress_bar.set_visible(True)
        self.progress_bar.pulse()
        self.status_label.set_text("Compilando...")
        self.status_label.set_visible(True)
        
        # Run in thread
        def run():
            try:
                cmd = [str(self.build_script)] + args
                result = subprocess.run(
                    cmd,
                    cwd=str(self.project_dir),
                    capture_output=True,
                    text=True
                )
                
                GLib.idle_add(self.on_build_complete, result.returncode == 0, result.stdout, result.stderr)
            except Exception as e:
                GLib.idle_add(self.on_build_complete, False, "", str(e))
        
        import threading
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
    
    def on_build_complete(self, success, stdout, stderr):
        """Handle build completion"""
        self.progress_bar.set_visible(False)
        
        if success:
            self.status_label.set_text("✓ Compilación exitosa")
            self.on_refresh_themes(None)
        else:
            self.status_label.set_text("✗ Error en compilación")
            self.show_error(f"Error:\n{stderr}")
        
        GLib.timeout_add_seconds(3, lambda: self.status_label.set_visible(False))
        return False
    
    def show_error(self, message):
        """Show error dialog"""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Error")
        dialog.set_body(message)
        dialog.add_response("ok", "OK")
        dialog.present()


class ThemeManagerApp(Adw.Application):
    """Main application"""
    
    def __init__(self):
        super().__init__(
            application_id="com.github.adw_gtk3.ThemeManager",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
    
    def do_activate(self):
        """Activate the application"""
        win = self.props.active_window
        if not win:
            win = ThemeManagerWindow(application=self)
        win.present()


def main():
    """Main entry point"""
    app = ThemeManagerApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
