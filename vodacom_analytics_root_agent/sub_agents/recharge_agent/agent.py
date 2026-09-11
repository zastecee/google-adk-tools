import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .tools import (
  get_grouped_recharge_month_on_month_metrics,
  get_grouped_recharge_month_to_date_total,
  get_grouped_recharge_year_on_year_metrics,
  get_kpi_month_to_date_total,
  get_recharge_month_on_month_metrics,
  get_recharge_year_on_year_metrics,
  get_total_mpesa_recharge_per_day,
  get_total_other_recharge_per_day,
  get_total_recharge_per_day,
  get_total_recharge_per_day_all_kpis,
)

load_dotenv()

recharge_agent = LlmAgent(
  name="recharge_agent",
  model=f"bedrock/converse/{os.getenv('BEDROCK_MODEL_ID')}",
  description=(
    "Agente especializado no processamento e análise de recargas (Recharge), "
    "volume de recargas diárias, canais de distribuição e comportamento de recarga dos clientes."
  ),
  instruction="""
    Você é o especialista em recargas (Recharge) da Vodacom.
    Processe dados e consultas sobre valores e volumes de recargas realizadas pelos clientes.
    """,
  tools=[
    get_total_recharge_per_day,
    get_total_other_recharge_per_day,
    get_total_mpesa_recharge_per_day,
    get_recharge_month_on_month_metrics,
    get_recharge_year_on_year_metrics,
    get_grouped_recharge_month_on_month_metrics,
    get_grouped_recharge_year_on_year_metrics,
    get_grouped_recharge_month_to_date_total,
    get_kpi_month_to_date_total,
    get_total_recharge_per_day_all_kpis,
  ],
)
