import axios from "axios";
import type { DataType } from "../components/Jobs";

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

export const fetchCvPdf = async (id?: string, cvName?: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api_v1/cv/get_pdf`, {
      params: {id, cvName},
      responseType: 'blob'
    });
    const file = new Blob([response.data], { type: 'application/pdf' });
    const fileURL = URL.createObjectURL(file);
    return fileURL;
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

export const updateCv = async (cvData: object) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/api_v1/cv/update_cv`, cvData);
    
    return response.data;
  } catch (error) {
    console.error("CV update failed", error);
    throw error;
  }
};

export const generateMark = async (data: object[]) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api_v1/cv/generate_mark`, data);
    
    return response.data;
  } catch (error) {
    console.error("Job update failed", error);
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

export const fetchGitHubData = async (id: string | undefined) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api_v1/cv/fetch_github`, {params: {id}});
    return response.data;
  } catch (error) {
    console.error("Fetch Github data failed", error);
    throw error;
  }
}

//Mailling
export const sendSelectedMail = async (data: object[]) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api_v1/email/send-cv-selected-email`, data);
    return response.data;
  } catch (error) {
    console.error("Selection email failed", error);
    throw error;
  }
};

export const sendRejectedMail = async (data: object[]) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api_v1/email/send-cv-rejection-email`, data);
    return response.data;
  } catch (error) {
    console.error("Rejection email failed", error);
    throw error;
  }
};

export const sendInterviewScheduledMail = async (data: object) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api_v1/email/send-interview-scheduled-email`, data);
    return response.data;
  } catch (error) {
    console.error("Interview scheduled email failed", error);
    throw error;
  }
};

//excel
export const exportCvsToExcel = async (cvIds: string[]) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api_v1/cv/export_cvs_to_excel`,
      { cv_ids: cvIds },
      {
        responseType: 'blob', // Important for file download
      }
    );
    
    // Create blob link to download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    // Extract filename from Content-Disposition header or use default
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'CV_Export.xlsx';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    return { success: true, message: 'Export successful' };
  } catch (error) {
    console.error("Export to Excel failed", error);
    throw error;
  }
};