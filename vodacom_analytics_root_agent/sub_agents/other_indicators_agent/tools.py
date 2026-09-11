import csv
import json
import os
from datetime import UTC, datetime
from typing import Literal

# Load the customers dataset from a CSV file
_dir = os.path.dirname(os.path.abspath(__file__))
_datasets_dir = os.path.join(_dir, "..", "..", "..", "datasets")
with open(
  os.path.join(_datasets_dir, "customers_dataset.csv"),
  mode="r",
  encoding="iso-8859-1",
  newline="",
) as file:
  customer_records = list(csv.DictReader(file))


# Load the revenue dataset from a CSV file
_dir = os.path.dirname(os.path.abspath(__file__))
_datasets_dir = os.path.join(_dir, "..", "..", "..", "datasets")
with open(
  os.path.join(_datasets_dir, "revenue_dataset.csv"),
  mode="r",
  encoding="iso-8859-1",
  newline="",
) as file:
  revenue_records = list(csv.DictReader(file))

# Load the traffic dataset from a CSV file
_dir = os.path.dirname(os.path.abspath(__file__))
_datasets_dir = os.path.join(_dir, "..", "..", "..", "datasets")
with open(
  os.path.join(_datasets_dir, "traffic_dataset.csv"),
  mode="r",
  encoding="iso-8859-1",
  newline="",
) as file:
  traffic_records = list(csv.DictReader(file))

BillingType = Literal["prepaid", "hybrid", "total"]


GSM_REVENUE_KPIS = [
  "Voice",
  "Data",
  "Sms",
  "Airtime Advance",
  "Others",
]


VOICE_TRAFFIC_KPIS = [
  "Voice Traffic - Billed",
  "Voice Traffic - Free",
  "Voice Traffic - OOB",
]

DATA_TRAFFIC_KPIS = [
  "Data Traffic - Billed",
  "Data Traffic - Free",
  "Data Traffic - OOB",
]

REVENUE_BILLING_MAP = {
  "prepaid": "DR_PREPAID",
  "hybrid": "DR_HYBRID",
  "total": "DR_TOTAL",
}

CUSTOMER_BILLING_MAP = {
  "prepaid": "DC_PREPAD",
  "hybrid": "DC_HYBRID",
  "total": "DC_TOTAL",
}

TRAFFIC_BILLING_MAP = {
  "prepaid": "DC_PREPAD",
  "hybrid": "DC_HYBRID",
  "total": "DC_TOTAL",
}


# average revenue per user (ARPU) for GSM, data, voice, sms, airtime advance and other services
def get_arpu_gsm(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  try:
    revenue_target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)
    customer_target_column = CUSTOMER_BILLING_MAP.get(
      billing_type.lower(), billing_type
    )

    total_revenue = sum(
      float(item[revenue_target_column])
      for item in revenue_records
      if item.get("SERVICE_NAME") in GSM_REVENUE_KPIS and item.get("OC_DATE") == date
    )

    total_customers = sum(
      int(item[customer_target_column])
      for item in customer_records
      if item.get("EVENT_DESCRIPTION") == "Active GSM" and item.get("DC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "total_revenue": total_revenue,
      "arpu_gsm": f"{round(total_revenue / total_customers, 2):,}"
      if total_customers
      else None,
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_arpu_gsm failed: {e}"}


# average revenue per user (ARPU) for data services
def get_arpu_data(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  try:
    revenue_target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)
    customer_target_column = CUSTOMER_BILLING_MAP.get(
      billing_type.lower(), billing_type
    )

    total_revenue = sum(
      float(item[revenue_target_column])
      for item in revenue_records
      if item.get("SERVICE_NAME") == "Data" and item.get("OC_DATE") == date
    )

    total_customers = sum(
      int(item[customer_target_column])
      for item in customer_records
      if item.get("EVENT_DESCRIPTION") == "Data Users" and item.get("DC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "arpu_data": f"{round(total_revenue / total_customers, 2):,}"
      if total_customers
      else None,
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_arpu_data failed: {e}"}


# average revenue per user (ARPU) for voice services
def get_arpu_voice(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  try:
    revenue_target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)
    customer_target_column = CUSTOMER_BILLING_MAP.get(
      billing_type.lower(), billing_type
    )

    total_revenue = sum(
      float(item[revenue_target_column])
      for item in revenue_records
      if item.get("SERVICE_NAME") == "Voice" and item.get("OC_DATE") == date
    )

    total_customers = sum(
      int(item[customer_target_column])
      for item in customer_records
      if item.get("EVENT_DESCRIPTION") == "Voice Users" and item.get("DC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "arpu_voice": f"{round(total_revenue / total_customers, 2):,}"
      if total_customers
      else None,
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_arpu_voice failed: {e}"}


# Price per minute
def get_ppm(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  try:
    revenue_target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)
    traffic_target_column = TRAFFIC_BILLING_MAP.get(billing_type.lower(), billing_type)

    voice_revenue = sum(
      float(item[revenue_target_column])
      for item in revenue_records
      if item.get("SERVICE_NAME") == "Voice" and item.get("OC_DATE") == date
    )

    total_traffic = sum(
      float(item[traffic_target_column])
      for item in traffic_records
      if item.get("EVENT_DESCRIPTION") in VOICE_TRAFFIC_KPIS
      and item.get("DC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "ppm": f"{round(voice_revenue / total_traffic, 2):,}" if total_traffic else None,
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_ppm failed: {e}"}


# Price per MB
def get_ppmb(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  try:
    revenue_target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)
    traffic_target_column = TRAFFIC_BILLING_MAP.get(billing_type.lower(), billing_type)

    data_revenue = sum(
      float(item[revenue_target_column])
      for item in revenue_records
      if item.get("SERVICE_NAME") == "Data" and item.get("OC_DATE") == date
    )

    total_traffic = sum(
      float(item[traffic_target_column])
      for item in traffic_records
      if item.get("EVENT_DESCRIPTION") in DATA_TRAFFIC_KPIS
      and item.get("DC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "ppm": f"{round(data_revenue / total_traffic, 2):,}" if total_traffic else None,
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_ppmb failed: {e}"}


# Minutes of Use per user
def get_mou(date: str, billing_type: BillingType = "prepaid") -> dict:
  try:
    traffic_target_column = TRAFFIC_BILLING_MAP.get(billing_type.lower(), billing_type)
    customer_target_column = CUSTOMER_BILLING_MAP.get(
      billing_type.lower(), billing_type
    )

    total_customers = sum(
      int(item[customer_target_column])
      for item in customer_records
      if item.get("EVENT_DESCRIPTION") == "Voice Users" and item.get("DC_DATE") == date
    )

    total_traffic = sum(
      float(item[traffic_target_column])
      for item in traffic_records
      if item.get("EVENT_DESCRIPTION") in VOICE_TRAFFIC_KPIS
      and item.get("DC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "mou": f"{round(total_traffic / total_customers, 2):,}"
      if total_customers
      else None,
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_mou failed: {e}"}


# MB of Use per user
def get_mbou(date: str, billing_type: BillingType = "prepaid") -> dict:
  try:
    traffic_target_column = TRAFFIC_BILLING_MAP.get(billing_type.lower(), billing_type)
    customer_target_column = CUSTOMER_BILLING_MAP.get(
      billing_type.lower(), billing_type
    )

    total_customers = sum(
      int(item[customer_target_column])
      for item in customer_records
      if item.get("EVENT_DESCRIPTION") == "Data Users" and item.get("DC_DATE") == date
    )

    total_traffic = sum(
      float(item[traffic_target_column])
      for item in traffic_records
      if item.get("EVENT_DESCRIPTION") in DATA_TRAFFIC_KPIS
      and item.get("DC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "mbou": f"{round(total_traffic / total_customers, 2):,}"
      if total_customers
      else None,
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_mbou failed: {e}"}


# Test the functions
if __name__ == "__main__":
  # date = "13-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_arpu_gsm(date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # date = "13-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_arpu_data(date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # date = "13-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_arpu_voice(date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # date = "13-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_ppm(date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  date = "12-AUG-26"
  for billing_type in ["prepaid", "hybrid", "total"]:
    result = get_ppmb(date, billing_type=billing_type)
    print(json.dumps(result, indent=2))

  # date = "13-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_mou(date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # date = "13-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_mbou(date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))
