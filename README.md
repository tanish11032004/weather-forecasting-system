# Weather Forecasting System using Machine Learning

## 📌 Project Overview
The **Weather Forecasting System** is a machine learning-based application that predicts weather conditions based on historical data. It provides users with accurate weather forecasts while allowing admin interaction through a dedicated support page. The system is built using **Django, scikit-learn, HTML, CSS, JavaScript, and SQLite**.

## 🚀 Features
- **Weather Prediction:** Provides temperature, humidity, and precipitation forecasts.
- **User & Admin Interface:** A user-friendly interface for checking forecasts and admin functionalities.
- **Machine Learning Integration:** Uses **scikit-learn** for predictive analytics.
- **Database Management:** Stores user queries and forecast data in **SQLite**.
- **Help Center & Support Page:** Interactive pages for user queries and assistance.

## 🛠️ Technologies Used
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Django
- **Machine Learning:** scikit-learn
- **Database:** SQLite

## 📂 Project Structure
```
Weather-Forecasting-System/
│-- static/            # Static files (CSS, JS, images)
│-- templates/         # HTML templates
│-- weather_forecast/  # Main Django app
│   ├── models.py      # Database models
│   ├── views.py       # Application logic
│   ├── urls.py        # URL routing
│   ├── forms.py       # Forms for user inputs
│-- db.sqlite3         # SQLite Database
│-- manage.py          # Django project manager
│-- requirements.txt   # Required Python libraries
│-- README.md          # Project documentation
```

## 📦 Installation & Setup
### Step 1: Set Up the Environment
1. **Ensure Python is Installed:**
   - Download and install Python from [python.org](https://www.python.org/downloads/).
   - Verify installation:
     ```bash
     python --version
     ```
2. **Install Virtual Environment (if not installed):**
   ```bash
   pip install virtualenv
   ```
3. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```
4. **Activate the Virtual Environment:**
   ```bash
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

### Step 2: Clone and Set Up the Project
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/weather-forecasting-system.git
   cd weather-forecasting-system
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```
4. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
5. **Open the Application:**
   Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## 📊 Machine Learning Model
- **Dataset:** Historical weather data is preprocessed and used to train the model.
- **Algorithm:** Uses **scikit-learn** regression/classification models to predict temperature, humidity, and weather conditions.
- **Model Training:** The model is trained using past climate data and evaluated using various metrics like **R² Score and Mean Squared Error (MSE)**.

## 🛠 Future Improvements
- Integrate **real-time API** for live weather updates.
- Improve **model accuracy** with advanced algorithms.
- Add **user authentication** and profile management.
- Enhance **UI/UX** for better usability.

## 🤝 Contributing
1. Fork the repository.
2. Create a new branch (`feature-name`).
3. Commit your changes.
4. Push to the branch and create a **Pull Request**.

## 📄 License
This project is licensed under the **MIT License**.

## 📩 Contact
For any queries or contributions, reach out via:
- 📧 Email: mehtatanish443@gmail.com
- 🔗 GitHub: tanish11032004
