import { useState } from "react";
import { View, Text, TextInput, Button, Alert } from "react-native";
import { router } from "expo-router";
import api from "../../api/api";

export default function Register() {

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async () => {
    try {

      await api.post("/register", {
        name,
        email,
        password
      });

      Alert.alert("Success", "Account created");

      router.replace("/login");

    } catch (error: any) {
      Alert.alert("Error", "Registration failed");
    }
  };

  return (
    <View style={{ padding: 20 }}>

      <Text style={{ fontSize: 24, marginBottom: 20 }}>
        Register
      </Text>

      <TextInput
        placeholder="Name"
        value={name}
        onChangeText={setName}
        style={{ borderWidth: 1, marginBottom: 10, padding: 10 }}
      />

      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        style={{ borderWidth: 1, marginBottom: 10, padding: 10 }}
      />

      <TextInput
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        style={{ borderWidth: 1, marginBottom: 20, padding: 10 }}
      />

      <Button title="Register" onPress={handleRegister} />

    </View>
  );
}