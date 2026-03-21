import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
} from "react-native";

import { useState, useCallback } from "react";
import { useFocusEffect } from "@react-navigation/native";
import { useRouter } from "expo-router";

import API from "../../api/api";

export default function Patients() {
  const router = useRouter();

  const [patients, setPatients] = useState([]);
  const [editingId, setEditingId] = useState<number | null>(null);

  const [fullName, setFullName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [phone, setPhone] = useState("");

  useFocusEffect(
    useCallback(() => {
      fetchPatients();
    }, [])
  );

  const fetchPatients = async () => {
    try {
      const response = await API.get("/patients");
      setPatients(response.data);
    } catch (error: any) {
      Alert.alert("Error", "Failed to load patients");
    }
  };

  const addPatient = async () => {
    try {
      await API.post("/patients", {
        full_name: fullName,
        age: parseInt(age),
        gender,
        phone,
      });

      clearForm();
      fetchPatients();
    } catch (error: any) {
      Alert.alert("Error", "Failed to add patient");
    }
  };

  const updatePatient = async () => {
    try {
      await API.put(`/patients/${editingId}`, {
        full_name: fullName,
        age: parseInt(age),
        gender,
        phone,
      });

      clearForm();
      fetchPatients();
    } catch (error: any) {
      Alert.alert("Error", "Failed to update patient");
    }
  };

  const deletePatient = async (id: number) => {
    try {
      await API.delete(`/patients/${id}`);
      fetchPatients();
    } catch (error: any) {
      Alert.alert("Error", "Failed to delete patient");
    }
  };

  const editPatient = (patient: any) => {
    setEditingId(patient.id);
    setFullName(patient.full_name);
    setAge(patient.age.toString());
    setGender(patient.gender);
    setPhone(patient.phone);
  };

  const clearForm = () => {
    setEditingId(null);
    setFullName("");
    setAge("");
    setGender("");
    setPhone("");
  };

  /**
   * Start Screening Flow (FIXED)
   * Pass FULL patient object
   */
  const startScreening = (patient: any) => {
    router.push({
      pathname: "/screening",
      params: {
        patient_id: patient.id,
        patient_name: patient.full_name,
      },
    });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>
        {editingId ? "Update Patient" : "Add Patient"}
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Full Name"
        value={fullName}
        onChangeText={setFullName}
      />

      <TextInput
        style={styles.input}
        placeholder="Age"
        keyboardType="numeric"
        value={age}
        onChangeText={setAge}
      />

      <TextInput
        style={styles.input}
        placeholder="Gender"
        value={gender}
        onChangeText={setGender}
      />

      <TextInput
        style={styles.input}
        placeholder="Phone"
        keyboardType="phone-pad"
        value={phone}
        onChangeText={setPhone}
      />

      <TouchableOpacity
        style={styles.addButton}
        onPress={editingId ? updatePatient : addPatient}
      >
        <Text style={styles.buttonText}>
          {editingId ? "Update Patient" : "Add Patient"}
        </Text>
      </TouchableOpacity>

      <FlatList
        data={patients}
        keyExtractor={(item: any) => item.id.toString()}
        renderItem={({ item }: any) => (
          <View style={styles.card}>
            <Text style={styles.name}>{item.full_name}</Text>
            <Text>Age: {item.age}</Text>
            <Text>Gender: {item.gender}</Text>
            <Text>Phone: {item.phone}</Text>

            <View style={styles.buttonRow}>
              <TouchableOpacity
                style={styles.updateButton}
                onPress={() => editPatient(item)}
              >
                <Text style={styles.buttonText}>Edit</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.deleteButton}
                onPress={() => deletePatient(item.id)}
              >
                <Text style={styles.buttonText}>Delete</Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={styles.screeningBtn}
              onPress={() => startScreening(item)}
            >
              <Text style={styles.buttonText}>Start Screening</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#fff",
  },

  sectionTitle: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 10,
  },

  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 10,
    padding: 12,
    marginBottom: 10,
  },

  addButton: {
    backgroundColor: "#007AFF",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
    marginBottom: 20,
  },

  buttonText: {
    color: "white",
    fontWeight: "bold",
  },

  card: {
    backgroundColor: "#f2f2f2",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },

  name: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 5,
  },

  buttonRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 12,
  },

  updateButton: {
    backgroundColor: "#f39c12",
    padding: 10,
    borderRadius: 8,
    width: "48%",
    alignItems: "center",
  },

  deleteButton: {
    backgroundColor: "#e74c3c",
    padding: 10,
    borderRadius: 8,
    width: "48%",
    alignItems: "center",
  },

  screeningBtn: {
    backgroundColor: "#000",
    padding: 12,
    borderRadius: 10,
    marginTop: 12,
    alignItems: "center",
  },
});