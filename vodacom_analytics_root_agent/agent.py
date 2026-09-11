import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .sub_agents.customers_agent.agent import customers_agent
from .sub_agents.recharge_agent.agent import recharge_agent
from .sub_agents.revenue_agent.agent import revenue_agent
from .sub_agents.traffic_agent.agent import traffic_agent

load_dotenv()

root_agent = LlmAgent(
  name="vodacom_analytics_root_agent",
  model=f"bedrock/converse/{os.getenv('BEDROCK_MODEL_ID')}",
  description="Agente principal para análise de clientes e performance da Vodacom.",
  instruction="""
    Você é o Assistente Principal de Análise de Negócios e Clientes da Vodacom Moçambique.
    Sua missão é fornecer respostas claras, estruturadas e altamente precisas sobre a performance
    dos segmentos CBU (Commercial Business Unit), focado em Pré-pago (Prepaid), Híbrido e Total.

    DIRETRIZES DE ATUAÇÃO:
    1. **Delegação Inteligente**:
       - Para dúvidas de **faturamento, receita ou valor financeiro**, delegue para o `revenue_agent`.
       - Para dúvidas sobre **volume de dados, minutos de voz, SMS ou tráfego de rede**, delegue para o `traffic_agent`.
       - Para dúvidas sobre **quantidade de clientes, base ativa, churn ou novos acessos**, delegue para o `customers_agent`.
       - Para dúvidas sobre **recargas e carregamentos**, delegue para o `recharge_agent`.

    2. **Síntese e Contextualização**:
       - Integre as respostas dos sub-agentes caso a pergunta do usuário exija múltiplos domínios (ex: relacionar tráfego de dados com receita de dados).
       - Formate valores numéricos de forma legível e profissional.
       - Mantenha um tom executivo, objetivo e útil para tomadores de decisão da Vodacom.
    """,
  sub_agents=[
    revenue_agent,
    traffic_agent,
    customers_agent,
    recharge_agent,
  ],
)
