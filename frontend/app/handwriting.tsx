import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  ScrollView,
  ActivityIndicator,
} from "react-native";

import * as ImagePicker from "expo-image-picker";
import { useState } from "react";
import { useLocalSearchParams, useRouter } from "expo-router";

import API from "../api/api";

export default function Handwriting() {
  const router = useRouter();

  // Get patient
  const { patient } = useLocalSearchParams();

  let parsedPatient: any = null;
  try {
    parsedPatient =
      typeof patient === "string" ? JSON.parse(patient) : patient;
  } catch {
    parsedPatient = null;
  }

  const [spiralImage, setSpiralImage] = useState<string | null>(null);
  const [waveImage, setWaveImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  /**
   * Pick / capture functions
   */
  const pickSpiral = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 1,
    });

    if (!result.canceled) {
      setSpiralImage(result.assets[0].uri);
    }
  };

  const captureSpiral = async () => {
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ["images"],
      quality: 1,
    });

    if (!result.canceled) {
      setSpiralImage(result.assets[0].uri);
    }
  };

  const pickWave = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 1,
    });

    if (!result.canceled) {
      setWaveImage(result.assets[0].uri);
    }
  };

  const captureWave = async () => {
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ["images"],
      quality: 1,
    });

    if (!result.canceled) {
      setWaveImage(result.assets[0].uri);
    }
  };

  /**
   * Analyze handwriting and move to speech
   */
  const analyzeHandwriting = async () => {
    if (!parsedPatient || !parsedPatient.id) {
      Alert.alert("Invalid patient data");
      return;
    }

    if (!spiralImage || !waveImage) {
      Alert.alert("Please upload both spiral and wave images");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();

      formData.append("spiral", {
        uri: spiralImage,
        name: "spiral.jpg",
        type: "image/jpeg",
      } as any);

      formData.append("wave", {
        uri: waveImage,
        name: "wave.jpg",
        type: "image/jpeg",
      } as any);

      await API.post(
        `/screenings/handwriting?patient_id=${parsedPatient.id}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      /**
       * Move to speech screen with patient
       */
      router.push({
        pathname: "/speech",
        params: {
          patient: JSON.stringify(parsedPatient),
        },
      });

    } catch (error) {
      console.log("Handwriting error:", error);
      Alert.alert("Error analyzing handwriting");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>
        Handwriting Screening ({parsedPatient?.full_name || "No Patient"})
      </Text>

      <Text style={styles.subtitle}>
        Upload or capture spiral and wave drawings
      </Text>

      <Text style={styles.sectionTitle}>Spiral Drawing</Text>

      <TouchableOpacity style={styles.button} onPress={pickSpiral}>
        <Text style={styles.buttonText}>Upload Spiral Image</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.button} onPress={captureSpiral}>
        <Text style={styles.buttonText}>Capture Spiral</Text>
      </TouchableOpacity>

      {spiralImage && (
        <Image source={{ uri: spiralImage }} style={styles.preview} />
      )}

      <Text style={styles.sectionTitle}>Wave Drawing</Text>

      <TouchableOpacity style={styles.button} onPress={pickWave}>
        <Text style={styles.buttonText}>Upload Wave Image</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.button} onPress={captureWave}>
        <Text style={styles.buttonText}>Capture Wave</Text>
      </TouchableOpacity>

      {waveImage && (
        <Image source={{ uri: waveImage }} style={styles.preview} />
      )}

      <TouchableOpacity
        style={styles.analyzeButton}
        onPress={analyzeHandwriting}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Analyze Handwriting</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    paddingBottom: 40,
  },

  title: {
    fontSize: 22,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 10,
  },

  subtitle: {
    fontSize: 14,
    textAlign: "center",
    color: "gray",
    marginBottom: 30,
  },

  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 10,
    marginTop: 10,
  },

  button: {
    backgroundColor: "#007AFF",
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
    marginBottom: 10,
  },

  analyzeButton: {
    backgroundColor: "#28A745",
    padding: 16,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 20,
  },

  buttonText: {
    color: "white",
    fontWeight: "600",
  },

  preview: {
    width: "100%",
    height: 200,
    resizeMode: "contain",
    marginBottom: 20,
  },
});