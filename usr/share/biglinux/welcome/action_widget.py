import gi

gi.require_version("Gtk", "4.0")
import gettext
import locale
import os
import shlex
import subprocess

from gi.repository import Gdk, GdkPixbuf, GLib, Gtk

# Set up gettext for application localization.
DOMAIN = "biglinux-welcome"
LOCALE_DIR = "/usr/share/locale"
locale.setlocale(locale.LC_ALL, "")
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

APP_PATH = None


class ActionWidget(Gtk.Box):
    """
    A custom widget that can be either a clickable button with an icon and label,
    or a static image with a label.
    """

    def __init__(self, label, icon_name, action_type, command, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6, **kwargs)

        self.action_type = action_type
        self.command = command

        if self.action_type == "image":
            self.build_image_widget(label, icon_name)
        else:
            self.build_button_widget(label, icon_name)

    def build_image_widget(self, label, icon_name):
        """Builds a non-clickable image widget."""
        # Icon/Image - Use GdkPixbuf for sharp rendering
        image_path = os.path.join(APP_PATH, "image", icon_name)
        
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_path, 64, 64)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            image.set_pixel_size(64)
        except GLib.Error as e:
            print(f"Error loading image {image_path}: {e}. Using fallback.")
            # Fallback
            fallback_path = os.path.join(APP_PATH, "image", "main", "image-missing-symbolic.svg")
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(fallback_path, 64, 64)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                image.set_pixel_size(64)
            except GLib.Error:
                image = Gtk.Image.new_from_icon_name("image-missing")
                image.set_pixel_size(64)
                
        image.set_halign(Gtk.Align.CENTER)
        self.append(image)

        # Label
        label_widget = Gtk.Label(label=label)
        label_widget.set_wrap(True)
        self.append(label_widget)

    def build_button_widget(self, label, icon_name):
        """Builds a clickable button widget that will be packed into the parent Box."""
        button = Gtk.Button()
        button.set_has_frame(False)
        button.add_css_class("flat")
        button.connect("clicked", self._on_clicked)
        button.set_tooltip_text(label)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        button.set_child(content_box)

        # Try to load from file - check both direct path and nested folder paths
        # Use GdkPixbuf to render SVG at exact size for sharpness (same strategy as browser_widget)
        icon_path = os.path.join(APP_PATH, "image", icon_name)
        icon_size = 64  # Match browser page icon size
        
        if os.path.exists(icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, icon_size, icon_size)
                icon = Gtk.Image.new_from_pixbuf(pixbuf)
                icon.set_pixel_size(icon_size)
            except GLib.Error as e:
                print(f"Error loading icon {icon_path}: {e}. Using fallback.")
                # Fallback to missing icon image
                fallback_path = os.path.join(APP_PATH, "image", "main", "image-missing-symbolic.svg")
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(fallback_path, 64, 64)
                    icon = Gtk.Image.new_from_pixbuf(pixbuf)
                    icon.set_pixel_size(64)
                except GLib.Error:
                    # Ultimate fallback
                    icon = Gtk.Image.new_from_icon_name("image-missing")
                    icon.set_pixel_size(64)
        else:
            # Fallback to missing icon image
            fallback_path = os.path.join(APP_PATH, "image", "main", "image-missing-symbolic.svg")
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(fallback_path, 64, 64)
                icon = Gtk.Image.new_from_pixbuf(pixbuf)
                icon.set_pixel_size(64)
            except GLib.Error:
                icon = Gtk.Image.new_from_icon_name("image-missing")
                icon.set_pixel_size(64)
            print(f"Warning: Icon not found at {icon_path}, using fallback")

        content_box.append(icon)

        # Label
        label_widget = Gtk.Label(label=label)
        label_widget.set_wrap(True)
        content_box.append(label_widget)

        self.append(button)

    def _on_clicked(self, widget):
        """Handles the click event and performs the defined action."""
        print(f"Action triggered: type='{self.action_type}', command='{self.command}'")
        try:
            if self.action_type == "script":
                script_path = os.path.join(APP_PATH, self.command)
                command_parts = shlex.split(script_path)
                subprocess.Popen(command_parts)
            elif self.action_type == "app":
                command_parts = shlex.split(self.command)
                subprocess.Popen(command_parts)
            elif self.action_type == "url":
                Gtk.show_uri(None, self.command, Gdk.CURRENT_TIME)
        except Exception as e:
            print(f"Failed to execute command '{self.command}': {e}")
