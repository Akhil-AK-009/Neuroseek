import { View, Text, TextInput, Button, StyleSheet, Alert, TouchableOpacity } from "react-native";
import { useState } from "react";
import { router } from "expo-router";
import API from "../../api/api";
import AsyncStorage from "@react-native-async-storage/async-storage";

export default function Login() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {

    if (!email || !password) {
      Alert.alert("Error", "Please enter email and password");
      return;
    }

    try {

      const response = await API.post("/login", {
        email: email,
        password: password,
      });

      console.log("Backend response:", response.data);

      const token = response.data.access_token;

      // Save token locally
      await AsyncStorage.setItem("token", token);

      Alert.alert("Success", "Login Successful");

      // Navigate to dashboard
      router.replace("/dashboard");

    } catch (error) {

      console.log("Login error:", error);
      Alert.alert("Login Failed", "Invalid email or password");

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

      <Button title="Login" onPress={handleLogin} />

      {/* Register Link */}

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
    fontWeight: "bold"
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
    alignItems: "center"
  },

  registerText: {
    color: "#007BFF",
    fontSize: 16
  }

});