# 🧵 AI Fabric & Material Advisor

An intelligent AI-powered system that recommends fabrics and materials based on weather conditions, festivals/occasions, and purpose/usage. Built with ML (Scikit-learn), Generative AI (Google Gemini), and a premium web interface (FastAPI).

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd d:\AIProject
pip install -r requirements.txt
```

### 2. Generate Datasets

```bash
python data/create_datasets.py
```

### 3. Preprocess & Merge Data

```bash
python ml/preprocess.py
```

### 4. Train the ML Model

```bash
python ml/train_model.py
```

### 5. (Optional) Set Gemini API Key

Get a free API key from [Google AI Studio](https://aistudio.google.com/) and update `.env`:

```
GEMINI_API_KEY=your_actual_key_here
```

> The chatbot works without a key using intelligent fallback responses.

### 6. Start the Web Application

```bash
cd d:\AIProject
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Open in Browser

Visit: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

---

## 📁 Project Structure

```
AIProject/
├── data/
│   ├── raw/                          # Generated source datasets
│   │   ├── fabric_properties.csv     # 30 fabric types with properties
│   │   ├── weather_categories.csv    # Weather → fabric mapping
│   │   ├── festival_mapping.csv      # Occasion → fabric mapping
│   │   └── purpose_mapping.csv       # Usage → fabric mapping
│   ├── processed/
│   │   └── unified_fabric_dataset.csv # Merged dataset
│   └── create_datasets.py            # Dataset generation script
│
├── ml/
│   ├── preprocess.py                 # Data cleaning & merging
│   ├── train_model.py                # Random Forest training
│   ├── recommend.py                  # Hybrid recommendation engine
│   └── models/
│       └── fabric_recommender.pkl    # Trained model artifact
│
├── api/
│   ├── main.py                       # FastAPI entry point
│   ├── routes/
│   │   ├── recommend.py              # /api/recommend endpoint
│   │   └── chat.py                   # /api/chat endpoint
│   ├── services/
│   │   ├── recommendation_service.py # ML inference service
│   │   └── chat_service.py           # Gemini AI chat service
│   └── schemas/
│       └── models.py                 # Pydantic validation models
│
├── frontend/
│   ├── index.html                    # Premium glassmorphic UI
│   ├── css/style.css                 # Design system
│   └── js/app.js                     # Frontend logic
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web UI |
| `GET` | `/api/health` | System health check |
| `GET` | `/api/options` | Get dropdown options |
| `POST` | `/api/recommend` | Get fabric recommendations |
| `POST` | `/api/chat` | Chat with AI advisor |
| `GET` | `/docs` | Interactive API docs |

### Example: Get Recommendations

```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"weather": "summer", "festival": "Wedding", "purpose": "Party"}'
```

---

## 🧠 How It Works

1. **Dataset**: Synthetic multi-source data with 30 fabric types, 5 weather conditions, 16 occasions, and 12 purposes
2. **ML Model**: Random Forest classifier trained on the unified dataset
3. **Scoring**: Context-aware suitability scoring (comfort × durability × breathability × sustainability with dynamic weights)
4. **Chatbot**: Gemini AI for natural language conversations, enriched with ML recommendation data
5. **Hybrid Engine**: Combines ML predictions with rule-based scoring for robust results

---

## 📊 Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| fabric_type | string | Name of the fabric |
| weather | string | Weather condition |
| festival | string | Festival or occasion |
| purpose | string | Usage purpose |
| comfort_level | int (1-10) | Comfort rating |
| durability | int (1-10) | Durability rating |
| breathability | int (1-10) | Breathability rating |
| sustainability_score | int (1-10) | Eco-friendliness score |
| cost_category | string | Low/Medium/High/Premium |
| suitability_score | float | Computed suitability score |

---

## 🛠️ Technologies

- **Backend**: FastAPI, Uvicorn
- **ML**: Scikit-learn (Random Forest), Pandas, NumPy
- **AI**: Google Gemini API
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Glassmorphism, Dark mode, Animated gradients

