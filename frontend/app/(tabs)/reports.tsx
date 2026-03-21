import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
} from "react-native";

import { useEffect, useState } from "react";
import { useRouter } from "expo-router";

import API from "../../api/api";

export default function ReportsScreen() {
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [patientsData, setPatientsData] = useState<any[]>([]);

  // Fetch all reports
  const fetchReports = async () => {
    try {
      const res = await API.get("/screenings/history");
      const reports = res.data || [];

      // Group reports by patient name
      const grouped: any = {};

      reports.forEach((item: any) => {
        const name = item.patient_name?.trim() || "Unknown";

        if (!grouped[name]) {
          grouped[name] = [];
        }

        grouped[name].push(item);
      });

      // Sort each patient's reports (latest first)
      Object.keys(grouped).forEach((name) => {
        grouped[name].sort(
          (a: any, b: any) =>
            new Date(b.date).getTime() - new Date(a.date).getTime()
        );
      });

      // Format data
      const formatted = Object.keys(grouped).map((name) => ({
        patient_name: name,
        reports: grouped[name],
        latest: grouped[name][0],
      }));

      setPatientsData(formatted);
    } catch (error) {
      console.log("Error fetching reports:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const getRiskColor = (level: string) => {
    if (!level) return "#52c41a";

    const lower = level.toLowerCase();

    if (lower.includes("high")) return "#ff4d4f";
    if (lower.includes("moderate")) return "#faad14";

    return "#52c41a";
  };

  const renderItem = ({ item }: any) => {
    const latest = item.latest;

    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() =>
          router.push({
            pathname: "/patientReports",
            params: {
              patient_name: item.patient_name,
              reports: JSON.stringify(item.reports),
            },
          })
        }
      >
        <Text style={styles.name}>{item.patient_name}</Text>

        <Text
          style={[
            styles.risk,
            { color: getRiskColor(latest.risk_level) },
          ]}
        >
          {latest.risk_level}
        </Text>

        <Text style={styles.score}>
          Score: {Number(latest.final_score).toFixed(2)}
        </Text>

        <Text style={styles.date}>{latest.date}</Text>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Reports</Text>

      <FlatList
        data={patientsData}
        keyExtractor={(item) => item.patient_name}
        renderItem={renderItem}
      />
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

  name: {
    fontSize: 18,
    fontWeight: "600",
  },

  risk: {
    fontSize: 16,
    marginTop: 4,
  },

  score: {
    color: "#555",
    marginTop: 2,
  },

  date: {
    color: "#888",
    marginTop: 2,
    fontSize: 12,
  },

  loader: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
});