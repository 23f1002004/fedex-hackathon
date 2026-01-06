# FedEx SMART Hackathon – Intelligent DCA Management Platform

## Overview
This project presents a centralized, data-driven platform to manage Debt Collection Agencies (DCAs) more efficiently. The system replaces manual Excel- and email-based workflows with automated case allocation, SLA monitoring, and performance analytics.

## Key Features
- Case priority scoring based on overdue days and amount
- Dynamic DCA scoring and allocation
- SLA monitoring and penalty handling
- Anti-cheating verification workflow
- FedEx and DCA role-based dashboards

## Model & Decision Logic
The current prototype uses explainable, rule-based scoring models:
- Case Priority Model
- DCA Performance Scoring Model

The architecture is AI-ready and can incorporate ML models once historical data is available.

## Tech Stack
- Backend: Flask (Python)
- Frontend: HTML, CSS
- Data: In-memory mock data
- Visualization: Tables (charts planned)

## How to Run
1. pip install -r requirements.txt
2. python app.py
3. Open http://127.0.0.1:5000

## Note
This is a hackathon prototype focused on design correctness, explainability, and scalability.
