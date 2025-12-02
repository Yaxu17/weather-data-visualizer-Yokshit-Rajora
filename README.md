# Weather Data Visualizer – Yokshit

This project is a Python-based weather data analysis and visualization tool created as part of the **Programming for Problem Solving using Python** mini project.

## 📌 Features
- Load real-world weather dataset (CSV)
- Clean missing values and convert dates
- Compute daily, monthly, and yearly statistics
- Create visual charts:
  - Line chart (temperature)
  - Bar chart (rainfall)
  - Scatter plot (humidity vs temperature)
  - Combined figure
- Grouping by seasons & monthly aggregation
- Export cleaned dataset and PNG plots
- Generate summary report

## 📂 Folder Structure

weather-data-visualizer-Yokshit/
│── data/
│   ├── raw_weather.csv
│   └── cleaned_weather.csv
│
│── images/
│   ├── daily_temperature.png
│   ├── monthly_rainfall.png
│   ├── humidity_vs_temperature.png
│   └── combined_plots.png
│
│── src/
│   └── weather_analysis.py
│
│── reports/
│   └── summary_report.md
│
│── README.md
│── requirements.txt


## 🛠 Tools Used
- Python  
- Pandas  
- NumPy  
- Matplotlib  
- Jupyter Notebook (optional)

## 📊 Dataset Description
The dataset contains:
- Date  
- Temperature  
- Rainfall  
- Humidity  

## 🚀 How to Run

cd src
python weather_analysis.py

## Outputs will be saved into:
- `data/cleaned_weather.csv`
- `images/*.png`
- `reports/summary_report.md`

## 👩‍🏫 Course Information
Mini Project: Weather Data Visualizer  
Weightage: 15%  
Submitted to: Jyoti Yadav  
