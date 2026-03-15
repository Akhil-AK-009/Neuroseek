import { View, Text, StyleSheet, TouchableOpacity, Image, Alert, ScrollView } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { useState } from "react";
import API from "../api/api";

export default function Handwriting() {

  const [spiralImage, setSpiralImage] = useState<string | null>(null);
  const [waveImage, setWaveImage] = useState<string | null>(null);

  const [result, setResult] = useState<any>(null);

  const pickSpiral = async () => {

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });

    if (!result.canceled) {
      setSpiralImage(result.assets[0].uri);
    }

  };

  const captureSpiral = async () => {

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });

    if (!result.canceled) {
      setSpiralImage(result.assets[0].uri);
    }

  };

  const pickWave = async () => {

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });

    if (!result.canceled) {
      setWaveImage(result.assets[0].uri);
    }

  };

  const captureWave = async () => {

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });

    if (!result.canceled) {
      setWaveImage(result.assets[0].uri);
    }

  };

  const analyzeHandwriting = async () => {

    if (!spiralImage || !waveImage) {
      Alert.alert("Please upload both spiral and wave images");
      return;
    }

    try {

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

      const patientId = 1;

      const response = await API.post(
        `/screenings/handwriting?patient_id=${patientId}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log("Handwriting result:", response.data);

      setResult(response.data);

    } catch (error) {

      console.log("Upload error:", error);
      Alert.alert("Error analyzing handwriting");

    }

  };

  return (
    <ScrollView contentContainerStyle={styles.container}>

      <Text style={styles.title}>Handwriting Screening</Text>

      <Text style={styles.subtitle}>
        Upload or Capture Spiral and Wave Drawings
      </Text>

      <Text style={styles.sectionTitle}>Spiral Drawing</Text>

      <TouchableOpacity style={styles.button} onPress={pickSpiral}>
        <Text style={styles.buttonText}>Upload Spiral Image</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.button} onPress={captureSpiral}>
        <Text style={styles.buttonText}>Capture Spiral with Camera</Text>
      </TouchableOpacity>

      {spiralImage && (
        <Image source={{ uri: spiralImage }} style={styles.preview} />
      )}

      <Text style={styles.sectionTitle}>Wave Drawing</Text>

      <TouchableOpacity style={styles.button} onPress={pickWave}>
        <Text style={styles.buttonText}>Upload Wave Image</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.button} onPress={captureWave}>
        <Text style={styles.buttonText}>Capture Wave with Camera</Text>
      </TouchableOpacity>

      {waveImage && (
        <Image source={{ uri: waveImage }} style={styles.preview} />
      )}

      <TouchableOpacity style={styles.analyzeButton} onPress={analyzeHandwriting}>
        <Text style={styles.buttonText}>Analyze Handwriting</Text>
      </TouchableOpacity>

      {result && (
        <View style={styles.resultCard}>

          <Text style={styles.resultTitle}>
            Handwriting Screening Result
          </Text>

          <Text style={styles.resultText}>
            Risk Score: {result.overall_risk.score}
          </Text>

          <Text style={styles.resultText}>
            Severity: {result.overall_risk.level}
          </Text>

          <Text style={styles.resultInterpretation}>
            {result.interpretation}
          </Text>

        </View>
      )}

    </ScrollView>
  );
}

const styles = StyleSheet.create({

  container: {
    padding: 20,
    paddingBottom: 40,
  },

  title: {
    fontSize: 26,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 10,
  },

  subtitle: {
    fontSize: 16,
    textAlign: "center",
    color: "gray",
    marginBottom: 30,
  },

  sectionTitle: {
    fontSize: 18,
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

  resultCard: {
    marginTop: 30,
    padding: 20,
    backgroundColor: "#F5F5F5",
    borderRadius: 12,
  },

  resultTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 10,
  },

  resultText: {
    fontSize: 16,
    marginBottom: 5,
  },

  resultInterpretation: {
    marginTop: 10,
    fontSize: 15,
    fontStyle: "italic",
  },

});