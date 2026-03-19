import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  Alert,
  TouchableOpacity,
} from "react-native";
import { useState } from "react";
import { router } from "expo-router";
import API from "../../api/api";
import AsyncStorage from "@react-native-async-storage/async-storage";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert("Error", "Please enter email and password");
      return;
    }

    try {
      setLoading(true);

      const response = await API.post("/login", {
        email,
        password,
      });

      const token = response.data.access_token;

      // ✅ Save token
      await AsyncStorage.setItem("access_token", token);

      console.log("✅ Token saved:", token);

      Alert.alert("Success", "Login Successful");

      // ✅ Slight delay ensures token is ready before next screen
      setTimeout(() => {
        router.replace("/dashboard");
      }, 300);

    } catch (error: any) {
      console.log("❌ Login error:", error?.response?.data || error.message);
      Alert.alert("Login Failed", "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>NeuroSeek Login</Text>

      <TextInput
        placeholder="Email"
        style={styles.input}
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
      />

      <TextInput
        placeholder="Password"
        secureTextEntry
        style={styles.input}
        value={password}
        onChangeText={setPassword}
      />

      <Button
        title={loading ? "Logging in..." : "Login"}
        onPress={handleLogin}
        disabled={loading}
      />

      <TouchableOpacity
        style={styles.registerContainer}
        onPress={() => router.push("/register")}
      >
        <Text style={styles.registerText}>
          Don't have an account? Register
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    padding: 20,
  },

  title: {
    fontSize: 24,
    marginBottom: 20,
    textAlign: "center",
    fontWeight: "bold",
  },

  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    marginBottom: 15,
    borderRadius: 5,
  },

  registerContainer: {
    marginTop: 20,
    alignItems: "center",
  },

  registerText: {
    color: "#007BFF",
    fontSize: 16,
  },
});