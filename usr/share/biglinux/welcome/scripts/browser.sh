#!/bin/bash

# # check current status
# checkBrowserState() {
#   if [[ "$1" == "brave" ]];then
#     if [[ -e "/usr/bin/brave" ]];then
#       echo "true"
#       desktopFile="brave-browser.desktop"
#     elif [[ -e "/var/lib/flatpak/app/com.brave.Browser" ]];then
#       echo "true"
#       desktopFile="com.brave.Browser.desktop"
#     else
#       echo "false"
#     fi
#   elif [[ "$1" == "chromium" ]];then
#     if [[ -e "/usr/bin/chromium" ]];then
#       echo "true"
#       desktopFile="chromium.desktop"
#     elif [[ -e "/var/lib/flatpak/app/org.chromium.Chromium" ]];then
#       echo "true"
#       desktopFile="org.chromium.Chromium.desktop"
#     else
#       echo "false"
#     fi
#   elif [[ "$1" == "google-chrome" ]];then
#     if [[ -e "/usr/bin/google-chrome-stable" ]];then
#       echo "true"
#       desktopFile="google-chrome.desktop"
#     elif [[ -e "/var/lib/flatpak/app/com.google.Chrome" ]];then
#       echo "true"
#       desktopFile="com.google.Chrome.desktop"
#     else
#       echo "false"
#     fi
#   elif [[ "$1" == "falkon" ]];then
#     if [[ -e "/usr/bin/falkon" ]];then
#       echo "true"
#       desktopFile="org.kde.falkon.desktop"
#     elif [[ -e "/var/lib/flatpak/app/org.kde.falkon" ]];then
#       echo "true"
#       desktopFile="org.kde.falkon.desktop"
#     else
#       echo "false"
#     fi
#   elif [[ "$1" == "firefox" ]];then
#     if [[ -e "/usr/bin/firefox" ]];then
#       echo "true"
#       desktopFile="firefox.desktop"
#     elif [[ -e "/var/lib/flatpak/app/org.mozilla.firefox" ]];then
#       echo "true"
#       desktopFile="org.mozilla.firefox.desktop"
#     else
#       echo "false"
#     fi
#   elif [[ "$1" == "librewolf" ]];then
#     if [[ -e "/usr/bin/librewolf" ]];then
#       echo "true"
#       desktopFile="librewolf.desktop"
#     elif [[ -e "/var/lib/flatpak/app/io.gitlab.librewolf-community" ]];then
#       echo "true"
#       desktopFile="io.gitlab.librewolf-community.desktop"
#     else
#       echo "false"
#     fi
#   elif [[ "$1" == "opera" ]];then
#     if [[ -e "/usr/bin/opera" ]];then
#       echo "true"
#       desktopFile="opera.desktop"
#     elif [[ -e "/var/lib/flatpak/app/com.opera.Opera" ]];then
#       echo "true"
#       desktopFile="com.opera.Opera.desktop"
#     else
#       echo "false"
#     fi
#   elif [[ "$1" == "vivaldi" ]];then
#     if [[ -e "/usr/bin/vivaldi" ]];then
#       echo "true"
#       desktopFile="vivaldi-stable.desktop"
#     elif [[ -e "/var/lib/flatpak/app/com.vivaldi.Vivaldi" ]];then
#       echo "true"
#       desktopFile="com.vivaldi.Vivaldi.desktop"
#     else
#       echo "false"
#     fi
#   elif [[ "$1" == "edge" ]];then
#     if [[ -e "/usr/bin/microsoft-edge-stable" ]];then
#       echo "true"
#       desktopFile="microsoft-edge.desktop"
#     elif [[ -e "/var/lib/flatpak/app/com.microsoft.Edge" ]];then
#       echo "true"
#       desktopFile="com.microsoft.Edge.desktop"
#     else
#       echo "false"
#     fi
#   fi
# }

getDefaultBrowser() {
  xdg-settings get default-web-browser
#   xdg-mime query default x-scheme-handler/http
}

setDefaultBrowser() {
  xdg-mime default $1 x-scheme-handler/http
  xdg-mime default $1 x-scheme-handler/https
  xdg-settings set default-web-browser $1
}

# change the state
installBrowser() {
  # Get the directory where the script is located
  local script_dir
  script_dir="$(dirname "$(readlink -f "$0")")"
  pkexec "$script_dir/browserInstall.sh" "$1" "$USER" "$DISPLAY" "$XAUTHORITY" "$DBUS_SESSION_BUS_ADDRESS" "$LANG" "$LANGUAGE"
  exitCode=$?
  exit $exitCode
}

# Executes the function based on the parameter
case "$1" in
    # "check")
    #     checkBrowserState "$2"
    #     ;;
    "install")
        installBrowser "$2"
        ;;
    "getBrowser")
        getDefaultBrowser
        ;;
    "setBrowser")
        setDefaultBrowser "$2"
        ;;
    *)
        echo "Use: $0 {check|install} [true|false]"
        echo "  check          - Check current status"
        echo "  install        - install the specified browser"
        exit 1
        ;;
esac
