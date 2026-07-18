import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';
import 'package:permission_handler/permission_handler.dart';

const String apiBaseUrl = 'https://covertidor-speech-to-text-and-v.vercel.app';

const Map<String, String> languages = {
  'es': 'Espanol',
  'en': 'English',
  'pt': 'Portugues',
  'fr': 'Francais',
  'de': 'Deutsch',
  'it': 'Italiano',
  'ja': 'Nihongo',
  'ko': 'Korean',
  'zh': 'Zhongwen',
};

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Speech Converter',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFFE94560),
          surface: const Color(0xFF1A1A2E),
        ),
        scaffoldBackgroundColor: const Color(0xFF1A1A2E),
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String _selectedLang = 'es';
  bool _isRecording = false;
  bool _isLoading = false;
  String _transcribedText = '';
  String _inputText = '';
  String? _audioPath;
  final AudioPlayer _audioPlayer = AudioPlayer();
  final FlutterSoundRecorder _recorder = FlutterSoundRecorder();
  final TextEditingController _textController = TextEditingController();
  bool _recorderInitialized = false;

  @override
  void initState() {
    super.initState();
    _initRecorder();
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    _recorder.closeRecorder();
    _textController.dispose();
    super.dispose();
  }

  Future<void> _initRecorder() async {
    await _recorder.openRecorder();
    _recorderInitialized = true;
  }

  Future<bool> _checkPermission() async {
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  Future<void> _startRecording() async {
    if (!await _checkPermission()) {
      _showAlert('Permiso requerido', 'Necesitamos acceso al microfono.');
      return;
    }

    if (!_recorderInitialized) {
      await _initRecorder();
    }

    final dir = await getTemporaryDirectory();
    final path = '${dir.path}/recording.wav';

    await _recorder.startRecorder(
      toFile: path,
      codec: Codec.pcm16WAV,
      sampleRate: 16000,
      numChannels: 1,
    );

    setState(() {
      _isRecording = true;
      _transcribedText = '';
    });
  }

  Future<void> _stopRecording() async {
    final path = await _recorder.stopRecorder();
    setState(() => _isRecording = false);

    if (path != null) {
      await _sendAudioToAPI(path);
    }
  }

  Future<void> _sendAudioToAPI(String filePath) async {
    setState(() => _isLoading = true);

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$apiBaseUrl/api/transcribe'),
      );
      request.fields['language'] = _selectedLang;
      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        final textMatch = RegExp(r'"text"\s*:\s*"([^"]*)"').firstMatch(responseBody);
        final text = textMatch?.group(1) ?? 'No se detecto texto.';
        setState(() => _transcribedText = text);
      } else {
        _showAlert('Error', 'Error al transcribir: $responseBody');
      }
    } catch (e) {
      _showAlert('Error', 'No se pudo conectar con la API.');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _synthesizeText() async {
    if (_inputText.trim().isEmpty) {
      _showAlert('Error', 'Escribe un texto para sintetizar.');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/synthesize?language=$_selectedLang&gender=neutral'),
        headers: {'Content-Type': 'application/json'},
        body: '{"text": "$_inputText", "language": "$_selectedLang", "gender": "neutral"}',
      );

      if (response.statusCode == 200) {
        final dir = await getTemporaryDirectory();
        final file = File('${dir.path}/tts_output.mp3');
        await file.writeAsBytes(response.bodyBytes);

        setState(() => _audioPath = file.path);
        _playAudio(file.path);
      } else {
        _showAlert('Error', 'Error al sintetizar.');
      }
    } catch (e) {
      _showAlert('Error', 'No se pudo conectar con la API.');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _playAudio(String path) async {
    await _audioPlayer.play(DeviceFileSource(path));
  }

  void _showAlert(String title, String message) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 60),
        child: Column(
          children: [
            const Text(
              'Speech Converter',
              style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFFE94560)),
            ),
            const SizedBox(height: 4),
            const Text('Voz a Texto y Texto a Voz', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 24),

            Wrap(
              spacing: 6,
              runSpacing: 6,
              alignment: WrapAlignment.center,
              children: languages.entries.map((e) {
                final isSelected = _selectedLang == e.key;
                return GestureDetector(
                  onTap: () => setState(() => _selectedLang = e.key),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: isSelected ? const Color(0xFFE94560) : const Color(0xFF16213E),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: isSelected ? const Color(0xFFE94560) : Colors.grey.shade800),
                    ),
                    child: Text(e.value, style: TextStyle(color: isSelected ? Colors.white : Colors.grey, fontSize: 12)),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 28),

            const Align(alignment: Alignment.centerLeft, child: Text('Voz a Texto', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold))),
            const SizedBox(height: 4),
            const Align(alignment: Alignment.centerLeft, child: Text('Presiona el boton, habla y se transcribira tu voz', style: TextStyle(color: Colors.grey, fontSize: 13))),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : (_isRecording ? _stopRecording : _startRecording),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isRecording ? Colors.red.shade700 : const Color(0xFFE94560),
                  padding: const EdgeInsets.symmetric(vertical: 20),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(50)),
                  elevation: 8,
                  shadowColor: Color(0xFFE94560).withValues(alpha: 0.4),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text(_isRecording ? 'Detener' : 'Grabar', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
              ),
            ),
            if (_transcribedText.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF16213E),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey.shade800),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Transcripcion:', style: TextStyle(color: Color(0xFFE94560), fontWeight: FontWeight.bold, fontSize: 12)),
                    const SizedBox(height: 6),
                    Text(_transcribedText, style: const TextStyle(color: Colors.white, fontSize: 16)),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 24),
            Container(height: 1, color: Colors.grey.shade800),
            const SizedBox(height: 24),

            const Align(alignment: Alignment.centerLeft, child: Text('Texto a Voz', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold))),
            const SizedBox(height: 4),
            const Align(alignment: Alignment.centerLeft, child: Text('Escribe un texto y escucha como suena', style: TextStyle(color: Colors.grey, fontSize: 13))),
            const SizedBox(height: 16),
            TextField(
              controller: _textController,
              maxLines: 4,
              onChanged: (v) => _inputText = v,
              decoration: InputDecoration(
                hintText: 'Escribe aqui tu texto...',
                hintStyle: const TextStyle(color: Colors.grey),
                fillColor: const Color(0xFF16213E),
                filled: true,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Colors.grey.shade800)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Colors.grey.shade800)),
              ),
              style: const TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _synthesizeText,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0F3460),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('Sintetizar', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
              ),
            ),
            if (_audioPath != null) ...[
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => _playAudio(_audioPath!),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF27AE60),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Reproducir Audio', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
