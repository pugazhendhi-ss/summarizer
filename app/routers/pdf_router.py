from fastapi import APIRouter, UploadFile, File, Depends
from fastapi import Form
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Literal
from app.services.llm_service import LLMService
from app.services.pdf_service import PDFService
from app.services.vector_service import VectorService


def get_pdf_service():
    return PDFService()


def get_llm_service():
    return LLMService()

def get_vector_service():
    return VectorService()


pdf_router = APIRouter()

test_txt = """
### Commodity-Specific Analysis

#### 1. Beef Production Analysis
In the second quarter of 2025, U.S. beef production is projected at 6.54 million pounds, a decrease from the previous quarter's 6.78 million pounds. The annual production estimate for 2025 has been adjusted to 26.36 million pounds, down from 26.42 million pounds projected in May. Factors contributing to this decline include reduced cattle inventories and higher feed costs. The beef production forecast for 2026 is further reduced to 25.28 million pounds, reflecting ongoing challenges in the cattle sector.

#### 2. Pork Production Analysis
Pork production for the second quarter of 2025 is projected at 6.76 million pounds, slightly lower than the previous quarter's 6.88 million pounds. The annual estimate remains unchanged at 27.99 million pounds. The pork sector is experiencing stable demand, but production growth is constrained by feed prices and labor shortages. For 2026, pork production is expected to remain stable at 28.37 million pounds.

#### 3. Poultry Production Analysis
Total poultry production is projected at 13.31 million pounds for the second quarter of 2025, with broiler production at 13.31 million pounds and turkey production at 11.81 million pounds. The annual projection for total poultry production is 54.52 million pounds, slightly down from previous estimates. The poultry sector is facing challenges from avian influenza outbreaks, which have impacted production levels. For 2026, total poultry production is expected to increase to 53.80 million pounds.

#### 4. Egg Production Analysis
Egg production is projected at 1.19 billion dozen for the second quarter of 2025, a slight increase from the previous quarter. The annual estimate for 2025 is adjusted to 8.65 billion dozen, reflecting a recovery from earlier production declines due to avian influenza. For 2026, production is expected to rise to 9.18 billion dozen, driven by improved flock health and increased demand.

#### 5. Milk Production Analysis
U.S. milk production is projected at 57.0 billion pounds for the second quarter of 2025, with an annual estimate of 227.8 billion pounds. The dairy sector is benefiting from strong domestic demand and export opportunities, particularly for cheese and butter. The forecast for 2026 indicates a slight increase to 228.2 billion pounds, supported by improved feed availability and herd management practices.

### Supply Situation

#### Beef Supply
Beginning stocks for beef are projected at 602 million pounds, with total supply at 32.21 billion pounds. Exports are expected to reach 2.71 billion pounds, leading to ending stocks of 570 million pounds. The stocks-to-use ratio is projected at 1.98%, indicating a tight supply situation.

#### Pork Supply
Pork's beginning stocks are estimated at 435 million pounds, with total supply at 29.55 billion pounds. Exports are projected at 6.95 billion pounds, resulting in ending stocks of 425 million pounds. The stocks-to-use ratio stands at 1.92%, reflecting a balanced supply-demand scenario.

#### Poultry Supply
Total poultry supply is estimated at 53.55 billion pounds, with exports at 7.02 billion pounds and ending stocks at 975 million pounds. The stocks-to-use ratio is projected at 1.82%, indicating a stable supply situation.

#### Egg Supply
Egg supply is projected at 8.79 billion dozen, with exports at 187.2 million dozen and ending stocks at 18 million dozen. The stocks-to-use ratio is 2.35%, suggesting a healthy supply balance.

#### Milk Supply
Milk supply is projected at 248.5 billion pounds, with exports at 13.6 billion pounds and ending stocks at 12.1 billion pounds. The stocks-to-use ratio is 4.86%, indicating a comfortable supply situation.

### Demand Dynamics

#### Beef Demand
Domestic consumption of beef is projected at 28.94 billion pounds, with strong demand from both retail and foodservice sectors. Export demand remains robust, particularly in Asian markets.

#### Pork Demand
Pork consumption is projected at 22.18 billion pounds, driven by stable domestic demand and strong export markets, particularly in Mexico and Asia.

#### Poultry Demand
Total poultry use is projected at 45.55 billion pounds, with increasing demand for both broilers and turkeys. Export demand is also strong, particularly in the Middle East and Asia.

#### Egg Demand
Egg disappearance is projected at 7.42 billion dozen, with strong demand for both retail and foodservice applications.

#### Milk Demand
Domestic use of milk is projected at 222.8 billion pounds, with strong demand for cheese and butter driving overall consumption.

### Stock Levels

#### Beef Stocks
Ending stocks for beef are projected at 570 million pounds, with a stocks-to-use ratio of 1.98%. This indicates a tight supply situation, which may support higher prices.

#### Pork Stocks
Ending stocks for pork are projected at 425 million pounds, with a stocks-to-use ratio of 1.92%. This suggests a balanced supply-demand scenario.

#### Poultry Stocks
Ending stocks for poultry are projected at 975 million pounds, with a stocks-to-use ratio of 1.82%. This indicates a stable supply situation.

#### Egg Stocks
Ending stocks for eggs are projected at 18 million dozen, with a stocks-to-use ratio of 2.35%, suggesting a healthy supply balance.

#### Milk Stocks
Ending stocks for milk are projected at 12.1 billion pounds, with a stocks-to-use ratio of 4.86%, indicating a comfortable supply situation.

### Trade Flows

#### Beef Trade
Beef exports are projected at 2.71 billion pounds, with key destinations including Japan, South Korea, and Mexico. Import requirements are stable, with limited competition from other countries.

#### Pork Trade
Pork exports are projected at 6.95 billion pounds, with strong demand from Mexico and Asia. Import requirements are minimal, as the U.S. maintains a competitive position in the global market.

#### Poultry Trade
Poultry exports are projected at 7.02 billion pounds, with key markets in the Middle East and Asia. Import requirements are limited, as domestic production meets most demand.

#### Egg Trade
Egg exports are projected at 187.2 million dozen, with demand from Canada and Mexico. Import requirements are minimal.

#### Milk Trade
Milk exports are projected at 13.6 billion pounds, with strong demand from Mexico and Southeast Asia. Import requirements are stable, with limited competition.

### Market Overview Section

#### Supply and Demand Changes
The overall supply and demand landscape for animal products shows a mixed picture, with beef and poultry facing tighter supplies, while pork and milk remain stable. The ongoing impacts of feed costs and labor shortages are influencing production levels across the board.

#### Price Trends
Season-average prices for beef are projected to rise, reflecting tighter supplies. Pork prices are expected to remain stable, while poultry prices may experience slight increases due to strong demand. Milk prices are projected to remain stable, supported by robust domestic and export demand.

#### Market Outlook and Forecasts
The outlook for the animal products market remains cautiously optimistic, with demand expected to remain strong. However, uncertainties related to feed costs, labor availability, and potential disease outbreaks could impact production levels and market dynamics moving forward. The global market dynamics, including trade policies and competition from other exporting countries, will also play a crucial role in shaping future trends.
"""


@pdf_router.post("/upload-pdf")
async def upload_and_summarize(
        file: UploadFile = File(...),
        operation: Literal["summarize", "chat"] = Form("chat"),
        pdf_service: PDFService = Depends(get_pdf_service),
):
    try:
        result = pdf_service.process_pdf(file)
        print(operation)
        if result.status == "success":
            if operation == "summarize":
                llm_service = get_llm_service()
                llm_response = await llm_service.summarize_nudge(result.pdf_filename)
                return llm_response
            vector_service = get_vector_service()
            vector_response = vector_service.vectorize_nudge(result)
            return vector_response
        else:
            return result

    except Exception as e:
        print(e)

    # return {"summary": test_txt,
    #         "status": "success"}


