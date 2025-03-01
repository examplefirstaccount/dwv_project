# Weather Data Visualization Project

## Overview
This project visualizes historical and current weather data using interactive maps and charts.  
It uses **Flask** as the backend and **D3.js, Leaflet.js, and Chart.js** for data visualization.

## Tech Stack
- Backend: **Flask, requests**
- Frontend: **HTML, CSS, JavaScript (D3.js, Leaflet.js, Chart.js)**
- Data Processing: **Pandas, NumPy**
- Deployment: **Flask Dev Server on locahost (stopgap)**

---

## Installation and Local Deployment

**1. Clone the Repository**
```sh
git clone https://github.com/examplefirstaccount/dwv_project.git
cd dwv_project
```

**2. Set Up a Virtual Environment**
```sh
cd backend
python -m venv venv
source venv/bin/activate   # For MacOS/Linux
venv\Scripts\activate      # For Windows
pip install -r requirements.txt
```

**3. Start the Flask Server**
```sh
python app.py
```
By default, the Flask API will be available at:  
📍 **http://127.0.0.1:5000/**

**4. Accessing the Frontend**
- Simply open the file: `frontend/index.html` in your browser.
- Or run a Simple HTTP Server
```sh
cd ../frontend
python -m http.server 8080
```
Then, open:
📍 **http://localhost:8080/** in your browser.
