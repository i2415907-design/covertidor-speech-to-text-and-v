# Speech-to-Text y Text-to-Speech con Google Cloud

Proyecto para convertir audio a texto y texto a voz usando las APIs de Google Cloud.

## Requisitos previos

1. Python 3.10 o superior
2. Cuenta de Google Cloud habilitada
3. APIs habilitadas en Google Cloud Console:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Verificar que el archivo `zampa-8795f-61aef27cf55a.json` está en la carpeta raíz.

## Uso

### Transcribir audio a texto

```bash
# Transcribir archivo MP3 (español por defecto)
python speech_converter.py transcribe audio.mp3

# Transcribir archivo WAV en inglés
python speech_converter.py transcribe audio.wav --language en

# Transcribir audio largo (>60 segundos)
python speech_converter.py transcribe audio_largo.mp3 --long

# Guardar transcripción en archivo
python speech_converter.py transcribe audio.mp3 --output transcripcion.txt
```

### Sintetizar texto a voz

```bash
# Generar audio MP3 (español, voz neutra)
python speech_converter.py synthesize "Hola mundo"

# Generar audio en inglés con voz femenina
python speech_converter.py synthesize "Hello world" --language en --gender female

# Especificar archivo de salida
python speech_converter.py synthesize "Hola mundo" --output hola.mp3

# Generar archivo WAV
python speech_converter.py synthesize "Hola mundo" --output hola.wav
```

### Listar idiomas soportados

```bash
python speech_converter.py languages
```

## Idiomas soportados

| Código | Idioma |
|--------|--------|
| es | Español (es-ES) |
| en | Inglés (en-US) |
| pt | Portugués (pt-BR) |
| fr | Francés (fr-FR) |
| de | Alemán (de-DE) |
| it | Italiano (it-IT) |
| ja | Japonés (ja-JP) |
| ko | Coreano (ko-KR) |
| zh | Chino (zh-CN) |

## Formatos de audio soportados

- WAV
- MP3
- FLAC
- OGG
- MP4
- WebM

## Notas importantes

- Para audio largo (mayor a 60 segundos), usar el flag `--long`
- Las credenciales del Service Account deben estar en `zampa-8795f-61aef27cf55a.json`
- Se requiere conexión a internet para usar las APIs de Google Cloud
