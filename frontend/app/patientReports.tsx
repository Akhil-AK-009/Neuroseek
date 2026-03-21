import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
} from "react-native";

import { useLocalSearchParams, useRouter } from "expo-router";
import { useEffect, useState } from "react";

export default function PatientReportsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();

  const [reports, setReports] = useState<any[]>([]);

  // SAFE param handling
  const patient_name =
    typeof params.patient_name === "string"
      ? params.patient_name
      : "Unknown";

  // Parse reports
  useEffect(() => {
    if (params.reports) {
      try {
        const parsed = JSON.parse(params.reports as string);

        const sorted = parsed.sort(
          (a: any, b: any) =>
            new Date(b.date).getTime() - new Date(a.date).getTime()
        );

        setReports(sorted);
      } catch (error) {
        console.log("Error parsing reports:", error);
      }
    }
  }, [params.reports]);

  const getRiskColor = (level: string) => {
    if (!level) return "#52c41a";

    const lower = level.toLowerCase();

    if (lower.includes("high")) return "#ff4d4f";
    if (lower.includes("moderate")) return "#faad14";

    return "#52c41a";
  };

  const openReport = (item: any) => {
    router.push({
      pathname: "/report",
      params: {
        patient_name: item.patient_name,
        patient_age: item.patient_age,
        patient_gender: item.patient_gender?.trim(),

        handwriting_score: item.handwriting_score ?? 0,
        speech_score: item.speech_score ?? 0,
        gait_score: item.gait_score ?? 0,

        final_score: item.final_score,
        risk_level: item.risk_level,

        date: item.date,
      },
    });
  };

  const renderItem = ({ item }: any) => {
    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => openReport(item)}
      >
        <Text style={styles.date}>{item.date}</Text>

        <Text
          style={[
            styles.risk,
            { color: getRiskColor(item.risk_level) },
          ]}
        >
          {item.risk_level}
        </Text>

        <Text style={styles.score}>
          Score: {Number(item.final_score).toFixed(2)}
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>{patient_name}</Text>

      {reports.length === 0 ? (
        <Text style={styles.empty}>No screenings available</Text>
      ) : (
        <FlatList
          data={reports}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderItem}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f7fb",
    padding: 16,
  },

  header: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 16,
  },

  card: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    elevation: 2,
  },

  date: {
    color: "#888",
    fontSize: 13,
  },

  risk: {
    fontSize: 16,
    fontWeight: "600",
    marginTop: 4,
  },

  score: {
    marginTop: 4,
    color: "#555",
  },

  empty: {
    textAlign: "center",
    marginTop: 40,
    color: "#888",
  },
});