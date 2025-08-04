import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api", // FastAPI 后端地址
  timeout: 1000000, // 超时时间
});

export default apiClient;
