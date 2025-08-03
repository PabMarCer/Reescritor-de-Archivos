import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QWidget, QFileDialog, QVBoxLayout,
    QComboBox, QCheckBox, QLineEdit, QMessageBox, QHBoxLayout,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase, QColor
from PyQt5.QtCore import Qt, QTimer

class MatrixTitle(QLabel):
    def __init__(self, text, font):
        super().__init__(text)
        self.original_text = text
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        self.characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*"

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_text)

        self.update_count = 0
        self.color_change_interval = 5

        self.current_text = list(self.original_text)
        self.indices_to_change = []

    def enterEvent(self, event):
        self.current_text = list(self.original_text)
        self.indices_to_change = list(range(len(self.original_text)))
        random.shuffle(self.indices_to_change)
        self.update_count = 0
        self.timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.timer.stop()
        self.setText(self.original_text)
        self.setStyleSheet("color: #FFFFFF;")
        super().leaveEvent(event)

    def update_text(self):
        self.update_count += 1

        if self.indices_to_change:
            index = self.indices_to_change.pop()
            self.current_text[index] = random.choice(self.characters)
            self.setText(''.join(self.current_text))
        else:
            self.setText(''.join(random.choice(self.characters) for _ in self.original_text))

        if self.update_count % self.color_change_interval == 0:
            r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            self.setStyleSheet(f"color: {QColor(r, g, b).name()};")

class RetroGlitchApp(QLabel):
    def __init__(self):
        super().__init__()

        self.pixmap = QPixmap("fondo_custom.png")
        self.setPixmap(self.pixmap)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.pixmap.width(), self.pixmap.height())

        self.close_button = QPushButton("X", self)
        self.close_button.resize(25, 25)
        self.close_button.move(self.pixmap.width() - self.close_button.width() - 35, 10)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                border: 1px solid black;
                font: bold 14px 'MS Sans Serif', Geneva, sans-serif;
                color: white;
            }
            QPushButton:pressed {
                background-color: darkred;
            }
        """)
        self.close_button.clicked.connect(self.close)

        self.drag_pos = None
        self.infiles = []
        self.outdir = ""

        preferred_fonts = ["Perfect DOS VGA 437", "Px437 IBM VGA8", "Lucida Console", "Consolas"]
        font_family = next((f for f in preferred_fonts if f in QFontDatabase().families()), "Courier New")

        font_title = QFont(font_family, 40, QFont.Bold)
        font_label = QFont(font_family, 13)
        font_button = QFont(font_family, 14, QFont.Bold)

        self.widget_container = QWidget(self)
        self.widget_container.setAttribute(Qt.WA_TranslucentBackground)
        self.widget_container.setGeometry(20, 50, self.pixmap.width() - 40, self.pixmap.height() - 60)

        layout = QVBoxLayout(self.widget_container)
        layout.setContentsMargins(0, 30, 0, 0)

        def centered(widget, fraction=1/3):
            widget.setFixedWidth(int(self.width() * fraction))
            row = QHBoxLayout()
            row.addStretch()
            row.addWidget(widget)
            row.addStretch()
            return row

        self.title = MatrixTitle("Reescritor de Archivos", font_title)
        self.title.setStyleSheet("color: #FFFFFF;")
        layout.addLayout(centered(self.title, 0.8))

        btn_select_files = QPushButton("Seleccionar archivos")
        btn_select_files.setFont(font_button)
        btn_select_files.clicked.connect(self.select_files)
        btn_select_files.setStyleSheet("background-color: black; color: #FFFFFF; border: 2px solid #FFFFFF; padding: 6px;")
        layout.addLayout(centered(btn_select_files))

        self.file_label = QLabel("Ningún archivo cargado")
        self.file_label.setFont(font_label)
        self.file_label.setStyleSheet("color: #FFFFFF;")
        self.file_label.setIndent(133)
        layout.addLayout(centered(self.file_label, 0.6))

        btn_select_outdir = QPushButton("Carpeta de salida")
        btn_select_outdir.setFont(font_button)
        btn_select_outdir.clicked.connect(self.select_output_dir)
        btn_select_outdir.setStyleSheet("background-color: black; color: #FFFFFF; border: 2px solid #FFFFFF; padding: 6px;")
        layout.addLayout(centered(btn_select_outdir))

        self.outdir_label = QLabel("Directorio: ./")
        self.outdir_label.setFont(font_label)
        self.outdir_label.setStyleSheet("color: #FFFFFF;")
        self.outdir_label.setIndent(133)
        layout.addLayout(centered(self.outdir_label, 0.6))

        iter_label = QLabel("Iteraciones por archivo:")
        iter_label.setFont(font_label)
        iter_label.setStyleSheet("color: #FFFFFF;")
        iter_label.setIndent(133)
        layout.addLayout(centered(iter_label, 0.6))

        self.iter_entry = QLineEdit("3")
        self.iter_entry.setFont(font_label)
        self.iter_entry.setStyleSheet("background-color: black; color: #FFFFFF; border: 1px solid #FFFFFF;")
        layout.addLayout(centered(self.iter_entry))

        mode_label = QLabel("Modo de glitch:")
        mode_label.setFont(font_label)
        mode_label.setStyleSheet("color: #FFFFFF;")
        mode_label.setIndent(133)
        layout.addLayout(centered(mode_label, 0.6))

        self.mode_option = QComboBox()
        self.mode_option.setFont(font_label)
        self.mode_option.addItems(["cambiar", "insertar", "repetir", "cero", "eliminar", "recolocar", "revertir", "mover"])
        self.mode_option.setCurrentText("cambiar")
        self.mode_option.setStyleSheet("background-color: black; color: #FFFFFF; border: 1px solid #FFFFFF;")
        layout.addLayout(centered(self.mode_option))

        glitches_label = QLabel("Glitches por iteración:")
        glitches_label.setFont(font_label)
        glitches_label.setStyleSheet("color: #FFFFFF;")
        glitches_label.setIndent(133)
        layout.addLayout(centered(glitches_label, 0.6))

        self.count_entry = QLineEdit("20")
        self.count_entry.setFont(font_label)
        self.count_entry.setStyleSheet("background-color: black; color: #FFFFFF; border: 1px solid #FFFFFF;")
        layout.addLayout(centered(self.count_entry))

        bytes_label = QLabel("Bytes por glitch:")
        bytes_label.setFont(font_label)
        bytes_label.setStyleSheet("color: #FFFFFF;")
        bytes_label.setIndent(133)
        layout.addLayout(centered(bytes_label, 0.6))

        self.size_entry = QLineEdit("10")
        self.size_entry.setFont(font_label)
        self.size_entry.setStyleSheet("background-color: black; color: #FFFFFF; border: 1px solid #FFFFFF;")
        layout.addLayout(centered(self.size_entry))

        # ← MOVIDO: Saltar primeros 100 bytes
        self.skip_header = QCheckBox("Saltar primeros 100 bytes")
        self.skip_header.setFont(font_label)
        self.skip_header.setStyleSheet("color: #FFFFFF;")
        layout.addLayout(centered(self.skip_header))

        spacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)

        glitch_btn = QPushButton(">> GLITCHEAR ARCHIVOS <<")
        glitch_btn.setFont(font_button)
        glitch_btn.clicked.connect(self.run_batch_glitch)
        glitch_btn.setStyleSheet("background-color: black; color: #FFFFFF; border: 2px solid #FFFFFF; padding: 6px;")
        layout.addLayout(centered(glitch_btn))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos")
        if files:
            self.infiles = files
            self.file_label.setText(f"{len(self.infiles)} archivo(s) seleccionado(s)")

    def select_output_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if path:
            self.outdir = path
            self.outdir_label.setText(f"Directorio: {path}")

    def glitch_file(self, filepath, mode, count, size, skip_header, iter_num):
        with open(filepath, "rb") as f:
            original_data = bytearray(f.read())

        start = 100 if skip_header else 0
        data = bytearray(original_data)

        for _ in range(count):
            if len(data) <= size + start:
                continue
            pos = random.randint(start, len(data) - size - 1)
            chunk = data[pos:pos + size]

            if mode == "cambiar":
                data[pos:pos + size] = [random.randint(0, 255) for _ in range(size)]
            elif mode == "cero":
                data[pos:pos + size] = [0] * size
            elif mode == "insertar":
                data[pos:pos] = [random.randint(0, 255) for _ in range(size)]
            elif mode == "eliminar":
                del data[pos:pos + size]
            elif mode == "repetir":
                repeat = chunk * (size // len(chunk) + 1)
                data[pos:pos + size] = repeat[:size]
            elif mode == "recolocar":
                b1, b2 = random.randint(0, 255), random.randint(0, 255)
                data[pos:pos + size] = [b2 if b == b1 else b for b in chunk]
            elif mode == "revertir":
                data[pos:pos + size] = chunk[::-1]
            elif mode == "mover":
                del data[pos:pos + size]
                new_pos = random.randint(start, len(data))
                data[new_pos:new_pos] = chunk

        base, ext = os.path.splitext(os.path.basename(filepath))
        output_name = f"{base}_glitched_{mode}_{iter_num}{ext}"
        output_path = os.path.join(self.outdir if self.outdir else ".", output_name)

        with open(output_path, "wb") as f:
            f.write(data)

        return output_path

    def run_batch_glitch(self):
        if not self.infiles:
            QMessageBox.critical(self, "ERROR", "Selecciona al menos un archivo.")
            return
        try:
            count = int(self.count_entry.text())
            size = int(self.size_entry.text())
            iterations = int(self.iter_entry.text())
        except ValueError:
            QMessageBox.critical(self, "ERROR", "Campos numéricos inválidos.")
            return

        mode = self.mode_option.currentText()
        skip_header = self.skip_header.isChecked()
        results = []

        for file in self.infiles:
            for i in range(1, iterations + 1):
                path = self.glitch_file(file, mode, count, size, skip_header, i)
                results.append(path)

        QMessageBox.information(self, "ÉXITO",
                                f"{len(results)} archivos generados:\n\n" + "\n".join(results))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RetroGlitchApp()
    window.show()
    sys.exit(app.exec_())
