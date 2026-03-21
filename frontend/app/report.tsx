import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";

import { useLocalSearchParams, useRouter } from "expo-router";

export default function ReportScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();

  // FIX: Proper param parsing (Expo Router safe handling)
  const patient_name =
    typeof params.patient_name === "string"
      ? params.patient_name
      : "N/A";

  const patient_age =
    typeof params.patient_age === "string"
      ? params.patient_age
      : "N/A";

  const patient_gender =
    typeof params.patient_gender === "string"
      ? params.patient_gender
      : "N/A";

  const date =
    typeof params.date === "string"
      ? params.date
      : new Date().toLocaleDateString();

  const handwriting_score = Number(params.handwriting_score ?? 0);
  const speech_score = Number(params.speech_score ?? 0);
  const gait_score = Number(params.gait_score ?? 0);

  const final_score = Number(params.final_score ?? 0);

  const risk_level =
    typeof params.risk_level === "string"
      ? params.risk_level
      : "Unknown";

  // Risk color helper
  const getRiskColor = (level: string) => {
    if (!level) return "#52c41a";

    const lower = level.toLowerCase();

    if (lower.includes("high")) return "#ff4d4f";
    if (lower.includes("moderate")) return "#faad14";

    return "#52c41a";
  };

  return (
    <View style={styles.root}>
      {/* FIXED HEADER */}
      <View style={styles.fixedHeader}>
        <Text style={styles.header}>NeuroSeek Screening Report</Text>
      </View>

      {/* SCROLLABLE CONTENT */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Patient Information */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Patient Information</Text>

          <Row label="Name" value={patient_name} />
          <Row label="Age" value={patient_age} />
          <Row label="Gender" value={patient_gender.trim()} />
          <Row label="Date" value={date} />
        </View>

        {/* Final Assessment */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Final Assessment</Text>

          <Text style={styles.finalScore}>
            {final_score.toFixed(2)}
          </Text>

          <Text
            style={[
              styles.riskLevel,
              { color: getRiskColor(risk_level) },
            ]}
          >
            {risk_level}
          </Text>
        </View>

        {/* Modality Scores */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Modality Scores</Text>

          <Row label="Handwriting" value={handwriting_score.toFixed(2)} />
          <Row label="Speech" value={speech_score.toFixed(2)} />
          <Row label="Gait" value={gait_score.toFixed(2)} />
        </View>

        {/* Disclaimer */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Disclaimer</Text>
          <Text style={styles.disclaimer}>
            This report is AI-generated and intended for screening purposes only.
            Please consult a medical professional for confirmation.
          </Text>
        </View>

        {/* Buttons */}
        <TouchableOpacity
          style={styles.primaryButton}
          onPress={() => router.replace("/(tabs)/dashboard")}
        >
          <Text style={styles.primaryText}>Back to Dashboard</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={() => router.replace("/(tabs)/patients")}
        >
          <Text style={styles.secondaryText}>Start New Screening</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

// Reusable row component
function Row({ label, value }: { label: string; value: any }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: "#f5f7fb",
  },

  fixedHeader: {
    backgroundColor: "#f5f7fb",
    padding: 16,
    elevation: 4,
    zIndex: 10,
  },

  header: {
    fontSize: 22,
    fontWeight: "bold",
  },

  scrollContent: {
    padding: 16,
    paddingBottom: 80,
  },

  card: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    elevation: 2,
  },

  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 10,
  },

  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: 6,
  },

  label: {
    color: "#555",
  },

  value: {
    fontWeight: "500",
  },

  finalScore: {
    fontSize: 32,
    fontWeight: "bold",
    textAlign: "center",
  },

  riskLevel: {
    textAlign: "center",
    fontSize: 18,
    fontWeight: "600",
  },

  disclaimer: {
    color: "#666",
    fontSize: 13,
  },

  primaryButton: {
    backgroundColor: "#000",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },

  primaryText: {
    color: "#fff",
    fontWeight: "600",
  },

  secondaryButton: {
    backgroundColor: "#eaeaea",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },

  secondaryText: {
    fontWeight: "600",
  },
});