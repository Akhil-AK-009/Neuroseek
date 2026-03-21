import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Image,
  ScrollView,
} from "react-native";

import { useState } from "react";
import { useRouter, useLocalSearchParams } from "expo-router";

import * as ImagePicker from "expo-image-picker";
import * as DocumentPicker from "expo-document-picker";
import { Audio } from "expo-av";
import { Camera } from "expo-camera";

import API from "../api/api";

export default function ScreeningScreen() {
  const router = useRouter();
  const { patient_id, patient_name } = useLocalSearchParams();

  const [step, setStep] = useState(1);

  const [spiral, setSpiral] = useState<any>(null);
  const [wave, setWave] = useState<any>(null);
  const [audio, setAudio] = useState<any>(null);
  const [video, setVideo] = useState<any>(null);

  const [recording, setRecording] = useState<any>(null);

  // Upload image
  const pickImage = async (setFunc: any) => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
    });
    if (!res.canceled) setFunc(res.assets[0]);
  };

  // Capture image
  const captureImage = async (setFunc: any) => {
    const res = await ImagePicker.launchCameraAsync({
      mediaTypes: ["images"],
    });
    if (!res.canceled) setFunc(res.assets[0]);
  };

  // File picker
  const pickFile = async (setFunc: any) => {
    const res = await DocumentPicker.getDocumentAsync({});
    if (res.assets) setFunc(res.assets[0]);
  };

  // Audio recording
  const startRecording = async () => {
    await Audio.requestPermissionsAsync();

    const { recording } = await Audio.Recording.createAsync(
      Audio.RecordingOptionsPresets.HIGH_QUALITY
    );

    setRecording(recording);
  };

  const stopRecording = async () => {
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();

    setAudio({
      uri,
      name: "recording.wav",
      mimeType: "audio/wav",
    });

    setRecording(null);
  };

  // Video recording
  const recordVideo = async () => {
    const permission = await Camera.requestCameraPermissionsAsync();
    if (!permission.granted) return;

    const res = await ImagePicker.launchCameraAsync({
      mediaTypes: ["videos"],
    });

    if (!res.canceled) setVideo(res.assets[0]);
  };

  // Final full screening
  const handleFullScreening = async () => {
    if (!spiral || !wave || !audio || !video) {
      return Alert.alert("Please provide all inputs");
    }

    const formData = new FormData();

    formData.append("spiral", {
      uri: spiral.uri,
      name: "spiral.jpg",
      type: "image/jpeg",
    } as any);

    formData.append("wave", {
      uri: wave.uri,
      name: "wave.jpg",
      type: "image/jpeg",
    } as any);

    formData.append("audio", {
      uri: audio.uri,
      name: audio.name || "audio.wav",
      type: audio.mimeType || "audio/mpeg",
    } as any);

    formData.append("video", {
      uri: video.uri,
      name: video.name || "gait.mp4",
      type: "video/mp4",
    } as any);

    try {
      const res = await API.post(
        `/screenings/full?patient_id=${patient_id}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      console.log("FULL API RESPONSE:", res.data);

      // Warn if screening is incomplete
      if (!res.data.is_complete) {
        Alert.alert("Warning", "Screening is not fully complete");
      }

      // Extract backend data safely
      const backendReport = res.data.report || {};
      const modalities = res.data.modalities || {};
      const finalResult = res.data.final_result || {};

      // Build final report object (correct mapping)
      const reportData = {
        patient_name: backendReport.patient_name || patient_name || "Unknown",
        patient_age: backendReport.patient_age ?? "N/A",
        patient_gender: backendReport.patient_gender ?? "N/A",

        handwriting_score: modalities.handwriting ?? 0,
        speech_score: modalities.speech ?? 0,
        gait_score: modalities.gait ?? 0,

        final_score: finalResult.risk_score ?? 0,
        risk_level: finalResult.risk_level ?? "Unknown",

        date: backendReport.date || new Date().toLocaleDateString(),
      };

      console.log("FINAL REPORT:", reportData);

      // Navigate to report screen
      router.push({
        pathname: "/report",
        params: reportData,
      });

    } catch (error) {
      console.log("Full screening error:", error);
      Alert.alert("Screening failed");
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Screening: {patient_name}</Text>
      <Text style={styles.step}>Step {step} / 3</Text>

      {/* Step 1 - Handwriting */}
      {step === 1 && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Handwriting</Text>

          <View style={styles.row}>
            <TouchableOpacity style={styles.optionBtn} onPress={() => pickImage(setSpiral)}>
              <Text>Upload Spiral</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.optionBtn} onPress={() => captureImage(setSpiral)}>
              <Text>Camera</Text>
            </TouchableOpacity>
          </View>

          {spiral && <Image source={{ uri: spiral.uri }} style={styles.preview} />}

          <View style={styles.row}>
            <TouchableOpacity style={styles.optionBtn} onPress={() => pickImage(setWave)}>
              <Text>Upload Wave</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.optionBtn} onPress={() => captureImage(setWave)}>
              <Text>Camera</Text>
            </TouchableOpacity>
          </View>

          {wave && <Image source={{ uri: wave.uri }} style={styles.preview} />}

          <TouchableOpacity style={styles.nextBtn} onPress={() => setStep(2)}>
            <Text style={styles.nextText}>Next → Speech</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Step 2 - Speech */}
      {step === 2 && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Speech</Text>

          <TouchableOpacity style={styles.optionBtn} onPress={() => pickFile(setAudio)}>
            <Text>Upload Audio</Text>
          </TouchableOpacity>

          {!recording ? (
            <TouchableOpacity style={styles.optionBtn} onPress={startRecording}>
              <Text>Start Recording</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity style={styles.optionBtn} onPress={stopRecording}>
              <Text>Stop Recording</Text>
            </TouchableOpacity>
          )}

          {audio && <Text style={styles.success}>Audio Ready</Text>}

          <TouchableOpacity style={styles.nextBtn} onPress={() => setStep(3)}>
            <Text style={styles.nextText}>Next → Gait</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Step 3 - Gait */}
      {step === 3 && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Gait</Text>

          <TouchableOpacity style={styles.optionBtn} onPress={() => pickFile(setVideo)}>
            <Text>Upload Video</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.optionBtn} onPress={recordVideo}>
            <Text>Record Video</Text>
          </TouchableOpacity>

          {video && <Text style={styles.success}>Video Ready</Text>}

          <TouchableOpacity style={styles.nextBtn} onPress={handleFullScreening}>
            <Text style={styles.nextText}>Generate Result</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7fb", padding: 16 },

  title: { fontSize: 24, fontWeight: "bold" },

  step: { color: "gray", marginBottom: 15 },

  card: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 16,
    marginBottom: 20,
    elevation: 3,
  },

  sectionTitle: { fontSize: 18, fontWeight: "600", marginBottom: 10 },

  row: { flexDirection: "row", justifyContent: "space-between" },

  optionBtn: {
    backgroundColor: "#eef1f5",
    padding: 12,
    borderRadius: 10,
    width: "48%",
    alignItems: "center",
    marginBottom: 10,
  },

  preview: {
    width: "100%",
    height: 150,
    borderRadius: 10,
    marginBottom: 10,
  },

  nextBtn: {
    backgroundColor: "#000",
    padding: 15,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 10,
  },

  nextText: { color: "#fff", fontWeight: "bold" },

  success: { color: "green", marginBottom: 10 },
});