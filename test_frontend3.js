const axios = require('axios');
axios.post('https://lunery-backend.onrender.com/api/v1/auth/login', 'username=owner%40lunery.local&password=password123', {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
}).then(res => console.log(res.data)).catch(err => {
  if (err.response) {
    console.log("ERR RESPONSE STATUS:", err.response.status);
    console.log("ERR RESPONSE DATA:", err.response.data);
  } else {
    console.log("NO RESPONSE");
  }
});
