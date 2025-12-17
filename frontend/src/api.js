import axios from "axios";

const api = axios.create({
  // baseURL removed to allow Vite proxy to handle requests relative to current origin
});

export default api;
