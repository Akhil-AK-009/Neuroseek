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
  const [results, setResults] = useState<any>({});

  // 📸 Upload Image
  const pickImage = async (setFunc: any) => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
    });
    if (!res.canceled) setFunc(res.assets[0]);
  };

  // 📷 Capture Image
  const captureImage = async (setFunc: any) => {
    const res = await ImagePicker.launchCameraAsync({
      mediaTypes: ["images"],
    });
    if (!res.canceled) setFunc(res.assets[0]);
  };

  // 📁 File picker
  const pickFile = async (setFunc: any) => {
    const res = await DocumentPicker.getDocumentAsync({});
    if (res.assets) setFunc(res.assets[0]);
  };

  // 🎤 Recording
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

  // 🎥 Video record
  const recordVideo = async () => {
    const permission = await Camera.requestCameraPermissionsAsync();
    if (!permission.granted) return;

    const res = await ImagePicker.launchCameraAsync({
      mediaTypes: ["videos"],
    });

    if (!res.canceled) setVideo(res.assets[0]);
  };

  // ✍️ Handwriting
  const handleHandwriting = async () => {
    if (!spiral || !wave) return Alert.alert("Upload both images");

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

    try {
      const res = await API.post(
        `/screenings/handwriting?patient_id=${patient_id}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setResults((prev: any) => ({
        ...prev,
        handwriting_score: res.data.handwriting_score,
      }));

      setStep(2);
    } catch (err) {
      Alert.alert("Handwriting failed");
    }
  };

  // 🎤 Speech
  const handleSpeech = async () => {
    if (!audio) return Alert.alert("Upload or record audio");

    const formData = new FormData();

    formData.append("audio", {
      uri: audio.uri,
      name: audio.name || "audio.wav",
      type: audio.mimeType || "audio/mpeg",
    } as any);

    try {
      const res = await API.post(
        `/screenings/speech?patient_id=${patient_id}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setResults((prev: any) => ({
        ...prev,
        speech_score: res.data.speech_score,
      }));

      setStep(3);
    } catch (err) {
      Alert.alert("Speech failed");
    }
  };

  // 🚶 Gait + FINAL RESULT
  const handleGait = async () => {
    if (!video) return Alert.alert("Upload or record video");

    const formData = new FormData();

    formData.append("video", {
      uri: video.uri,
      name: video.name || "gait.mp4",
      type: "video/mp4",
    } as any);

    try {
      const res = await API.post(
        `/screenings/gait?patient_id=${patient_id}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      const finalData = {
        handwriting_score: Number(results.handwriting_score || 0),
        speech_score: Number(results.speech_score || 0),
        gait_score: Number(res.data.gait_score || 0),

        final_score: Number(res.data.final_risk_score || 0), // ✅ FIX
        risk_level: res.data.risk_level || "Unknown",
      };

      console.log("FINAL DATA:", finalData);

      router.push({
        pathname: "/result",
        params: finalData,
      });

    } catch (error) {
      console.log("Gait error:", error);
      Alert.alert("Gait processing failed");
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Screening: {patient_name}</Text>
      <Text style={styles.step}>Step {step} / 3</Text>

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

          <TouchableOpacity style={styles.nextBtn} onPress={handleHandwriting}>
            <Text style={styles.nextText}>Next → Speech</Text>
          </TouchableOpacity>
        </View>
      )}

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

          {audio && <Text style={styles.success}>✔ Audio Ready</Text>}

          <TouchableOpacity style={styles.nextBtn} onPress={handleSpeech}>
            <Text style={styles.nextText}>Next → Gait</Text>
          </TouchableOpacity>
        </View>
      )}

      {step === 3 && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Gait</Text>

          <TouchableOpacity style={styles.optionBtn} onPress={() => pickFile(setVideo)}>
            <Text>Upload Video</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.optionBtn} onPress={recordVideo}>
            <Text>Record Video</Text>
          </TouchableOpacity>

          {video && <Text style={styles.success}>✔ Video Ready</Text>}

          <TouchableOpacity style={styles.nextBtn} onPress={handleGait}>
            <Text style={styles.nextText}>Generate Result</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

// 🎨 Styles
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