import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import numpy as np
import threading
import traceback

from pyrnnoise.rnnoise import create as rn_create
from pyrnnoise.rnnoise import process_mono_frame as rn_process

class DenoiserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mic Denoiser Pro (RNNoise)")
        self.root.geometry("450x420") # Ventana más alta para que quepa todo
        self.root.resizable(False, False)
        
        self.is_running = False
        self.rn_state = rn_create()
        
        self.in_level = 0
        self.out_level = 0
        
        self.devices = sd.query_devices()
        self.input_devices = [d['name'] for d in self.devices if d['max_input_channels'] > 0]
        self.output_devices = [d['name'] for d in self.devices if d['max_output_channels'] > 0]
        
        # --- INTERFAZ GRÁFICA ---
        # Fila de Entrada
        frame_in = tk.Frame(root)
        frame_in.pack(pady=(15, 0))
        tk.Label(frame_in, text="🎤 Entrada:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w")
        self.in_combo = ttk.Combobox(frame_in, values=self.input_devices, state="readonly", width=40)
        self.in_combo.grid(row=1, column=0, padx=5)
        if self.input_devices: self.in_combo.current(0)
        
        self.led_in = tk.Canvas(frame_in, width=20, height=20, highlightthickness=0)
        self.led_in_circle = self.led_in.create_oval(2, 2, 18, 18, fill="gray")
        self.led_in.grid(row=1, column=1)
            
        # Fila de Salida
        frame_out = tk.Frame(root)
        frame_out.pack(pady=(10, 5))
        tk.Label(frame_out, text="🔊 Salida:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w")
        self.out_combo = ttk.Combobox(frame_out, values=self.output_devices, state="readonly", width=40)
        self.out_combo.grid(row=1, column=0, padx=5)
        if self.output_devices: self.out_combo.current(0)
        
        self.led_out = tk.Canvas(frame_out, width=20, height=20, highlightthickness=0)
        self.led_out_circle = self.led_out.create_oval(2, 2, 18, 18, fill="gray")
        self.led_out.grid(row=1, column=1)

        # --- NUEVOS CONTROLES ---
        frame_controls = tk.Frame(root)
        frame_controls.pack(pady=10, fill="x", padx=30)

        # Control 1: Mezcla (Dry/Wet)
        tk.Label(frame_controls, text="🎛️ Intensidad del Filtro IA (%):", font=("Helvetica", 9)).pack(anchor="w")
        self.mix_slider = tk.Scale(frame_controls, from_=0, to=100, orient="horizontal", length=380)
        self.mix_slider.set(100) # 100% IA por defecto
        self.mix_slider.pack()

        # Control 2: Puerta de Ruido (VAD)
        tk.Label(frame_controls, text="🚪 Sensibilidad Puerta de Voz (%):", font=("Helvetica", 9)).pack(anchor="w", pady=(10,0))
        self.vad_slider = tk.Scale(frame_controls, from_=0, to=100, orient="horizontal", length=380)
        self.vad_slider.set(0) # 0% significa apagado (siempre abierto)
        self.vad_slider.pack()
        
        # Botón
        self.btn = tk.Button(root, text="Iniciar Filtro", command=self.toggle, 
                             bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
        self.btn.pack(pady=15)

        self.update_leds()
        
    def update_leds(self):
        umbral = 300 
        if self.is_running:
            color_in = "#00FF00" if self.in_level > umbral else "#003300"
            color_out = "#00FF00" if self.out_level > umbral else "#003300"
        else:
            color_in = "gray"
            color_out = "gray"
            
        self.led_in.itemconfig(self.led_in_circle, fill=color_in)
        self.led_out.itemconfig(self.led_out_circle, fill=color_out)
        
        self.in_level = 0
        self.out_level = 0
        self.root.after(50, self.update_leds)

    def toggle(self):
        if not self.is_running:
            self.is_running = True
            self.btn.config(text="Detener Filtro", bg="#f44336")
            threading.Thread(target=self.run_audio, daemon=True).start()
        else:
            self.is_running = False
            self.btn.config(text="Iniciar Filtro", bg="#4CAF50")

    def run_audio(self):
        in_name = self.in_combo.get()
        out_name = self.out_combo.get()
        
        in_id = next(i for i, d in enumerate(self.devices) if d['name'] == in_name and d['max_input_channels'] > 0)
        out_id = next(i for i, d in enumerate(self.devices) if d['name'] == out_name and d['max_output_channels'] > 0)

        CHUNK = 480  
        RATE = 48000
        stream_in = None
        stream_out = None

        try:
            stream_in = sd.InputStream(samplerate=RATE, blocksize=CHUNK,
                                       device=in_id, channels=1, dtype='int16')
            stream_out = sd.OutputStream(samplerate=RATE, blocksize=CHUNK,
                                         device=out_id, channels=1, dtype='int16')
            
            stream_in.start()
            stream_out.start()

            while self.is_running:
                in_data, overflowed = stream_in.read(CHUNK)
                audio_1d = in_data.flatten()
                self.in_level = np.max(np.abs(audio_1d))
                
                # Leemos los valores de la interfaz en tiempo real
                mix_percent = self.mix_slider.get() / 100.0
                vad_threshold = self.vad_slider.get() / 100.0
                
                # Procesamos con la IA
                denoised_frame, speech_prob = rn_process(self.rn_state, audio_1d)
                
                # --- NUESTRA PROPIA MATEMÁTICA ---
                # 1. Puerta de ruido
                if speech_prob < vad_threshold:
                    # Si la IA no cree que sea voz (probabilidad menor al slider), silenciamos
                    final_audio = np.zeros_like(audio_1d)
                else:
                    # 2. Mezcla Dry/Wet
                    # Multiplicamos el original y el limpio por sus porcentajes y los sumamos
                    final_audio = (audio_1d * (1.0 - mix_percent)) + (denoised_frame * mix_percent)
                
                # Formateamos y enviamos
                out_data = np.array(final_audio, dtype=np.int16).reshape(-1, 1)
                self.out_level = np.max(np.abs(out_data))
                stream_out.write(out_data)

        except Exception as e:
            print("\n🚨 ERROR 🚨\n")
            traceback.print_exc()
            
        finally:
            self.is_running = False
            self.btn.config(text="Iniciar Filtro", bg="#4CAF50")
            if stream_in is not None: stream_in.stop(); stream_in.close()
            if stream_out is not None: stream_out.stop(); stream_out.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = DenoiserApp(root)
    root.mainloop()
