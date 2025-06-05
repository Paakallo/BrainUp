# 🧠 EEG Signal Visualizer

A web application for interactive visualization and analysis of EEG signals. It allows users to select channels, filter brainwave frequencies (alpha, beta, theta, delta), and manipulate the plot in real time.

---

## 👨‍💻 Authors

Sergiusz Pyskowacki, Filip Jaworski

---

## ⚡ Project Overview

The goal of the project is to enable fast and intuitive EEG data analysis through a browser-based application built with Dash (or FastAPI as an alternative). The user can filter brainwaves, select EEG channels, and explore signals through a convenient interface.

---

## 📘 Project Description

The application allows:
- loading EEG files in various formats (`.edf`, `.xdf`, `.csv`, `.xsl`),
- selecting EEG channels for display,
- filtering data by frequency bands (e.g., alpha, beta waves),
- interactive zooming and panning of the plot,
- browsing data through a web interface,
- generating a 2D topographic map,
- downloading a file with extracted brainwave data.

---

## 🎯 Goals and Assumptions

- Clear visualization of EEG data  
- Interactive plot with zoom and pan capabilities  
- Support for multiple EEG channels  
- Filtering brainwaves by frequency bands  

---

## 🧩 Features

✅ EEG data import  
✅ Dynamic channel selection  
✅ Frequency band filtering:  
   - Delta (0.5–4 Hz)  
   - Theta (4–8 Hz)  
   - Alpha (8–13 Hz)  
   - Beta (13–30 Hz)  
✅ Interactive plot (zoom, pan, reset)  
✅ Intuitive web interface  
✅ Generation of a 2D topographic map  
✅ Downloading brainwave data as a file  

---

## 🛠️ Technologies Used

**Frontend:**  
- Dash  
- Matplotlib  

**Backend:**  
- Pandas  
- NumPy  
- MNE  

---

## 🚀 How to Run the Project

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd BrainUp
   python app.py
