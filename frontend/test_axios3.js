const axios = require('axios');
const FormData = require('form-data');

const api = axios.create({
  baseURL: 'http://localhost:3000',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  if (config.headers) {
    config.headers.Authorization = `Bearer abc`;
  }
  return config;
});

const fd = new FormData();
fd.append('test', '123');

console.log(api.post('/', fd, {
  headers: { 'Content-Type': undefined }
}).catch(() => {}));
