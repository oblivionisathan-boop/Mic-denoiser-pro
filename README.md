# 🎙️ Mic Denoiser Pro (IA RNNoise)

¡Adiós al ruido de fondo! Este es un filtro de micrófono en tiempo real impulsado por Inteligencia Artificial (RNNoise) y escrito en Python. Elimina el ruido de teclados, ventiladores y estática, dejando pasar únicamente tu voz de forma clara y nítida.

Ideal para usar con Discord, OBS, Twitch o cualquier juego.

![Captura de pantalla de la interfaz del programa](URL_DE_TU_IMAGEN_AQUI)
*(Nota para ti: Aquí debes subir una foto de tu ventana de Python funcionando)*

---

## 🚀 Instalación desde Cero (Para principiantes)

Si nunca has programado o no tienes Python, no te preocupes. Sigue estos pasos exactos:

### 1. Instalar Python
1. Descarga Python desde su [página oficial (python.org)](https://www.python.org/downloads/).
2. Abre el instalador descargado.
3. **⚠️ PASO CRÍTICO:** En la primera pantalla que aparece, asegúrate de **MARCAR LA CASILLA** que dice **`Add python.exe to PATH`** en la parte inferior. Si no marcas esto, el programa no funcionará.
4. Haz clic en "Install Now" y espera a que termine.



### 2. Descargar este proyecto
1. Ve a la parte superior de esta página en GitHub.
2. Haz clic en el botón verde **`<> Code`** y selecciona **`Download ZIP`**.
3. Extrae esa carpeta en tu Escritorio o donde prefieras.

### 3. Instalar los "motores" del programa
Para que la Inteligencia Artificial y el audio funcionen, necesitamos instalar unas librerías gratuitas.
1. Abre la carpeta que acabas de extraer (donde está el archivo `denoiser.py`).
2. Haz clic en la barra de direcciones de la carpeta (arriba, donde dice la ruta), borra todo, escribe `cmd` y presiona **Enter**. Se abrirá una ventana negra (Terminal).
3. Escribe el siguiente comando y presiona Enter:
   ```cmd
   pip install -r requirements.txt
