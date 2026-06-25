# AI Interview Coach
# 🤖 AI Interview Coach

An AI-powered Interview Coach built with **Python**, **Flask**, and **Google Gemini API** that helps users prepare for job interviews through AI-generated questions, answer evaluation, detailed feedback, and performance reports.

---

## 📌 Features

- 🎯 AI-generated interview questions based on the selected job role
- 📝 Resume and Job Description based interview customization
- 📊 AI evaluation of every answer
- ⭐ Score and personalized feedback
- 📄 Interview report generation
- 📈 Dashboard to view previous interview reports
- 🌐 Clean and responsive web interface

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### AI
- Google Gemini API

### Other Libraries
- python-dotenv

---

## 📂 Project Structure

```
ai-coach/
│
├── app.py                      # Main Flask application
├── interview_engine.py         # Interview session management
├── gemini_service.py           # Gemini API integration
├── report_generator.py         # Report generation
├── utils.py                    # Utility functions
├── requirements.txt
├── .env
│
├── templates/
│   ├── index.html
│   ├── setup.html
│   ├── interview.html
│   ├── feedback.html
│   ├── report.html
│   └── dashboard.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
│
└── data/
    └── Generated interview reports
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-coach.git
```

### 2. Move into the project

```bash
cd ai-coach
```

### 3. Create a virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configure Gemini API

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
SECRET_KEY=your_secret_key
```

Replace `YOUR_GEMINI_API_KEY` with your Google Gemini API key.

---

## ▶️ Run the Application

```bash
python app.py
```

Open your browser and visit

```
http://127.0.0.1:5000
```

---

## 💻 How It Works

1. Enter the job role.
2. Add the job description (optional).
3. Paste your resume (optional).
4. Select the interview difficulty.
5. Choose the number of questions.
6. Start the interview.
7. Answer each AI-generated question.
8. Receive AI-generated feedback and scores.
9. View the complete interview report on the dashboard.

---

## 📷 Screens

- Home Page
- Interview Setup
- AI Interview
- Feedback Page
- Report Page
- Dashboard

*(Add screenshots here if available.)*

---

## 📦 Dependencies

- Flask
- google-generativeai
- python-dotenv

Install them using:

```bash
pip install -r requirements.txt
```

---

## 🎯 Future Improvements

- Voice-based interviews
- Speech-to-text answer recording
- Timer for each question
- PDF report download
- User authentication
- Performance analytics
- Multiple AI model support
- Dark mode

---

## 👨‍💻 Author

**Priyansh Verma**

MCA (Generative AI) Student  
Alliance University, Bengaluru

GitHub: https://github.com/yourusername

---

## 📄 License

This project is intended for educational and learning purposes.
