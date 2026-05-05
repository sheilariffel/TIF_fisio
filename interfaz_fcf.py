import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import csv
from datetime import datetime

class FCFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medición FCF - Interfaz")
        self.root.geometry("450x550")
        
        self.serial_conn = None
        self.freq = 50  # El método inicia en 50 Hz
        self.archivo_guardado = "resultados_fcf.csv"

        # --- SECCIÓN 1: CONEXIÓN ---
        frame_conn = ttk.LabelFrame(root, text="Conexión (COM PORT / Baud Rate 9600)")
        frame_conn.pack(pady=10, padx=10, fill="x")
        
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        self.port_cb = ttk.Combobox(frame_conn, values=puertos, state="readonly")
        self.port_cb.pack(side=tk.LEFT, padx=5, pady=5)
        if puertos: 
            self.port_cb.current(0)
            
        self.btn_connect = ttk.Button(frame_conn, text="Conectar", command=self.conectar)
        self.btn_connect.pack(side=tk.LEFT, padx=5, pady=5)

        # --- SECCIÓN 2: CONTROL DEL ESTÍMULO ---
        frame_led = ttk.LabelFrame(root, text="Estímulo (LED)")
        frame_led.pack(pady=10, padx=10, fill="x")
        
        ttk.Button(frame_led, text="Encender", command=self.encender).pack(side=tk.LEFT, padx=20, pady=5)
        ttk.Button(frame_led, text="Apagar", command=self.apagar).pack(side=tk.RIGHT, padx=20, pady=5)

        # --- SECCIÓN 3: FRECUENCIA ---
        frame_freq = ttk.LabelFrame(root, text="Frecuencia (Hz)")
        frame_freq.pack(pady=10, padx=10, fill="x")
        
        self.lbl_freq = ttk.Label(frame_freq, text=str(self.freq), font=("Arial", 36, "bold"))
        self.lbl_freq.pack(pady=10)
        
        ttk.Button(frame_freq, text="- 1 Hz (Disminuir)", command=self.bajar_freq).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(frame_freq, text="+ 1 Hz (Aumentar)", command=self.subir_freq).pack(side=tk.RIGHT, padx=10, pady=5)
        ttk.Button(frame_freq, text="Reset a 50 Hz", command=self.resetear_50).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(frame_freq, text="Reset a 5 Hz", command=self.resetear_5).pack(side=tk.RIGHT, padx=10, pady=10)

        # --- SECCIÓN 4: REGISTRO DE DATOS ---
        frame_reg = ttk.LabelFrame(root, text="Registro de Datos")
        frame_reg.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(frame_reg, text="ID del registro:").pack(pady=5)
        self.entry_id = ttk.Entry(frame_reg)
        self.entry_id.pack(pady=5)
        
        ttk.Button(frame_reg, text="Seleccionar Archivo...", command=self.seleccionar_archivo).pack(pady=5)
        ttk.Button(frame_reg, text="REGISTRAR", command=self.registrar_datos).pack(pady=10)

    # --- FUNCIONES ---
    def conectar(self):
        puerto = self.port_cb.get()
        if puerto:
            try:
                self.serial_conn = serial.Serial(puerto, 9600, timeout=1)
                messagebox.showinfo("Conectado", f"Conexión exitosa al puerto {puerto}")
                self.enviar_frecuencia()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo conectar: {e}")

    def encender(self):
        if self.serial_conn: self.serial_conn.write(b"ON\n")
            
    def apagar(self):
        if self.serial_conn: self.serial_conn.write(b"OFF\n")

    def bajar_freq(self):
        if self.freq > 1:
            self.freq -= 1
            self.actualizar_pantalla()

    def subir_freq(self):
        self.freq += 1
        self.actualizar_pantalla()

    def resetear_50(self):
        self.freq = 50
        self.actualizar_pantalla()

    def resetear_5(self):
        self.freq = 5
        self.actualizar_pantalla()

    def actualizar_pantalla(self):
        self.lbl_freq.config(text=str(self.freq))
        self.enviar_frecuencia()

    def enviar_frecuencia(self):
        if self.serial_conn:
            comando = f"FREQ:{self.freq}\n"
            self.serial_conn.write(comando.encode())

    def seleccionar_archivo(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivo CSV", "*.csv")])
        if archivo:
            self.archivo_guardado = archivo
            messagebox.showinfo("Archivo", f"Los datos se guardarán en:\n{self.archivo_guardado}")

    def registrar_datos(self):
        id_registro = self.entry_id.get()
        if not id_registro:
            messagebox.showwarning("Falta ID", "Por favor ingresa un ID de registro válido.")
            return
            
        try:
            with open(self.archivo_guardado, mode="a", newline="") as file:
                writer = csv.writer(file)
                file.seek(0, 2)
                if file.tell() == 0:
                    writer.writerow(["Fecha", "Hora", "ID_Registro", "FCF_Hz"])
                
                ahora = datetime.now()
                writer.writerow([ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S"), id_registro, self.freq])
                
            messagebox.showinfo("Éxito", f"Datos guardados: ID {id_registro} con FCF de {self.freq} Hz")
            self.entry_id.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FCFApp(root)
    root.mainloop()
