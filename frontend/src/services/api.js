import axios from 'axios';
import { API_BASE_URL } from '../config';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const telemetryAPI = {
  submit: (data) => api.post('/telemetry/', data),
  bulkSubmit: (data) => api.post('/telemetry/bulk/', data),
};

export const parkingAPI = {
  submitLog: (data) => api.post('/parking-log/', data),
};

export const dashboardAPI = {
  getSummary: (date) => api.get('/dashboard/summary/', { params: { date } }),
};

export const alertAPI = {
  getAlerts: (params) => api.get('/alerts/', { params }),
  acknowledge: (id) => api.patch(`/alerts/${id}/acknowledge/`),
};

export default api;