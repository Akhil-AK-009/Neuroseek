import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { router } from "expo-router";

export default function Screening() {
  return (
    <View style={styles.container}>

      <Text style={styles.title}>Start Screening</Text>

      <Text style={styles.subtitle}>
        Choose a modality for Parkinson's screening
      </Text>

      <View style={styles.section}>

        <Text style={styles.sectionTitle}>Handwriting</Text>

        <TouchableOpacity
          style={styles.button}
          onPress={() => router.push("/handwriting")}
        >
          <Text style={styles.buttonText}>Handwriting Screening</Text>
        </TouchableOpacity>

      </View>

      <View style={styles.section}>

        <Text style={styles.sectionTitle}>Speech</Text>

        <TouchableOpacity
          style={styles.button}
          onPress={() => router.push("/speech")}
        >
          <Text style={styles.buttonText}>Speech Screening</Text>
        </TouchableOpacity>

      </View>

      <View style={styles.section}>

        <Text style={styles.sectionTitle}>Gait</Text>

        <TouchableOpacity
          style={styles.button}
          onPress={() => router.push("/gait")}
        >
          <Text style={styles.buttonText}>Gait Video Screening</Text>
        </TouchableOpacity>

      </View>

      <TouchableOpacity
        style={styles.fullButton}
        onPress={() => router.push("/full-screening")}
      >
        <Text style={styles.buttonText}>Full Multimodal Screening</Text>
      </TouchableOpacity>

    </View>
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    padding: 20,
    justifyContent: "center",
  },

  title: {
    fontSize: 28,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 10,
  },

  subtitle: {
    fontSize: 16,
    textAlign: "center",
    color: "gray",
    marginBottom: 40,
  },

  section: {
    marginBottom: 20,
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 10,
  },

  button: {
    backgroundColor: "#007AFF",
    padding: 16,
    borderRadius: 10,
    alignItems: "center",
  },

  fullButton: {
    backgroundColor: "#28A745",
    padding: 16,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 30,
  },

  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },

});