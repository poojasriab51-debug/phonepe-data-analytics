# PhonePe Data Analytics Dashboard

A comprehensive Streamlit dashboard for visualizing PhonePe transaction and user data across India (2018-2024).

![Dashboard Preview](https://via.placeholder.com/800x400?text=PhonePe+Analytics+Dashboard)

## Features

- **State-wise Analysis**: Interactive maps and bar charts showing transaction distribution across Indian states
- **Transaction Types**: Pie and bar charts showing different payment categories
- **Growth Trends**: Quarterly and yearly transaction growth analysis
- **User Analysis**: Registered users and app opens by state
- **Raw Data**: Export functionality for transactions and user data

## Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Data Visualization**: Plotly
- **Database**: SQLite
- **Data Source**: PhonePe Pulse Dataset

## Installation

1. Clone the repository:
```bash
git clone https://github.com/poojasriab51-debug/phonepe-data-analytics.git
cd phonepe-data-analytics
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the dashboard:
```bash
streamlit run phonepe_dashboard.py
```

5. Open http://localhost:8501 in your browser

## Deployment to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Sign in with your GitHub account
4. Click "New app" and select your repository
5. Set the main file path as `phonepe_dashboard.py`
6. Click "Deploy"

## Project Structure

```
phonepe-data-analytics/
├── phonepe_dashboard.py       # Main Streamlit dashboard
├── phonepe_analysis.py        # Data analysis scripts
├── phonepe_sql_setup.py       # Database setup
├── phonepe_comprehensive_analysis.py  # Advanced analysis
├── phonepe_transactions.csv   # Sample data
├── phonepe_analysis.db       # SQLite database
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── pulse/                    # PhonePe Pulse data (optional)
```

## License

This project uses data from [PhonePe Pulse](https://github.com/PhonePe/pulse) which is licensed under CDLA-Permissive-2.0.

## Author

Pooja Sria

## Acknowledgments

- [PhonePe Pulse](https://www.phonepe.com/pulse/) for the dataset
- [Streamlit](https://streamlit.io/) for the amazing dashboard framework

