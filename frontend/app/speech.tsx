import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from "react-native";

import { useState, useEffect } from "react";
import { Audio } from "expo-av";
import * as DocumentPicker from "expo-document-picker";
import { useLocalSearchParams, useRouter } from "expo-router";

import API from "../api/api";

export default function SpeechScreen() {
  const router = useRouter();

  /**
   * Safe patient parsing
   */
  const { patient } = useLocalSearchParams();

  let parsedPatient: any = null;
  try {
    parsedPatient =
      typeof patient === "string" ? JSON.parse(patient) : patient;
  } catch (e) {
    console.log("Patient parse error:", e);
    parsedPatient = null;
  }

  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [audioUri, setAudioUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);

  /**
   * Recording timer
   */
  useEffect(() => {
    let interval: any;

    if (isRecording) {
      interval = setInterval(() => {
        setSeconds((prev) => prev + 1);
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isRecording]);

  /**
   * Start recording
   */
  const startRecording = async () => {
    if (recording) {
      Alert.alert("Already recording");
      return;
    }

    try {
      const permission = await Audio.requestPermissionsAsync();

      if (!permission.granted) {
        Alert.alert("Microphone permission required");
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
      setIsRecording(true);
      setSeconds(0);
    } catch (err) {
      console.log("Recording error:", err);
    }
  };

  /**
   * Stop recording
   */
  const stopRecording = async () => {
    if (!recording) return;

    try {
      await recording.stopAndUnloadAsync();

      const uri = recording.getURI();

      setAudioUri(uri);
      setRecording(null);
      setIsRecording(false);
    } catch (err) {
      console.log("Stop error:", err);
    }
  };

  /**
   * Pick audio file
   */
  const pickAudio = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: "audio/*",
    });

    if (!result.canceled && result.assets?.length > 0) {
      setAudioUri(result.assets[0].uri);
    }
  };

  /**
   * Analyze speech → move to gait
   */
  const analyzeSpeech = async () => {
    if (!parsedPatient || !parsedPatient.id) {
      Alert.alert("Invalid patient data");
      return;
    }

    if (!audioUri) {
      Alert.alert("Select or record audio first");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();

      formData.append("audio", {
        uri: audioUri,
        name: "speech.wav",
        type: "audio/wav",
      } as any);

      await API.post(
        `/screenings/speech?patient_id=${parsedPatient.id}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      /**
       * Navigate to gait screen
       */
      router.push({
        pathname: "/gait",
        params: {
          patient: JSON.stringify(parsedPatient),
        },
      });

    } catch (error: any) {
      console.log("Speech API error:", error?.response?.data || error.message);
      Alert.alert("Upload failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        Speech Screening ({parsedPatient?.full_name || "No Patient"})
      </Text>

      {isRecording && (
        <Text style={styles.recordingText}>
          Recording... {seconds}s
        </Text>
      )}

      <TouchableOpacity style={styles.recordBtn} onPress={startRecording}>
        <Text style={styles.buttonText}>Start Recording</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.stopBtn} onPress={stopRecording}>
        <Text style={styles.buttonText}>Stop Recording</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.uploadBtn} onPress={pickAudio}>
        <Text style={styles.buttonText}>Upload Audio</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.analyzeBtn}
        onPress={analyzeSpeech}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Analyze Speech</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    padding: 20,
    backgroundColor: "#f5f7fa",
  },

  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },

  recordingText: {
    color: "red",
    fontSize: 16,
    marginBottom: 10,
    fontWeight: "600",
  },

  recordBtn: {
    backgroundColor: "#007AFF",
    padding: 15,
    borderRadius: 10,
    marginVertical: 5,
    width: 220,
    alignItems: "center",
  },

  stopBtn: {
    backgroundColor: "#ff3b30",
    padding: 15,
    borderRadius: 10,
    marginVertical: 5,
    width: 220,
    alignItems: "center",
  },

  uploadBtn: {
    backgroundColor: "#34c759",
    padding: 15,
    borderRadius: 10,
    marginVertical: 5,
    width: 220,
    alignItems: "center",
  },

  analyzeBtn: {
    backgroundColor: "#5856d6",
    padding: 15,
    borderRadius: 10,
    marginVertical: 10,
    width: 220,
    alignItems: "center",
  },

  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});