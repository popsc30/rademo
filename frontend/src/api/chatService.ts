import axios from "axios";

const API_URL = "http://localhost:8002";

export const query = async (message: string) => {
  try {
    const response = await axios.post(`${API_URL}/query`, { query: message });
    return response.data.answer?.[0];
  } catch (error) {
    console.error("Error querying API:", error);
    throw new Error("Failed to get response from API");
  }
};

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${API_URL}/upload`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data.message;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw new Error("File upload failed");
  }
};
