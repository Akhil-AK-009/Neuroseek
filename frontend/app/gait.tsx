import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from "react-native";

import { useState } from "react";
import * as DocumentPicker from "expo-document-picker";
import * as ImagePicker from "expo-image-picker";
import { useLocalSearchParams, useRouter } from "expo-router";

import API from "../api/api";

export default function GaitScreen() {
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

  const [videoUri, setVideoUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  /**
   * Pick video from device
   */
  const pickVideo = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: "video/*",
    });

    if (!result.canceled && result.assets?.length > 0) {
      setVideoUri(result.assets[0].uri);
    }
  };

  /**
   * Record video using camera
   */
  const recordVideo = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();

    if (!permission.granted) {
      Alert.alert("Camera permission required");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      quality: 1,
    });

    if (!result.canceled && result.assets?.length > 0) {
      setVideoUri(result.assets[0].uri);
    }
  };

  /**
   * Analyze gait and navigate to report
   */
  const analyzeGait = async () => {
    if (!parsedPatient || !parsedPatient.id) {
      Alert.alert("Invalid patient data");
      return;
    }

    if (!videoUri) {
      Alert.alert("Please upload or record a video");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();

      formData.append("video", {
        uri: videoUri,
        name: "gait.mp4",
        type: "video/mp4",
      } as any);

      const response = await API.post(
        `/screenings/gait?patient_id=${parsedPatient.id}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const data = response.data;

      console.log("Gait response:", data);

      /**
       * Ensure full patient data (fallback)
       */
      let patientData = parsedPatient;

      if (!patientData?.full_name) {
        try {
          const res = await API.get(`/patients/${parsedPatient.id}`);
          patientData = res.data;
        } catch (err) {
          console.log("Patient fetch error:", err);
        }
      }

      /**
       * Navigate to report screen (FIXED)
       */
      router.push({
        pathname: "/report",
        params: {
          handwriting_score: data.handwriting_score ?? 0,
          speech_score: data.speech_score ?? 0,
          gait_score: data.gait_score ?? 0,
          final_score: data.final_risk_score ?? 0,
          risk_level: data.risk_level ?? "Unknown",

          patient_name: patientData?.full_name || "N/A",
          patient_age: patientData?.age || "N/A",
          patient_gender: patientData?.gender?.trim() || "N/A",

          // FIX: Ensure date is always passed
          date: new Date().toLocaleDateString(),
        },
      });

    } catch (error: any) {
      console.log("Gait API error:", error?.response?.data || error.message);
      Alert.alert("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        Gait Screening ({parsedPatient?.full_name || "No Patient"})
      </Text>

      <TouchableOpacity style={styles.uploadBtn} onPress={pickVideo}>
        <Text style={styles.buttonText}>Upload Video</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.recordBtn} onPress={recordVideo}>
        <Text style={styles.buttonText}>Record Video</Text>
      </TouchableOpacity>

      {videoUri && <Text style={styles.fileText}>Video selected</Text>}

      <TouchableOpacity
        style={styles.analyzeBtn}
        onPress={analyzeGait}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Analyze Gait</Text>
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

  uploadBtn: {
    backgroundColor: "#34c759",
    padding: 15,
    borderRadius: 10,
    marginVertical: 8,
    width: 220,
    alignItems: "center",
  },

  recordBtn: {
    backgroundColor: "#ff9500",
    padding: 15,
    borderRadius: 10,
    marginVertical: 8,
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

  fileText: {
    marginTop: 10,
    color: "green",
    fontSize: 14,
  },
});