# Guia de Prueba - Speech to Text y Text to Speech

## Configuracion Inicial

### 1. Habilitar APIs en Google Cloud

Antes de probar, debes habilitar las APIs en Google Cloud Console:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona el proyecto `zampa-8795f`
3. En el menu lateral, ve a **APIs & Services > Library**
4. Busca y habilita:
   - **Cloud Speech-to-Text API**
   - **Cloud Text-to-Speech API**

### 2. Activar Entorno Virtual

```bash
cd D:\Speech-to-Text
.\venv\Scripts\activate
```

---

## Prueba 1: Texto a Voz (Synthesize)

### Generar audio MP3 en español

```bash
python speech_converter.py synthesize "Hola, bienvenido al convertidor de voz. Esta es una prueba." --output audio_files\saludo.mp3
```

**Resultado esperado:** Se crea el archivo `audio_files\saludo.mp3`

### Generar audio en inglés con voz femenina

```bash
python speech_converter.py synthesize "Hello, welcome to the voice converter. This is a test." --language en --gender female --output audio_files\hello_female.mp3
```

### Generar audio en inglés con voz masculina

```bash
python speech_converter.py synthesize "Hello, welcome to the voice converter. This is a test." --language en --gender male --output audio_files\hello_male.mp3
```

### Generar archivo WAV

```bash
python speech_converter.py synthesize "Esta es una prueba en formato WAV." --output audio_files\prueba.wav
```

---

## Prueba 2: Audio a Texto (Transcribe)

> **Nota:** Necesitas un archivo de audio para esta prueba. Puedes usar los archivos generados en la Prueba 1.

### Transcribir archivo MP3

```bash
python speech_converter.py transcribe audio_files\saludo.mp3
```

**Resultado esperado:** Imprime en pantalla el texto transcrito

### Transcribir y guardar en archivo

```bash
python speech_converter.py transcribe audio_files\saludo.mp3 --output audio_files\transcripcion.txt
```

### Transcribir archivo en inglés

```bash
python speech_converter.py transcribe audio_files\hello_female.mp3 --language en
```

---

## Prueba 3: Listar Idiomas

```bash
python speech_converter.py languages
```

**Resultado esperado:**
```
Idiomas soportados:
  es: es-ES
  en: en-US
  pt: pt-BR
  fr: fr-FR
  de: de-DE
  it: it-IT
  ja: ja-JP
  ko: ko-KR
  zh: zh-CN
```

---

## Prueba Completa (Flujo Completo)

```bash
# Paso 1: Generar audio de prueba
python speech_converter.py synthesize "Esta es una prueba del sistema de conversion de voz. Puede convertir texto a voz y voz a texto." --output audio_files\prueba_completa.mp3

# Paso 2: Transcribir el audio generado
python speech_converter.py transcribe audio_files\prueba_completa.mp3

# Paso 3: Verificar que el texto coincida
```

---

## Solucion de Problemas

### Error: "No se encontro el archivo"

- Verifica que el archivo de audio existe en la ruta especificada
- Usa rutas absolutas si es necesario: `python speech_converter.py transcribe D:\Speech-to-Text\audio_files\archivo.mp3`

### Error: "Formato no soportado"

- Formatos validos: `.wav`, `.mp3`, `.flac`, `.ogg`
- Si tienes un archivo en otro formato, conviertelo primero a uno de estos

### Error de autenticacion / permisos

1. Verifica que el archivo `zampa-8795f-61aef27cf55a.json` esta en la carpeta raiz
2. Verifica que las APIs estan habilitadas en Google Cloud Console
3. Verifica que la cuenta de servicio tiene permisos de Editor o Owner

### Error: "python no se reconoce"

- Cierra y vuelve a abrir la terminal despues de instalar Python
- O ejecuta: `$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`

---

## Estructura del Proyecto

```
D:\Speech-to-Text\
├── venv\                          # Entorno virtual de Python
├── zampa-8795f-61aef27cf55a.json  # Credenciales Service Account
├── requirements.txt               # Dependencias
├── speech_converter.py            # Codigo principal
├── README.md                      # Documentacion
└── audio_files\                   # Carpeta para archivos de audio
    ├── saludo.mp3                 # (generado por la prueba)
    ├── hello_female.mp3           # (generado por la prueba)
    ├── hello_male.mp3             # (generado por la prueba)
    └── prueba.wav                 # (generado por la prueba)
```

---

## Comandos de Referencia

| Comando | Descripcion |
|---------|-------------|
| `python speech_converter.py transcribe <archivo>` | Transcribir audio a texto |
| `python speech_converter.py transcribe <archivo> --long` | Para audio mayor a 60 segundos |
| `python speech_converter.py synthesize "<texto>"` | Generar audio MP3 |
| `python speech_converter.py synthesize "<texto>" --output <archivo>` | Generar audio con nombre personalizado |
| `python speech_converter.py synthesize "<texto>" --language en` | Generar audio en ingles |
| `python speech_converter.py synthesize "<texto>" --gender female` | Generar audio con voz femenina |
| `python speech_converter.py languages` | Listar idiomas soportados |
