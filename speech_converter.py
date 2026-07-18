import os
import sys
import argparse
import tempfile
from pathlib import Path

from google.cloud import speech
from google.cloud import texttospeech

# Configurar credenciales: usa variable de entorno o busca el archivo local
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    CREDENTIALS_PATH = Path(__file__).parent / "zampa-8795f-61aef27cf55a.json"
    if CREDENTIALS_PATH.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDENTIALS_PATH)

# Mapeo de formatos de audio
AUDIO_FORMATS = {
    ".wav": {"encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16, "sample_rate": 16000},
    ".mp3": {"encoding": speech.RecognitionConfig.AudioEncoding.MP3, "sample_rate": 16000},
    ".flac": {"encoding": speech.RecognitionConfig.AudioEncoding.FLAC, "sample_rate": 16000},
    ".ogg": {"encoding": speech.RecognitionConfig.AudioEncoding.OGG_OPUS, "sample_rate": 16000},
    ".webm": {"encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS, "sample_rate": 16000},
}

# Idiomas soportados
SUPPORTED_LANGUAGES = {
    "es": "es-ES",
    "en": "en-US",
    "pt": "pt-BR",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "zh": "zh-CN",
}


def get_audio_sample_rate(audio_path: str) -> int:
    """
    Detectar la frecuencia de muestreo de un archivo de audio.
    
    Args:
        audio_path: Ruta al archivo de audio
    
    Returns:
        Frecuencia de muestreo en Hz
    """
    from pydub import AudioSegment
    
    audio = AudioSegment.from_file(audio_path)
    return audio.frame_rate


def transcribe_audio(audio_path: str, language: str = "es", sample_rate: int = None) -> str:
    """
    Transcribe un archivo de audio a texto usando Google Cloud Speech-to-Text.
    
    Args:
        audio_path: Ruta al archivo de audio
        language: Código del idioma (es, en, pt, fr, de, it, ja, ko, zh)
        sample_rate: Frecuencia de muestreo en Hz (opcional, se detecta automáticamente)
    
    Returns:
        Texto transcrito
    """
    audio_path = Path(audio_path)
    
    if not audio_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {audio_path}")
    
    ext = audio_path.suffix.lower()
    if ext not in AUDIO_FORMATS:
        raise ValueError(f"Formato no soportado: {ext}. Formatos válidos: {', '.join(AUDIO_FORMATS.keys())}")
    
    lang_code = SUPPORTED_LANGUAGES.get(language, language)
    
    # Detectar sample rate automáticamente si no se especifica
    if sample_rate is None:
        try:
            sample_rate = get_audio_sample_rate(str(audio_path))
        except Exception:
            sample_rate = AUDIO_FORMATS[ext]["sample_rate"]
    
    with open(audio_path, "rb") as audio_file:
        audio_content = audio_file.read()
    
    client = speech.SpeechClient()
    
    audio = speech.RecognitionAudio(content=audio_content)
    
    config = speech.RecognitionConfig(
        encoding=AUDIO_FORMATS[ext]["encoding"],
        sample_rate_hertz=sample_rate,
        language_code=lang_code,
        enable_automatic_punctuation=True,
        model="latest_long",
    )
    
    response = client.recognize(config=config, audio=audio)
    
    transcript_parts = []
    for result in response.results:
        if result.alternatives:
            transcript_parts.append(result.alternatives[0].transcript)
    
    return " ".join(transcript_parts)


def transcribe_long_audio(audio_path: str, language: str = "es", sample_rate: int = None) -> str:
    """
    Transcribe archivos de audio largos (mayores de 60 segundos).
    
    Args:
        audio_path: Ruta al archivo de audio
        language: Código del idioma
        sample_rate: Frecuencia de muestreo en Hz
    
    Returns:
        Texto transcrito
    """
    audio_path = Path(audio_path)
    
    if not audio_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {audio_path}")
    
    ext = audio_path.suffix.lower()
    if ext not in AUDIO_FORMATS:
        raise ValueError(f"Formato no soportado: {ext}")
    
    lang_code = SUPPORTED_LANGUAGES.get(language, language)
    
    with open(audio_path, "rb") as audio_file:
        audio_content = audio_file.read()
    
    client = speech.SpeechClient()
    
    audio = speech.RecognitionAudio(content=audio_content)
    
    config = speech.RecognitionConfig(
        encoding=AUDIO_FORMATS[ext]["encoding"],
        sample_rate_hertz=sample_rate or AUDIO_FORMATS[ext]["sample_rate"],
        language_code=lang_code,
        enable_automatic_punctuation=True,
        model="latest_long",
    )
    
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=300)
    
    transcript_parts = []
    for result in response.results:
        if result.alternatives:
            transcript_parts.append(result.alternatives[0].transcript)
    
    return " ".join(transcript_parts)


def synthesize_speech(
    text: str,
    output_path: str = "output.mp3",
    language: str = "es",
    voice_gender: str = "neutral",
) -> str:
    """
    Sintetizar texto a voz usando Google Cloud Text-to-Speech.
    
    Args:
        text: Texto a sintetizar
        output_path: Ruta del archivo de salida
        language: Código del idioma
        voice_gender: Género de la voz (male, female, neutral)
    
    Returns:
        Ruta del archivo de audio generado
    """
    if not text.strip():
        raise ValueError("El texto no puede estar vacío")
    
    lang_code = SUPPORTED_LANGUAGES.get(language, language)
    
    gender_map = {
        "male": texttospeech.SsmlVoiceGender.MALE,
        "female": texttospeech.SsmlVoiceGender.FEMALE,
        "neutral": texttospeech.SsmlVoiceGender.NEUTRAL,
    }
    ssml_gender = gender_map.get(voice_gender.lower(), texttospeech.SsmlVoiceGender.NEUTRAL)
    
    client = texttospeech.TextToSpeechClient()
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code=lang_code,
        ssml_gender=ssml_gender,
    )
    
    ext = Path(output_path).suffix.lower()
    if ext == ".wav":
        audio_encoding = texttospeech.AudioEncoding.LINEAR16
    elif ext == ".ogg":
        audio_encoding = texttospeech.AudioEncoding.OGG_OPUS
    else:
        audio_encoding = texttospeech.AudioEncoding.MP3
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=audio_encoding,
        sample_rate_hertz=24000,
    )
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convertidor de voz a texto y texto a voz usando Google Cloud",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python speech_converter.py transcribe audio.mp3
  python speech_converter.py transcribe audio.wav --language en
  python speech_converter.py synthesize "Hola mundo" --output hola.mp3
  python speech_converter.py synthesize "Hello world" --language en --gender female
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # Subparser para transcribir
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribir audio a texto")
    transcribe_parser.add_argument("audio", help="Ruta al archivo de audio")
    transcribe_parser.add_argument("--language", "-l", default="es", help="Código del idioma (default: es)")
    transcribe_parser.add_argument("--long", action="store_true", help="Usar para audio largo (>60s)")
    transcribe_parser.add_argument("--sample-rate", "-s", type=int, help="Frecuencia de muestreo en Hz")
    transcribe_parser.add_argument("--output", "-o", help="Guardar transcripción en archivo")
    
    # Subparser para sintetizar
    synthesize_parser = subparsers.add_parser("synthesize", help="Sintetizar texto a voz")
    synthesize_parser.add_argument("text", help="Texto a sintetizar")
    synthesize_parser.add_argument("--output", "-o", default="output.mp3", help="Archivo de salida (default: output.mp3)")
    synthesize_parser.add_argument("--language", "-l", default="es", help="Código del idioma (default: es)")
    synthesize_parser.add_argument("--gender", "-g", default="neutral", choices=["male", "female", "neutral"], help="Género de la voz")
    
    # Subparser para listar idiomas
    subparsers.add_parser("languages", help="Listar idiomas soportados")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "transcribe":
            if args.long:
                result = transcribe_long_audio(args.audio, args.language, args.sample_rate)
            else:
                result = transcribe_audio(args.audio, args.language, args.sample_rate)
            
            if args.output:
                Path(args.output).write_text(result, encoding="utf-8")
                print(f"Transcripción guardada en: {args.output}")
            else:
                print(result)
        
        elif args.command == "synthesize":
            result = synthesize_speech(args.text, args.output, args.language, args.gender)
            print(f"Audio generado en: {result}")
        
        elif args.command == "languages":
            print("Idiomas soportados:")
            for code, full_code in SUPPORTED_LANGUAGES.items():
                print(f"  {code}: {full_code}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
