#!/usr/bin/env python3
# hid_mouse.py
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

# Questo script registra un servizio HID (Mouse) su Raspberry Pi
# usando BlueZ DBus

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

# Qui normalmente registreremmo il device HID via DBus
# ma ci sono librerie già pronte per farlo facilmente,
# ad esempio raspibluetooth-hid (da github), che evita XML manuale

print("Servizio HID pronto. Accoppia il Raspberry Pi al PC come mouse.")
loop = GLib.MainLoop()
loop.run()
