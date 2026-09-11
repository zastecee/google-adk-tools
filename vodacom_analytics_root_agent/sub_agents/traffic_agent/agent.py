import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .tools import (
  get_kpi_month_to_date_total,
  get_total_traffic_per_day,
  get_traffic_month_on_month_metrics,
  get_traffic_year_on_year_metrics,
)

load_dotenv()

traffic_agent = LlmAgent(
  name="traffic_agent",
  model=f"bedrock/converse/{os.getenv('BEDROCK_MODEL_ID')}",
  description=(
    "Agente especializado no processamento e análise de volumes e tráfego de rede (Traffic), "
    "incluindo voz (faturado/não faturado), SMS, dados, Inflows e Outflows."
  ),
  instruction="""
    Você é o assistente técnico de tráfego de rede (Traffic) da Vodacom.
    Sua responsabilidade é responder a dúvidas sobre volume de uso da rede em diferentes
    períodos (diário, MTD, MoM e YoY).
    - Certifique-se de diferenciar tráfego Billed de Unbilled quando solicitado.
    - Retorne as métricas com precisão técnica.
    """,
  tools=[
    get_total_traffic_per_day,
    get_kpi_month_to_date_total,
    get_traffic_month_on_month_metrics,
    get_traffic_year_on_year_metrics,
  ],
)
