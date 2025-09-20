import axios from "axios";

const API_BASE_URL = "http://localhost:8000"; // FastAPI backend URL

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${API_BASE_URL}/api_v1/pdf/upload_file`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Upload failed", error);
    throw error;
  }
};