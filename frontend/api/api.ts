import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

const BASE_URL = "http://10.188.206.246:8000";

const API = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
});

// Attach token to every request
API.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    console.log("REQUEST:", config.url, "TOKEN:", token);

    return config;
  },
  (error) => Promise.reject(error)
);

// Handle responses
API.interceptors.response.use(
  (response) => {
    console.log("RESPONSE:", response.config.url);
    return response;
  },
  async (error) => {
    console.log("API ERROR:", error?.response?.data || error.message);

    if (error.response?.status === 401) {
      console.log("Unauthorized - Token issue");
    }

    return Promise.reject(error);
  }
);

export default API;