# ✈️ TripBuddy-AI

### A Multi-Agent AI Travel Planner using LangGraph

TripBuddy-AI is an AI-powered travel planning application that uses a **multi-agent architecture** to create personalized travel plans.

Users can describe their trip in natural language, and TripBuddy-AI can generate:

- ✈️ Flight information
- 🏨 Hotel recommendations
- 🗺️ Day-by-day itinerary
- 💰 Budget-conscious travel planning
- 🤖 AI-generated travel recommendations
- 📄 Downloadable travel plan as a PDF

---

# 🚀 Features

## ✈️ Flight Search

TripBuddy-AI uses a flight search tool to find relevant flight information based on the user's:

- Origin
- Destination
- Travel requirements

Example:

> Plan a 5-day Dubai trip from Mumbai including flights and hotels.

---

## 🏨 Hotel Discovery

The hotel agent searches for suitable accommodation based on the destination and travel requirements.

Hotel recommendations can include:

- Hotel name
- Location
- Description
- Relevant travel information

---

## 🗺️ AI Itinerary Generation

The itinerary agent creates a personalized day-by-day travel plan.

The itinerary can include:

- Sightseeing
- Activities
- Food recommendations
- Local transportation
- Suggested daily schedules

---

## 🤖 Multi-Agent Architecture

TripBuddy-AI uses **LangGraph** to coordinate multiple specialized AI agents.

The current workflow is:

```text
                    User Request
                         │
                         ▼
                 ┌───────────────┐
                 │ Flight Agent  │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  Hotel Agent  │
                 └───────┬───────┘
                         │
                         ▼
               ┌───────────────────┐
               │ Itinerary Agent   │
               └─────────┬─────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  Final Agent  │
                 └───────┬───────┘
                         │
                         ▼
                 Travel Plan