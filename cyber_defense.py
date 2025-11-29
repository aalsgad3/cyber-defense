import sys
import subprocess
import psutil
import time
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QTextEdit, QMessageBox
)
from PyQt5.QtGui import QFont, QColor, QPalette


class CyberDefense(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cyberpunk Defense Monitor")
        self.resize(950, 600)

        # Cyberpunk Theme
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(10, 10, 15))
        palette.setColor(QPalette.WindowText, QColor(0, 255, 170))
        self.setPalette(palette)

        title = QLabel("⚡ CYBER DEFENSE SYSTEM — REAL‑TIME MONITOR ⚡")
        title.setFont(QFont("Consolas", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.alertBox = QTextEdit()
        self.alertBox.setReadOnly(True)
        self.alertBox.setStyleSheet(
            "color:#00ffaa; background-color:#111319; border:1px solid #00ffaa;"
        )

        # Bottom panels
        self.portsBox = QTextEdit()
        self.connectionsBox = QTextEdit()
        self.processBox = QTextEdit()

        for box in (self.portsBox, self.connectionsBox, self.processBox):
            box.setReadOnly(True)
            box.setStyleSheet(
                "color:#00ffcc; background-color:#0d0f13; border:1px solid #00ffaa;"
            )

        bottom = QHBoxLayout()
        bottom.addWidget(self.portsBox)
        bottom.addWidget(self.connectionsBox)
        bottom.addWidget(self.processBox)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(QLabel("🔔 Alerts:"))
        layout.addWidget(self.alertBox)
        layout.addLayout(bottom)
        self.setLayout(layout)

        # Baselines for comparison
        self.old_ports = set()
        self.old_connections = set()
        self.old_processes = set(p.name() for p in psutil.process_iter())

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_checks)
        self.timer.start(5000)  # every 5 seconds

    # -------------------------------------------------------

    def add_alert(self, msg):
        timestamp = time.strftime("[%H:%M:%S]")
        full = f"{timestamp} {msg}"
        self.alertBox.append(full)

        popup = QMessageBox()
        popup.setWindowTitle("Cyber Defense Alert")
        popup.setText(full)
        popup.exec_()

    # -------------------------------------------------------

    def get_ports(self):
        ports = set()
        for conn in psutil.net_connections():
            if conn.laddr:
                ports.add(conn.laddr.port)
        return ports

    # -------------------------------------------------------

    def get_connections(self):
        try:
            result = subprocess.check_output("netstat -ano", shell=True).decode(errors="ignore")
            return set(result.splitlines())
        except:
            return set()

    # -------------------------------------------------------

    def get_processes(self):
        return set(p.name() for p in psutil.process_iter())

    # -------------------------------------------------------

    def run_checks(self):
        # Check ports
        ports = self.get_ports()
        self.portsBox.setText("\n".join(str(p) for p in sorted(ports)))

        new_ports = ports - self.old_ports
        if new_ports:
            self.add_alert(f"📌 منفذ جديد مفتوح: {list(new_ports)}")

        self.old_ports = ports

        # Check connections
        connections = self.get_connections()
        self.connectionsBox.setText("\n".join(list(connections)[:50]))

        new_conns = connections - self.old_connections
        if new_conns:
            self.add_alert(f"🌐 اتصال خارجي جديد مريب")

        self.old_connections = connections

        # Check processes
        procs = self.get_processes()
        self.processBox.setText("\n".join(sorted(procs)))

        new_procs = procs - self.old_processes
        if new_procs:
            self.add_alert(f"⚠ برنامج جديد بدأ التشغيل: {list(new_procs)}")

        self.old_processes = procs


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CyberDefense()
    window.show()
    sys.exit(app.exec_())
