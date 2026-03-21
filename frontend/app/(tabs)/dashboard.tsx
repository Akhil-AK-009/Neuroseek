import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { router } from "expo-router";

export default function Dashboard() {
  return (
    <View style={styles.container}>

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>NeuroSeek</Text>

        <Text style={styles.subtitle}>
          Multimodal Parkinson's Screening
        </Text>
      </View>

      {/* Buttons */}
      <View style={styles.buttonContainer}>

        <TouchableOpacity
          style={styles.button}
          onPress={() => router.push("/(tabs)/patients")}
        >
          <Text style={styles.buttonText}>Patient Management</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.button}
          onPress={() => router.push("/(tabs)/reports")}
        >
          <Text style={styles.buttonText}>View Reports</Text>
        </TouchableOpacity>

      </View>

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "space-between",
    padding: 20,
  },

  header: {
    marginTop: 80,
    alignItems: "center",
  },

  title: {
    fontSize: 32,
    fontWeight: "bold",
  },

  subtitle: {
    fontSize: 16,
    color: "gray",
    marginTop: 10,
  },

  buttonContainer: {
    marginBottom: 60,
  },

  button: {
    backgroundColor: "#007AFF",
    padding: 16,
    borderRadius: 10,
    marginBottom: 15,
    alignItems: "center",
  },

  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});