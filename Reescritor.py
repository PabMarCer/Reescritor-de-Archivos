import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import random

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")  # Puedes usar "dark-blue", "dark", o un tema personalizado

class RetroGlitchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Reescritor de Archivos")
        self.geometry("620x580")
        self.infiles = []
        self.outdir = ""

        # Título principal
        ctk.CTkLabel(self, text="Reescritor de Archivos", font=("Courier New", 22, "bold")).pack(pady=10)

        # Selección de archivos
        ctk.CTkButton(self, text="[1] Seleccionar archivos", command=self.select_files, font=("Courier New", 14)).pack()
        self.file_label = ctk.CTkLabel(self, text="Ningún archivo cargado", font=("Courier New", 12))
        self.file_label.pack(pady=5)

        # Selección de carpeta de salida
        ctk.CTkButton(self, text="[2] Carpeta de salida", command=self.select_output_dir, font=("Courier New", 14)).pack()
        self.outdir_label = ctk.CTkLabel(self, text="Directorio: ./", font=("Courier New", 12))
        self.outdir_label.pack(pady=5)

        # Iteraciones por archivo (movido aquí)
        ctk.CTkLabel(self, text="[3] Iteraciones por archivo:", font=("Courier New", 12)).pack(pady=2)
        self.iter_entry = ctk.CTkEntry(self, font=("Courier New", 12))
        self.iter_entry.insert(0, "3")
        self.iter_entry.pack()

        # Saltar cabecera (movido más arriba)
        self.skip_header = ctk.CTkCheckBox(self, text="[4] Saltar primeros 100 bytes", font=("Courier New", 12))
        self.skip_header.pack(pady=5)

        # Modo glitch
        ctk.CTkLabel(self, text="[5] Modo de glitch:", font=("Courier New", 12)).pack(pady=2)
        self.mode_option = ctk.CTkOptionMenu(self, values=[
            "change", "insert", "repeat", "zero", "remove", "replace", "reverse", "move"
        ], font=("Courier New", 12))
        self.mode_option.set("change")
        self.mode_option.pack()

        # Cantidad de glitches
        ctk.CTkLabel(self, text="[6] Glitches por iteración:", font=("Courier New", 12)).pack(pady=2)
        self.count_entry = ctk.CTkEntry(self, font=("Courier New", 12))
        self.count_entry.insert(0, "20")
        self.count_entry.pack()

        # Tamaño del glitch
        ctk.CTkLabel(self, text="[7] Bytes por glitch:", font=("Courier New", 12)).pack(pady=2)
        self.size_entry = ctk.CTkEntry(self, font=("Courier New", 12))
        self.size_entry.insert(0, "10")
        self.size_entry.pack()

        # Botón ejecutar
        ctk.CTkButton(self, text=">> GLITCHEAR ARCHIVOS", command=self.run_batch_glitch,
                      font=("Courier New", 14, "bold"), fg_color="white", text_color="black").pack(pady=15)

    def select_files(self):
        files = filedialog.askopenfilenames()
        if files:
            self.infiles = list(files)
            self.file_label.configure(text=f"{len(self.infiles)} archivo(s) seleccionado(s)")

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.outdir = path
            self.outdir_label.configure(text=f"Directorio: {path}")

    def glitch_file(self, filepath, mode, count, size, skip_header, iter_num):
        with open(filepath, "rb") as f:
            original_data = bytearray(f.read())

        start = 100 if skip_header else 0
        data = bytearray(original_data)

        for _ in range(count):
            if len(data) <= size + start:
                continue
            pos = random.randint(start, len(data) - size - 1)
            chunk = data[pos:pos+size]

            if mode == "change":
                data[pos:pos+size] = [random.randint(0, 255) for _ in range(size)]
            elif mode == "zero":
                data[pos:pos+size] = [0] * size
            elif mode == "insert":
                data[pos:pos] = [random.randint(0, 255) for _ in range(size)]
            elif mode == "remove":
                del data[pos:pos+size]
            elif mode == "repeat":
                repeat = chunk * (size // len(chunk) + 1)
                data[pos:pos+size] = repeat[:size]
            elif mode == "replace":
                b1, b2 = random.randint(0, 255), random.randint(0, 255)
                data[pos:pos+size] = [b2 if b == b1 else b for b in chunk]
            elif mode == "reverse":
                data[pos:pos+size] = chunk[::-1]
            elif mode == "move":
                del data[pos:pos+size]
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
            messagebox.showerror("ERROR", "Selecciona al menos un archivo.")
            return
        try:
            count = int(self.count_entry.get())
            size = int(self.size_entry.get())
            iterations = int(self.iter_entry.get())
        except ValueError:
            messagebox.showerror("ERROR", "Campos numéricos inválidos.")
            return

        mode = self.mode_option.get()
        skip_header = self.skip_header.get()
        results = []

        for file in self.infiles:
            for i in range(1, iterations + 1):
                path = self.glitch_file(file, mode, count, size, skip_header, i)
                results.append(path)

        messagebox.showinfo("ÉXITO", f"{len(results)} archivos generados:\n\n" + "\n".join(results))

if __name__ == "__main__":
    app = RetroGlitchApp()
    app.mainloop()
