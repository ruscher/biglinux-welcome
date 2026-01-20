import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
import locale
import gettext
import subprocess
import threading
import os
from gi.repository import Gtk, Adw, GLib

# Set up gettext for application localization.
DOMAIN = 'biglinux-welcome'
LOCALE_DIR = '/usr/share/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

from browser_widget import BrowserWidget

class BrowserPage(Adw.Bin):
    """A page to select, install, and set the default web browser."""
    def __init__(self, page_data, app_path, **kwargs):
        super().__init__(**kwargs)
        self.page_data = page_data
        self.app_path = app_path
        self.script_path = os.path.join(self.app_path, "scripts", "browser.sh")
        self.browser_widgets = []

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=11)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(36)
        main_box.set_margin_end(36)
        self.set_child(main_box)

        # Title and Subtitle
        title_label = Gtk.Label(halign=Gtk.Align.CENTER)
        title_label.set_markup(f"<span size='xx-large' weight='bold'>{_(page_data['title'])}</span>")
        main_box.append(title_label)

        subtitle_label = Gtk.Label(halign=Gtk.Align.CENTER, wrap=True)
        subtitle_label.set_markup(f"<span size='large'>{_(page_data['subtitle'])}</span>")
        main_box.append(subtitle_label)

        # Spinner for feedback
        self.spinner = Gtk.Spinner(spinning=False, halign=Gtk.Align.CENTER)
        main_box.append(self.spinner)

        # Action Buttons Grid
        self.flowbox = Gtk.FlowBox(valign=Gtk.Align.START, max_children_per_line=5)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_halign(Gtk.Align.CENTER)

        scrolled_window = Gtk.ScrolledWindow(vexpand=True)
        scrolled_window.set_child(self.flowbox)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.append(scrolled_window)

        for browser in page_data['actions']:
            widget = BrowserWidget(browser, self.app_path)
            widget.button.connect("clicked", self._on_browser_clicked, browser)
            self.browser_widgets.append(widget)
            self.flowbox.insert(widget, -1)

        # Initial state check, deferred to avoid blocking UI thread on startup
        GLib.idle_add(self.refresh_browser_states)

    def _run_script(self, args):
        """Helper to run the browser script and return its output."""
        try:
            cmd = [self.script_path] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error running script with args {args}: {e}")
            return None

    def _is_installed(self, package_name):
        """Check if a browser is installed via the script."""
        output = self._run_script(["check", package_name])
        return output == "true"

    def _get_default_browser(self, package_name):
        """Get the .desktop file of the current default browser via the script."""
        return self._run_script(["getBrowser", package_name])

    def refresh_browser_states(self):
        """Update all browser widgets to reflect the current system state."""
        self.flowbox.set_sensitive(False) # Disable during check
        default_browser_desktop = self._get_default_browser()

        for widget in self.browser_widgets:
            browser = widget.browser_data
            is_installed = self._is_installed(browser['package'])
            allowed_desktop_files = browser.get('desktop_file', [])

            # Verifica se é o padrão
            if isinstance(allowed_desktop_files, list):
                # Se for uma lista, verifica se o padrão do sistema está nela
                is_default = default_browser_desktop in allowed_desktop_files
            else:
                # Se for apenas uma string, faz a comparação direta como antes
                is_default = (allowed_desktop_files == default_browser_desktop)

            widget.set_installed(is_installed)
            widget.set_default(is_default)

        self.flowbox.set_sensitive(True) # Re-enable
        self.spinner.stop()
        return GLib.SOURCE_REMOVE # Important for idle_add

    def _on_browser_clicked(self, button, browser_data):
        """Handle click: install if needed, then set as default."""
        self.flowbox.set_sensitive(False)
        self.spinner.start()

        thread = threading.Thread(target=self._perform_browser_action, args=(browser_data,))
        thread.daemon = True
        thread.start()

    def _perform_browser_action(self, browser_data):
        """Worker thread function to perform installation and set default."""
        is_installed = self._is_installed(browser_data['package'])

        if not is_installed:
            # The script handles pkexec and user feedback, so we just run it.
            self._run_script(["install", browser_data['package']])
            # We can check exit code if needed, but for now we'll just refresh.

        # Set as default after installation or if it was already installed
        self._run_script(["setBrowser", browser_data['package']])

        # After the task is done, schedule a UI update on the main thread
        GLib.idle_add(self.refresh_browser_states)
