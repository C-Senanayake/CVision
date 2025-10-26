import axios from "axios";
import type { DataType } from "../components/Jobs";
import type { CVDataType } from "../components/CV";

const API_BASE_URL = "http://localhost:8000"; // FastAPI backend URL

//CVS
export const uploadCv = async (formData: FormData) => {

  try {
    const response = await axios.post(`${API_BASE_URL}/api_v1/cv/upload_cv`, formData, {
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

export const fetchCvs = async (division?: string, jobName?: string, candidateName?: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api_v1/cv/fetch_cvs`, {
      params: {division, jobName, candidateName}
    });
    
    return response.data;
  } catch (error) {
    console.error("Add job failed", error);
    throw error;
  }
};

export const deleteCv = async (id?: string) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/api_v1/cv/delete_cv`, {
      params: {id}
    });
    
    return response.data;
  } catch (error) {
    console.error("CV delete failed", error);
    throw error;
  }
};

export const updateCv = async (cvData: CVDataType | null) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/api_v1/cv/update_cv`, cvData);
    
    return response.data;
  } catch (error) {
    console.error("CV update failed", error);
    throw error;
  }
};


//Jobs
export const addJob = async (job: any) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api_v1/job/create_job`, job);
    
    return response.data;
  } catch (error) {
    console.error("Add job failed", error);
    throw error;
  }
};

export const fetchJob = async (division?: string, jobName?: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api_v1/job/fetch_jobs`, {
      params: {division, jobName}
    });
    
    return response.data;
  } catch (error) {
    console.error("Add job failed", error);
    throw error;
  }
};

export const deleteJob = async (id?: string) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/api_v1/job/delete_job`, {
      params: {id}
    });
    
    return response.data;
  } catch (error) {
    console.error("Job delete failed", error);
    throw error;
  }
};

export const updateJob = async (jobData: DataType | null) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/api_v1/job/update_job`, jobData);
    
    return response.data;
  } catch (error) {
    console.error("Job update failed", error);
    throw error;
  }
};

export const updateJobCriteria = async (jobData: {id: string | undefined, criteria: {[k: string]: string;}}) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/api_v1/job/update_job`, jobData);
    
    return response.data;
  } catch (error) {
    console.error("Job update failed", error);
    throw error;
  }
};