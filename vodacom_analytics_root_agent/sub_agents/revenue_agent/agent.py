import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .tools import (
  generate_dashboard,
  get_cbu_prepaid_month_to_date_total,
  get_cbu_prepaid_revenue_month_on_month_metrics,
  get_cbu_prepaid_revenue_per_day,
  get_cbu_prepaid_revenue_per_day_including_interconnect,
  get_cbu_prepaid_revenue_year_on_year_metrics,
  get_kpi_month_to_date_total,
  get_mpesa_revenue_per_day,
  get_revenue_month_on_month_metrics,
  get_revenue_year_on_year_metrics,
  get_total_revenue_per_day,
  get_total_service_revenue_per_day,
)

load_dotenv()

revenue_agent = LlmAgent(
  name="revenue_agent",
  model=f"bedrock/converse/{os.getenv('BEDROCK_MODEL_ID')}",
  description=(
    "Agente especializado no processamento e análise de métricas de receita (Revenue), "
    "incluindo visão diária, Month-to-Date (MTD), Month-on-Month (MoM) e Year-on-Year (YoY) "
    "para segmentos CBU e KPIs como Voice, Data, SMS, Airtime Advance e Interconnect."
  ),
  instruction="""
    Você é o assistente técnico de métricas de Receita (Revenue) da Vodacom.
    Sua única responsabilidade é consultar, processar e calcular dados financeiros e de receita.
    - Sempre selecione a ferramenta apropriada com base no KPI e no tipo de faturamento (prepaid, hybrid, total).
    - Retorne as informações de forma limpa e estruturada.
    """,
  tools=[
    get_total_revenue_per_day,
    get_cbu_prepaid_revenue_per_day,
    get_cbu_prepaid_revenue_per_day_including_interconnect,
    get_kpi_month_to_date_total,
    get_revenue_month_on_month_metrics,
    get_revenue_year_on_year_metrics,
    get_cbu_prepaid_month_to_date_total,
    get_cbu_prepaid_revenue_month_on_month_metrics,
    get_cbu_prepaid_revenue_year_on_year_metrics,
    get_total_service_revenue_per_day,
    get_mpesa_revenue_per_day,
    generate_dashboard,
  ],
)
