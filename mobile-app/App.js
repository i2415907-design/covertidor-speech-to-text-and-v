import { useState, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
  ScrollView,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { StatusBar } from 'expo-status-bar';

import { API_BASE_URL as API_URL } from './config';

const LANGUAGES = [
  { code: 'es', label: 'Espanol' },
  { code: 'en', label: 'English' },
  { code: 'pt', label: 'Portugues' },
  { code: 'fr', label: 'Francais' },
  { code: 'de', label: 'Deutsch' },
  { code: 'it', label: 'Italiano' },
  { code: 'ja', label: 'Nihongo' },
  { code: 'ko', label: 'Korean' },
  { code: 'zh', label: 'Zhongwen' },
];

export default function App() {
  const [language, setLanguage] = useState('es');
  const [recording, setRecording] = useState(null);
  const [transcribedText, setTranscribedText] = useState('');
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [audioUri, setAudioUri] = useState(null);
  const soundRef = useRef(null);

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permiso requerido', 'Necesitamos acceso al microfono.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      setTranscribedText('');
    } catch (err) {
      Alert.alert('Error', 'No se pudo iniciar la grabacion.');
    }
  };

  const stopRecording = async () => {
    if (!recording) return;
    setLoading(true);

    try {
      await recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({ allowsRecordingIOS: false });

      const uri = recording.getURI();
      setRecording(null);

      await sendAudioToAPI(uri);
    } catch (err) {
      Alert.alert('Error', 'No se pudo detener la grabacion.');
      setLoading(false);
    }
  };

  const sendAudioToAPI = async (uri) => {
    try {
      const fileInfo = await FileSystem.getInfoAsync(uri);
      const formData = new FormData();

      formData.append('file', {
        uri: Platform.OS === 'ios' ? uri : uri,
        name: 'recording.wav',
        type: 'audio/wav',
      });
      formData.append('language', language);

      const response = await fetch(`${API_URL}/api/transcribe`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al transcribir');
      }

      const data = await response.json();
      setTranscribedText(data.text || 'No se detecto texto.');
    } catch (err) {
      Alert.alert('Error', err.message || 'No se pudo conectar con la API.');
    } finally {
      setLoading(false);
    }
  };

  const synthesizeText = async () => {
    if (!inputText.trim()) {
      Alert.alert('Error', 'Escribe un texto para sintetizar.');
      return;
    }

    setLoading(true);
    setAudioUri(null);

    try {
      const response = await fetch(
        `${API_URL}/api/synthesize?language=${language}&gender=neutral`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: inputText, language, gender: 'neutral' }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al sintetizar');
      }

      const fileUri = FileSystem.cacheDirectory + 'tts_output.mp3';
      const blob = await response.blob();

      const reader = new FileReader();
      reader.onload = async () => {
        const base64 = reader.result.split(',')[1];
        await FileSystem.writeAsStringAsync(fileUri, base64, {
          encoding: FileSystem.EncodingType.Base64,
        });
        setAudioUri(fileUri);
        setLoading(false);
      };
      reader.onerror = () => {
        Alert.alert('Error', 'No se pudo guardar el audio.');
        setLoading(false);
      };
      reader.readAsDataURL(blob);
    } catch (err) {
      Alert.alert('Error', err.message || 'No se pudo conectar con la API.');
      setLoading(false);
    }
  };

  const playAudio = async () => {
    if (!audioUri) return;

    try {
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
      }

      const { sound } = await Audio.Sound.createAsync({ uri: audioUri });
      soundRef.current = sound;
      await sound.playAsync();
    } catch (err) {
      Alert.alert('Error', 'No se pudo reproducir el audio.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <StatusBar style="light" />
      <Text style={styles.title}>Speech Converter</Text>
      <Text style={styles.subtitle}>Voz a Texto y Texto a Voz</Text>

      <View style={styles.langContainer}>
        {LANGUAGES.map((lang) => (
          <TouchableOpacity
            key={lang.code}
            style={[
              styles.langButton,
              language === lang.code && styles.langButtonActive,
            ]}
            onPress={() => setLanguage(lang.code)}
          >
            <Text
              style={[
                styles.langText,
                language === lang.code && styles.langTextActive,
              ]}
            >
              {lang.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Voz a Texto</Text>
        <Text style={styles.sectionDesc}>
          Presiona el boton, habla y se transcribira tu voz
        </Text>

        <TouchableOpacity
          style={[
            styles.recordButton,
            recording && styles.recordButtonActive,
          ]}
          onPress={recording ? stopRecording : startRecording}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" size="large" />
          ) : (
            <Text style={styles.recordButtonText}>
              {recording ? 'Detener' : 'Grabar'}
            </Text>
          )}
        </TouchableOpacity>

        {transcribedText ? (
          <View style={styles.resultBox}>
            <Text style={styles.resultLabel}>Transcripcion:</Text>
            <Text style={styles.resultText}>{transcribedText}</Text>
          </View>
        ) : null}
      </View>

      <View style={styles.divider} />

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Texto a Voz</Text>
        <Text style={styles.sectionDesc}>
          Escribe un texto y escucha como suena
        </Text>

        <TextInput
          style={styles.textInput}
          multiline
          placeholder="Escribe aqui tu texto..."
          placeholderTextColor="#999"
          value={inputText}
          onChangeText={setInputText}
        />

        <TouchableOpacity
          style={styles.synthButton}
          onPress={synthesizeText}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.synthButtonText}>Sintetizar</Text>
          )}
        </TouchableOpacity>

        {audioUri ? (
          <TouchableOpacity style={styles.playButton} onPress={playAudio}>
            <Text style={styles.playButtonText}>Reproducir Audio</Text>
          </TouchableOpacity>
        ) : null}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#1a1a2e',
    padding: 20,
    paddingTop: 60,
    paddingBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#e94560',
    textAlign: 'center',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#aaa',
    textAlign: 'center',
    marginBottom: 24,
  },
  langContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 6,
    marginBottom: 28,
  },
  langButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#16213e',
    borderWidth: 1,
    borderColor: '#333',
  },
  langButtonActive: {
    backgroundColor: '#e94560',
    borderColor: '#e94560',
  },
  langText: {
    color: '#aaa',
    fontSize: 12,
  },
  langTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  sectionDesc: {
    fontSize: 13,
    color: '#888',
    marginBottom: 16,
  },
  recordButton: {
    backgroundColor: '#e94560',
    paddingVertical: 20,
    borderRadius: 50,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#e94560',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 8,
  },
  recordButtonActive: {
    backgroundColor: '#c0392b',
    shadowColor: '#c0392b',
  },
  recordButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultBox: {
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  resultLabel: {
    color: '#e94560',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  resultText: {
    color: '#fff',
    fontSize: 16,
    lineHeight: 22,
  },
  divider: {
    height: 1,
    backgroundColor: '#333',
    marginVertical: 24,
  },
  textInput: {
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 16,
    color: '#fff',
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 12,
  },
  synthButton: {
    backgroundColor: '#0f3460',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  synthButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  playButton: {
    backgroundColor: '#27ae60',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  playButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
