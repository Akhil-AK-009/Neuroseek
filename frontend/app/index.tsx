import { View, ActivityIndicator } from "react-native";
import { useEffect } from "react";
import { router } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";

export default function Index() {

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {

      const token = await AsyncStorage.getItem("access_token");

      if (token) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }

    } catch (error) {
      router.replace("/login");
    }
  };

  return (
    <View style={{
      flex: 1,
      justifyContent: "center",
      alignItems: "center"
    }}>
      <ActivityIndicator size="large" />
    </View>
  );
}