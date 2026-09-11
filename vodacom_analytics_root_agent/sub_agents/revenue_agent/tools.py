import csv
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from dateutil.relativedelta import relativedelta

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"


# Total Service Revenue ------------------------------------------------------
# CBU - Postpaid ---------------------------------------------------------
# VB ----------------------------------------------------------------

# Load the revenue dataset from a CSV file
_dir = os.path.dirname(os.path.abspath(__file__))
_datasets_dir = os.path.join(_dir, "..", "..", "..", "datasets")
with open(
  os.path.join(_datasets_dir, "revenue_dataset.csv"),
  mode="r",
  encoding="iso-8859-1",
  newline="",
) as file:
  records = list(csv.DictReader(file))


# Rev postpaid dataset
with open(
  os.path.join(_datasets_dir, "rev_postpaid_vb.csv"),
  mode="r",
  encoding="iso-8859-1",
  newline="",
) as file:
  rev_postpaid_records = list(csv.DictReader(file))


REVENUE_BILLING_MAP = {
  "prepaid": "DR_PREPAID",
  "hybrid": "DR_HYBRID",
  "total": "DR_TOTAL",
}

REVENUE_BILLING_MAP_EXCLUSIVE_FOR_VB_AND_CBU_POSTPAID = {
  "prepaid": "REVENUE_PREPAID",
  "hybrid": "REVENUE_HYBRID",
  "total": "REVENUE_TOTAL",
}


KPI_LIST = [
  "Voice",
  "Data",
  "Sms",
  "Airtime Advance",
  "Others",
  "Interconnect",
  # "Device Finance - Repayment",
  "Core",
  "Payments",
  "Financial Services",
  "Others - M-Pesa",
  "CBU Postpaid",
  "VB",
]


CBU_KPI_LIST = [
  "Voice",
  "Data",
  "Sms",
  "Airtime Advance",
  "Others",
]


MPESA_KPI_LIST = [
  "Core",
  "Payments",
  "Financial Services",
  "Others - M-Pesa",
]


CBU_KPI_LIST_INCLUDING_INTERCONNECT = [
  "Voice",
  "Data",
  "Sms",
  "Airtime Advance",
  "Others",
  "Interconnect",
]

POSTPAID_VB_KPIS = {
  "CBU Postpaid",
  "VB",
}


BillingType = Literal["prepaid", "hybrid", "total"]

KPIType = Literal[
  "Voice",
  "Data",
  "Sms",
  "Airtime Advance",
  "Others",
  "Interconnect",
  "Device Finance - Repayment",
  "Core",
  "Payments",
  "Financial Services",
  "Others - M-Pesa",
  "CBU Postpaid",
  "VB",
]


# Function to get total revenue per day for a specific KPI and date
def get_total_revenue_per_day(
  kpi: KPIType,
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the total revenue for a single service KPI on a specific date.

  Args:
      kpi: The revenue service KPI to query (e.g., 'Voice', 'Data', 'Sms').
      date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary containing query metadata and formatted total revenue,
            or an error dictionary if processing fails.
  """
  try:
    is_postpaid_vb = kpi in POSTPAID_VB_KPIS

    mapping = (
      REVENUE_BILLING_MAP_EXCLUSIVE_FOR_VB_AND_CBU_POSTPAID
      if is_postpaid_vb
      else REVENUE_BILLING_MAP
    )

    target_column = mapping.get(
      billing_type.lower(),
      billing_type,
    )

    source_data = rev_postpaid_records if is_postpaid_vb else records
    kpi_field = "SERVICE_TYPE" if is_postpaid_vb else "SERVICE_NAME"
    date_field = "DAY_DT" if is_postpaid_vb else "OC_DATE"

    total = sum(
      float(item[target_column])
      for item in source_data
      if item.get(kpi_field) == kpi and item.get(date_field) == date
    )

    return {
      "date": date,
      "kpi": kpi,
      "billing_type": billing_type,
      "total_revenue": f"{round(total):,}",
    }

  except (KeyError, ValueError) as e:
    return {"error": f"get_total_revenue_per_day failed due to invalid data: {e}"}


# Function to get total CBU prepaid revenue per day for a specific date
def get_cbu_prepaid_revenue_per_day(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the combined daily CBU revenue across standard services (Voice, Data, Sms, Airtime Advance, Others).

  Args:
      date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary containing the target date, billing type, and total CBU revenue.
  """
  try:
    target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)

    total_cbu_prepaid = sum(
      float(item[target_column])
      for item in records
      if item.get("SERVICE_NAME") in CBU_KPI_LIST and item.get("OC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "total_cbu_prepaid": f"{round(total_cbu_prepaid):,}",
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_cbu_prepaid_revenue_per_day failed: {e}"}


# Function to get total CBU prepaid revenue per day including interconnect for a specific date
def get_cbu_prepaid_revenue_per_day_including_interconnect(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the combined daily CBU revenue including Interconnect revenue for a given date.

  Args:
      date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary containing target date, billing type, and total CBU revenue including Interconnect.
  """
  try:
    target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)

    total_cbu_prepaid_including_interconnect = sum(
      float(item[target_column])
      for item in records
      if item.get("SERVICE_NAME") in CBU_KPI_LIST_INCLUDING_INTERCONNECT
      and item.get("OC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "total_cbu_prepaid_including_interconnect": f"{round(total_cbu_prepaid_including_interconnect):,}",
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {
      "error": f"get_cbu_prepaid_revenue_per_day_including_interconnect failed: {e}"
    }


# Function to get total M-Pesa revenue per day for a specific date
def get_mpesa_revenue_per_day(date: str, billing_type: BillingType = "prepaid") -> dict:
  """
  Calculates the total daily M-Pesa revenue for a given date.

    Args:
        date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
        billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
          Defaults to 'prepaid'.
    Returns:
        dict: A dictionary containing target date, billing type, and total M-Pesa revenue.
  """

  try:
    target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)

    total_mpesa = sum(
      float(item[target_column])
      for item in records
      if item.get("SERVICE_NAME") in MPESA_KPI_LIST and item.get("OC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "total_mpesa": f"{round(total_mpesa):,}",
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_mpesa_revenue_per_day failed: {e}"}


# Function to get total service revenue per day for a specific date
def get_total_service_revenue_per_day(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """
  Calculates the total daily service revenue for a given date.

  Args:
      date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.
  Returns:
      dict: A dictionary containing target date, billing type, and total service revenue.
  """
  try:
    target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)

    total_service = sum(
      float(item[target_column])
      for item in records
      if item.get("SERVICE_NAME") in KPI_LIST and item.get("OC_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "total_service": f"{round(total_service):,}",
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_total_service_revenue_per_day failed: {e}"}


# Function to get the total revenue for a specific KPI and date range
def get_kpi_month_to_date_total(
  kpi: KPIType,
  target_date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the Month-To-Date (MTD) cumulative revenue for a single service KPI up to a given date.

  Args:
      kpi: The revenue service KPI (e.g., 'Voice', 'Data', 'Interconnect').
      target_date: The end date for the MTD period in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary with target date, KPI, billing type, and cumulative MTD revenue.
  """
  try:
    parsed_dt = datetime.strptime(target_date, "%d-%b-%y").replace(tzinfo=UTC)
    target_date_obj = parsed_dt.date()
    month_start_date = target_date_obj.replace(day=1)
    month_to_date_total = 0.0

    is_postpaid_vb = kpi in POSTPAID_VB_KPIS

    mapping = (
      REVENUE_BILLING_MAP_EXCLUSIVE_FOR_VB_AND_CBU_POSTPAID
      if is_postpaid_vb
      else REVENUE_BILLING_MAP
    )

    target_column = mapping.get(
      billing_type.lower(),
      billing_type,
    )

    source_data = rev_postpaid_records if is_postpaid_vb else records
    kpi_field = "SERVICE_TYPE" if is_postpaid_vb else "SERVICE_NAME"
    date_field = "DAY_DT" if is_postpaid_vb else "OC_DATE"

    for record in source_data:
      if record[kpi_field] != kpi:
        continue

      record_date = (
        datetime.strptime(record[date_field], "%d-%b-%y").replace(tzinfo=UTC).date()
      )

      if month_start_date <= record_date <= target_date_obj:
        month_to_date_total += float(record.get(target_column))

    return {
      "date": target_date,
      "kpi": kpi,
      "billing_type": billing_type,
      "month_to_date_total": f"{round(month_to_date_total):,}",
    }

  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_kpi_month_to_date_total failed: {e}"}


# Function to get month-on-month metrics for a specific KPI and date
def get_revenue_month_on_month_metrics(
  kpi: KPIType,
  target_date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Compares Month-To-Date (MTD) revenue metrics between the target date and the same day of the previous month (MoM) for a KPI.

  Args:
      kpi: The revenue service KPI to analyze (e.g., 'Voice', 'Data').
      target_date: The evaluation date in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: Customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: Comparison metrics including current MTD total, previous month MTD total,
            absolute difference, and percentage change.
  """
  try:
    previous_month_date = get_previous_month_same_day(target_date)

    current_data = get_kpi_month_to_date_total(kpi, target_date, billing_type)
    previous_data = get_kpi_month_to_date_total(kpi, previous_month_date, billing_type)

    current_month_total = float(
      current_data.get("month_to_date_total", 0).replace(",", "")
    )
    previous_month_total = float(
      previous_data.get("month_to_date_total", 0).replace(",", "")
    )

    difference = current_month_total - previous_month_total

    percentage_change = (
      (difference / previous_month_total) * 100 if previous_month_total != 0 else None
    )

    return {
      "target_date": target_date,
      "previous_month_date": previous_month_date,
      "kpi": kpi,
      "billing_type": billing_type,
      "current_month_total": f"{round(current_month_total):,}",
      "previous_month_total": f"{round(previous_month_total):,}",
      "difference": f"{round(difference):,}",
      "percentage_change": (
        round(percentage_change, 1) if percentage_change is not None else None
      ),
    }
  except (KeyError, ValueError, TypeError) as e:
    return {
      "error": (f"get_revenue_month_on_month_metrics failed due to invalid data: {e}")
    }


# Function to get month-to-date total CBU prepaid revenue for a specific date
def get_cbu_prepaid_month_to_date_total(
  target_date: str,
  billing_type: BillingType = "prepaid",
  include_interconnect: bool = False,
) -> dict:
  """Calculates the Month-To-Date (MTD) cumulative total CBU revenue, with an option to include Interconnect revenue.

  Args:
      target_date: The end date for the MTD accumulation in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.
      include_interconnect: Whether to include 'Interconnect' in the aggregated CBU revenue total.
        Defaults to False.

  Returns:
      dict: A dictionary containing target date, billing type, and the aggregated MTD CBU revenue total.
  """
  try:
    target_column = REVENUE_BILLING_MAP.get(billing_type.lower(), billing_type)

    parsed_dt = datetime.strptime(target_date, "%d-%b-%y").replace(tzinfo=UTC)
    target_date_obj = parsed_dt.date()
    month_start_date = target_date_obj.replace(day=1)
    cbu_prepaid_month_to_date_total = 0.0

    kpi_list = (
      CBU_KPI_LIST_INCLUDING_INTERCONNECT if include_interconnect else CBU_KPI_LIST
    )

    for record in records:
      if record["SERVICE_NAME"] not in kpi_list:
        continue

      record_date = (
        datetime.strptime(record["OC_DATE"], "%d-%b-%y").replace(tzinfo=UTC).date()
      )

      if month_start_date <= record_date <= target_date_obj:
        cbu_prepaid_month_to_date_total += float(record.get(target_column))

    return {
      "date": target_date,
      "billing_type": billing_type,
      "cbu_prepaid_month_to_date_total": f"{round(cbu_prepaid_month_to_date_total):,}",
    }

  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_cbu_prepaid_month_to_date_total failed: {e}"}


# Function to get month-on-month metrics for CBU prepaid revenue
def get_cbu_prepaid_revenue_month_on_month_metrics(
  date: str,
  billing_type: BillingType = "prepaid",
  include_interconnect: bool = False,
) -> dict:
  """Compares Month-To-Date (MTD) CBU revenue between the target date and the same day of the previous month (MoM).

  Args:
      date: The evaluation date in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: Customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.
      include_interconnect: Whether to include Interconnect revenue in the comparison.
        Defaults to False.

  Returns:
      dict: Comparison results containing current MTD total, previous month MTD total,
            absolute difference, and percentage change.
  """
  try:
    previous_month_date = get_previous_month_same_day(date)

    current_data = get_cbu_prepaid_month_to_date_total(
      date, billing_type, include_interconnect
    )
    previous_data = get_cbu_prepaid_month_to_date_total(
      previous_month_date, billing_type, include_interconnect
    )

    current_month_total = float(
      current_data.get("cbu_prepaid_month_to_date_total", 0).replace(",", "")
    )
    previous_month_total = float(
      previous_data.get("cbu_prepaid_month_to_date_total", 0).replace(",", "")
    )

    difference = current_month_total - previous_month_total

    percentage_change = (
      (difference / previous_month_total) * 100 if previous_month_total != 0 else None
    )

    return {
      "date": date,
      "previous_month_date": previous_month_date,
      "billing_type": billing_type,
      "current_month_total": f"{round(current_month_total):,}",
      "previous_month_total": f"{round(previous_month_total):,}",
      "difference": f"{round(difference):,}",
      "percentage_change": (
        round(percentage_change, 1) if percentage_change is not None else None
      ),
    }

  except ValueError as e:
    return {
      "error": f"get_cbu_prepaid_revenue_month_on_month_metrics failed due to invalid date: {e}"
    }


# Function to get year-on-year metrics for CBU prepaid revenue
def get_cbu_prepaid_revenue_year_on_year_metrics(
  date: str,
  billing_type: BillingType = "prepaid",
  include_interconnect: bool = False,
) -> dict:
  """Compares Month-To-Date (MTD) CBU revenue between the target date and the same day of the previous year (YoY).

  Args:
      date: The evaluation date in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: Customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.
      include_interconnect: Whether to include Interconnect revenue in the comparison.
        Defaults to False.

  Returns:
      dict: Comparison results containing current year MTD total, previous year MTD total,
            absolute difference, and percentage change.
  """
  try:
    previous_year_date = get_previous_year_same_day(date)

    current_data = get_cbu_prepaid_month_to_date_total(
      date, billing_type, include_interconnect
    )
    previous_data = get_cbu_prepaid_month_to_date_total(
      previous_year_date, billing_type, include_interconnect
    )

    current_year_total = float(
      current_data.get("cbu_prepaid_month_to_date_total", 0).replace(",", "")
    )
    previous_year_total = float(
      previous_data.get("cbu_prepaid_month_to_date_total", 0).replace(",", "")
    )

    difference = current_year_total - previous_year_total
    percentage_change = (
      (difference / previous_year_total) * 100 if previous_year_total != 0 else None
    )

    return {
      "date": date,
      "previous_year_date": previous_year_date,
      "billing_type": billing_type,
      "current_year_total": f"{round(current_year_total):,}",
      "previous_year_total": f"{round(previous_year_total):,}",
      "difference": f"{round(difference):,}",
      "percentage_change": (
        round(percentage_change, 1) if percentage_change is not None else None
      ),
    }

  except ValueError as e:
    return {
      "error": f"get_cbu_prepaid_revenue_year_on_year_metrics failed due to invalid date: {e}"
    }


# Function to get year-on-year metrics for a specific KPI and date
def get_revenue_year_on_year_metrics(
  kpi: KPIType,
  target_date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Compares Month-To-Date (MTD) revenue metrics between the target date and the same day of the previous year (YoY) for a KPI.

  Args:
      kpi: The revenue service KPI to analyze (e.g., 'Voice', 'Data').
      target_date: The evaluation date in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: Customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: Comparison metrics including current year MTD total, previous year MTD total,
            absolute difference, and percentage change.
  """
  try:
    previous_year_date = get_previous_year_same_day(target_date)
    current_data = get_kpi_month_to_date_total(kpi, target_date, billing_type)
    previous_data = get_kpi_month_to_date_total(kpi, previous_year_date, billing_type)

    current_year_total = float(
      current_data.get("month_to_date_total", 0).replace(",", "")
    )
    previous_year_total = float(
      previous_data.get("month_to_date_total", 0).replace(",", "")
    )

    difference = current_year_total - previous_year_total
    percentage_change = (
      (difference / previous_year_total) * 100 if previous_year_total != 0 else None
    )

    return {
      "target_date": target_date,
      "previous_year_date": previous_year_date,
      "kpi": kpi,
      "billing_type": billing_type,
      "current_year_total": f"{round(current_year_total):,}",
      "previous_year_total": f"{round(previous_year_total):,}",
      "difference": f"{round(difference):,}",
      "percentage_change": (
        round(percentage_change, 1) if percentage_change is not None else None
      ),
    }
  except (KeyError, ValueError, TypeError) as e:
    return {
      "error": (f"get_revenue_year_on_year_metrics failed due to invalid data: {e}")
    }


# Function to get the same day of the previous month for a given date
def get_previous_month_same_day(target_date: str) -> str:
  try:
    target_date_obj = (
      datetime.strptime(target_date, "%d-%b-%y").replace(tzinfo=UTC).date()
    )
    prev_month_date = target_date_obj - relativedelta(months=1)
    return prev_month_date.strftime("%d-%b-%y").upper()
  except ValueError as e:
    raise ValueError(
      f"Data inválida '{target_date}'. O formato esperado é 'DD-MMM-YY' (ex: '22-OCT-25')."
    ) from e


# Function to get the same day of the previous year for a given date
def get_previous_year_same_day(target_date: str) -> str:
  try:
    target_date_obj = (
      datetime.strptime(target_date, "%d-%b-%y").replace(tzinfo=UTC).date()
    )
    prev_year_date = target_date_obj - relativedelta(years=1)
    return prev_year_date.strftime("%d-%b-%y").upper()
  except ValueError as e:
    raise ValueError(
      f"Data inválida '{target_date}'. O formato esperado é 'DD-MMM-YY' (ex: '22-OCT-25')."
    ) from e


def generate_dashboard(
  title: str,
  summary: str,
  charts: list,
  anomalies: list,
  filename: str = "dashboard",
) -> dict:
  return {
    "title": title,
    "summary": summary,
    "charts": charts,
    "anomalies": anomalies,
    "filename": filename,
  }


if __name__ == "__main__":
  # # Test case for total revenue per day
  kpi = "VB"  # VB
  date = "08-SEP-26"
  for billing_type in ["prepaid", "hybrid", "total"]:
    result = get_total_revenue_per_day(kpi, date, billing_type=billing_type)
    print(json.dumps(result, indent=2))

  # kpi = "CBU Postpaid"  # CBU Postpaid
  # date = "06-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_total_revenue_per_day(kpi, date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # date = "06-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_mpesa_revenue_per_day(date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # # # get_total_service_revenue_per_day
  # date = "09-SEP-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_total_service_revenue_per_day(date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # # get_kpi_month_to_date_total
  # kpi = "VB"  # VB
  # date = "06-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_kpi_month_to_date_total(kpi, date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # kpi = "Voice"  # Voice
  # date = "04-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_revenue_month_on_month_metrics(kpi, date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))

  # kpi = "Voice"  # Voice
  # date = "04-AUG-26"
  # for billing_type in ["prepaid", "hybrid", "total"]:
  #   result = get_revenue_year_on_year_metrics(kpi, date, billing_type=billing_type)
  #   print(json.dumps(result, indent=2))
