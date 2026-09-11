from google.adk.agents import LlmAgent

# ==============================================================================
# 1. SPECIALIZED SUB-AGENTS
# ==============================================================================

# ------------------------------------------------------------------------------
# Revenue Sub-Agent
# ------------------------------------------------------------------------------
revenue_agent = LlmAgent(
  name="revenue_agent",
  model="gemini-2.5-flash",
  description=(
    "Specialized agent for processing and analyzing revenue metrics, "
    "including daily views, Month-to-Date (MTD), Month-on-Month (MoM), "
    "and Year-on-Year (YoY) performance for CBU segments and KPIs such as "
    "Voice, Data, SMS, Airtime Advance, and Interconnect."
  ),
  instruction="""
    You are Vodacom's technical specialist for Revenue metrics.
    Your sole responsibility is to query, process, and calculate financial and revenue data.
    - Always select the appropriate tool based on the KPI and billing type (prepaid, hybrid, total).
    - Return clean, well-structured information without introducing unverified assumptions.
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
  ],
)

# ------------------------------------------------------------------------------
# Traffic Sub-Agent
# ------------------------------------------------------------------------------
traffic_agent = LlmAgent(
  name="traffic_agent",
  model="gemini-2.5-flash",
  description=(
    "Specialized agent for processing and analyzing network traffic volumes, "
    "including voice (billed/unbilled), SMS, data, inflows, and outflows."
  ),
  instruction="""
    You are Vodacom's technical specialist for Network Traffic metrics.
    Your responsibility is to handle inquiries regarding network usage volume across
    different timeframes (daily, MTD, MoM, and YoY).
    - Ensure clear differentiation between Billed and Unbilled traffic when requested.
    - Return all traffic volume metrics with high accuracy.
    """,
  tools=[
    get_total_traffic_per_day,
    get_kpi_month_to_date_total,
    get_traffic_month_on_month_metrics,
    get_traffic_year_on_year_metrics,
  ],
)

# ------------------------------------------------------------------------------
# Customers Sub-Agent
# ------------------------------------------------------------------------------
customers_agent = LlmAgent(
  name="customers_agent",
  model="gemini-2.5-flash",
  description=(
    "Specialized agent for analyzing customer base metrics, "
    "including active subscriber counts (1D, 30D, 90D), Gross Adds, "
    "churn rates, and Prepaid CBU customer behavior."
  ),
  instruction="""
    You are Vodacom's customer base (Customers) specialist.
    Process queries and metrics related to subscriber counts, new additions, churn, and base evolution.
    """,
  tools=[
    # Place customer sub-agent tools here
  ],
)

# ------------------------------------------------------------------------------
# Recharge Sub-Agent
# ------------------------------------------------------------------------------
recharge_agent = LlmAgent(
  name="recharge_agent",
  model="gemini-2.5-flash",
  description=(
    "Specialized agent for processing and analyzing recharge performance, "
    "daily recharge volumes, distribution channels, and customer top-up patterns."
  ),
  instruction="""
    You are Vodacom's recharge (Recharge) specialist.
    Process queries regarding recharge values, volumes, and top-up behaviors.
    """,
  tools=[
    # Place recharge sub-agent tools here
  ],
)


# ==============================================================================
# 2. ROOT AGENT (MAIN ORCHESTRATOR)
# ==============================================================================

root_agent = LlmAgent(
  name="vodacom_analytics_root_agent",
  model="gemini-2.5-pro",
  description="Main orchestrator agent for Vodacom customer business unit analytics.",
  instruction="""
    You are the Lead Business and Customer Analytics Assistant for Vodacom Mozambique.
    Your mission is to provide clear, structured, and precise insights regarding the 
    performance of CBU (Commercial Business Unit) segments—focusing on Prepaid, Hybrid, and Total.

    OPERATIONAL DIRECTIVES:
    1. **Intelligent Delegation**:
       - Route queries regarding **billing, financial revenue, or monetary value** to the `revenue_agent`.
       - Route queries regarding **data volume, voice minutes, SMS counts, or network traffic** to the `traffic_agent`.
       - Route queries regarding **subscriber counts, active base, churn, or new activations** to the `customers_agent`.
       - Route queries regarding **top-ups, recharge counts, or recharge volumes** to the `recharge_agent`.

    2. **Synthesis and Contextualization**:
       - Synthesize outputs from multiple sub-agents when user requests span across domains (e.g., correlating data traffic volume with data revenue).
       - Format numerical figures clearly using standard digit grouping.
       - Maintain an executive, objective, and action-oriented tone suited for Vodacom decision-makers.
    """,
  sub_agents=[
    revenue_agent,
    traffic_agent,
    customers_agent,
    recharge_agent,
  ],
)
