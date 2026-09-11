import csv
import os
from datetime import UTC, datetime
from typing import Literal

# Load the recharge dataset from a CSV file
_dir = os.path.dirname(os.path.abspath(__file__))
_datasets_dir = os.path.join(_dir, "..", "..", "..", "datasets")
with open(
  os.path.join(_datasets_dir, "recharge_dataset.csv"),
  mode="r",
  encoding="iso-8859-1",
  newline="",
) as file:
  records = list(csv.DictReader(file))

BillingType = Literal["prepaid", "hybrid", "total"]
RechargeGroup = Literal["mpesa", "other", "all"]


MPESA_KPI_LIST = [
  "MPesa Bundles",
  "So-Prati",
  "My Vodacom",
  "Super Agent",
  "Baza Baza",
  "M-Pesa Recharge",
]

OTHER_KPI_LIST = [
  "Electronic - Others",
  "Electronic - Bank",
  "Physical",
]

RECHARGE_KPI_LIST = MPESA_KPI_LIST + OTHER_KPI_LIST


RECHARGE_BILLING_MAP = {
  "prepaid": "REV_PREPAID",
  "hybrid": "REV_HYBRID",
  "total": "BPM_REVENUE",
}

RECHARGE_GROUP_MAP = {
  "mpesa": MPESA_KPI_LIST,
  "other": OTHER_KPI_LIST,
  "all": RECHARGE_KPI_LIST,
}

KPIType = Literal[
  "MPesa Bundles",
  "So-Prati",
  "My Vodacom",
  "Super Agent",
  "Baza Baza",
  "M-Pesa Recharge",
  "Electronic - Others",
  "Electronic - Bank",
  "Physical",
]


# Function to get total recharge per day for a specific KPI and date
def get_total_recharge_per_day(
  kpi: KPIType,
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the total recharge revenue for a single channel KPI on a specific date.

  Args:
      kpi: The recharge channel KPI to query (e.g., 'MPesa Bundles', 'Physical').
      date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary containing query parameters and formatted total recharge,
            or an error dictionary if retrieval fails.
  """
  try:
    target_column = RECHARGE_BILLING_MAP.get(billing_type.lower(), billing_type)

    total = sum(
      float(item[target_column])
      for item in records
      if item.get("CHANNEL") == kpi and item.get("BPM_START_DATE") == date
    )

    return {
      "date": date,
      "kpi": kpi,
      "billing_type": billing_type,
      "total_recharge": f"{round(total):,}",
    }
  except (KeyError, ValueError) as e:
    return {"error": f"get_total_recharge_per_day failed due to invalid data: {e}"}


# Function to get total M-Pesa recharge per day for a specific date
def get_total_mpesa_recharge_per_day(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the combined daily recharge total across all M-Pesa channels for a given date.

  Args:
      date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary containing the target date, billing type, and total M-Pesa recharge.
  """
  try:
    target_column = RECHARGE_BILLING_MAP.get(billing_type.lower(), billing_type)

    total_mpesa_recharge = sum(
      float(item[target_column])
      for item in records
      if item.get("CHANNEL") in MPESA_KPI_LIST and item.get("BPM_START_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "total_mpesa_recharge": f"{round(total_mpesa_recharge):,}",
    }
  except (KeyError, ValueError) as e:
    return {
      "error": f"get_total_mpesa_recharge_per_day failed due to invalid data: {e}"
    }


# Function to get total other recharge per day for a specific date
def get_total_other_recharge_per_day(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the combined daily recharge total for all non-M-Pesa channels (Electronic - Others, Electronic - Bank, Physical).

  Args:
      date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary with the target date, billing type, and combined non-M-Pesa recharge.
  """
  try:
    target_column = RECHARGE_BILLING_MAP.get(billing_type.lower(), billing_type)

    total_other_recharge = sum(
      float(item[target_column])
      for item in records
      if item.get("CHANNEL") in OTHER_KPI_LIST and item.get("BPM_START_DATE") == date
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "total_other_recharge": f"{round(total_other_recharge):,}",
    }
  except (KeyError, ValueError) as e:
    return {
      "error": f"get_total_other_recharge_per_day failed due to invalid data: {e}"
    }


# Function to get total recharge per day for all KPIs and a specific date
def get_total_recharge_per_day_all_kpis(
  date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the grand total daily recharge revenue across all available channels (M-Pesa + Other channels).

  Args:
      date: The target date in 'DD-MMM-YY' uppercase format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary containing the target date, billing type, and grand total recharge sum.
  """
  try:
    target_column = RECHARGE_BILLING_MAP.get(billing_type.lower(), billing_type)

    total_recharge_all_kpis = sum(
      float(item[target_column])
      for item in records
      if item.get("BPM_START_DATE") == date and item.get("CHANNEL") in RECHARGE_KPI_LIST
    )

    return {
      "date": date,
      "billing_type": billing_type,
      "total_recharge_all_kpis": f"{round(total_recharge_all_kpis):,}",
    }
  except (KeyError, ValueError) as e:
    return {
      "error": f"get_total_recharge_per_day_all_kpis failed due to invalid data: {e}"
    }


# Function to get the total revenue for a specific KPI and date range
def get_kpi_month_to_date_total(
  kpi: KPIType,
  target_date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the Month-To-Date (MTD) cumulative recharge revenue for a single channel KPI up to a given date.

  Args:
      kpi: The specific recharge channel KPI (e.g., 'MPesa Bundles', 'Physical').
      target_date: The end date for the MTD accumulation in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary containing target date, KPI, billing type, and formatted MTD revenue.
  """
  try:
    target_column = RECHARGE_BILLING_MAP.get(billing_type.lower(), billing_type)

    parsed_dt = datetime.strptime(target_date, "%d-%b-%y").replace(tzinfo=UTC)
    target_date_obj = parsed_dt.date()
    month_start_date = target_date_obj.replace(day=1)
    month_to_date_total = 0.0

    for record in records:
      if record["CHANNEL"] != kpi:
        continue

      record_date = (
        datetime.strptime(record["BPM_START_DATE"], "%d-%b-%y")
        .replace(tzinfo=UTC)
        .date()
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


# Function to get the total recharge for a specific group and date range
def get_grouped_recharge_month_to_date_total(
  target_date: str,
  group: RechargeGroup = "mpesa",
  billing_type: BillingType = "prepaid",
) -> dict:
  """Calculates the Month-To-Date (MTD) cumulative recharge total for a group of channels ('mpesa', 'other', or 'all').

  Args:
      target_date: The end date for the MTD period in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      group: The recharge channel group filter. Options are 'mpesa', 'other', or 'all'.
        Defaults to 'mpesa'.
      billing_type: The customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: A dictionary with the target date, group, billing type, and cumulative MTD total.
  """
  try:
    target_column = RECHARGE_BILLING_MAP.get(billing_type.lower(), billing_type)
    target_kpis = RECHARGE_GROUP_MAP.get(group.lower(), MPESA_KPI_LIST)

    parsed_dt = datetime.strptime(target_date, "%d-%b-%y").replace(tzinfo=UTC)
    target_date_obj = parsed_dt.date()
    month_start_date = target_date_obj.replace(day=1)
    month_to_date_total = 0.0

    for record in records:
      if record["CHANNEL"] not in target_kpis:
        continue

      record_date = (
        datetime.strptime(record["BPM_START_DATE"], "%d-%b-%y")
        .replace(tzinfo=UTC)
        .date()
      )

      if month_start_date <= record_date <= target_date_obj:
        month_to_date_total += float(record.get(target_column))

    return {
      "date": target_date,
      "group": group,
      "billing_type": billing_type,
      "month_to_date_total": f"{round(month_to_date_total):,}",
    }
  except (KeyError, ValueError, TypeError, AttributeError) as e:
    return {"error": f"get_grouped_recharge_month_to_date_total failed: {e}"}


# Function to get month-on-month metrics for a specific group and date
def get_grouped_recharge_month_on_month_metrics(
  target_date: str,
  group: RechargeGroup,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Compares Month-To-Date (MTD) recharge metrics between the target date and the same day of the previous month (MoM) for a channel group.

  Args:
      target_date: The current evaluation date in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      group: The recharge group to analyze ('mpesa', 'other', or 'all').
      billing_type: Customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: Comparison results containing current MTD total, previous month MTD total,
            absolute difference, and percentage change.
  """
  try:
    previous_month_date = get_previous_month_same_day(target_date)

    current_data = get_grouped_recharge_month_to_date_total(
      target_date, group, billing_type
    )
    previous_data = get_grouped_recharge_month_to_date_total(
      previous_month_date, group, billing_type
    )

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
      "group": group,
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
      "error": (
        f"get_grouped_recharge_month_on_month_metrics failed due to invalid data: {e}"
      )
    }


# Function to get year-on-year metrics for a specific group and date
def get_grouped_recharge_year_on_year_metrics(
  target_date: str,
  group: RechargeGroup,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Compares Month-To-Date (MTD) recharge metrics between the target date and the same day of the previous year (YoY) for a channel group.

  Args:
      target_date: The current evaluation date in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      group: The recharge group to analyze ('mpesa', 'other', or 'all').
      billing_type: Customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: Comparison results containing current year MTD total, previous year MTD total,
            absolute difference, and percentage change.
  """
  try:
    previous_year_date = get_previous_year_same_day(target_date)

    current_data = get_grouped_recharge_month_to_date_total(
      target_date, group, billing_type
    )
    previous_data = get_grouped_recharge_month_to_date_total(
      previous_year_date, group, billing_type
    )

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
      "group": group,
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
      "error": (
        f"get_grouped_recharge_year_on_year_metrics failed due to invalid data: {e}"
      )
    }


# Function to get month-on-month metrics for a specific KPI and date
def get_recharge_month_on_month_metrics(
  kpi: KPIType,
  target_date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Compares Month-To-Date (MTD) recharge metrics between the target date and the same day of the previous month (MoM) for a specific KPI channel.

  Args:
      kpi: The recharge channel KPI to evaluate (e.g., 'MPesa Bundles', 'Physical').
      target_date: The current evaluation date in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: Customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: Comparison results containing current MTD total, previous month MTD total,
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
      "error": (f"get_recharge_month_on_month_metrics failed due to invalid data: {e}")
    }


# Function to get year-on-year metrics for a specific KPI and date
def get_recharge_year_on_year_metrics(
  kpi: KPIType,
  target_date: str,
  billing_type: BillingType = "prepaid",
) -> dict:
  """Compares Month-To-Date (MTD) recharge metrics between the target date and the same day of the previous year (YoY) for a specific KPI channel.

  Args:
      kpi: The recharge channel KPI to evaluate (e.g., 'MPesa Bundles', 'Physical').
      target_date: The current evaluation date in 'DD-MMM-YY' format (e.g., '22-OCT-25').
      billing_type: Customer billing segment ('prepaid', 'hybrid', 'total').
        Defaults to 'prepaid'.

  Returns:
      dict: Comparison results containing current year MTD total, previous year MTD total,
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
      "error": (f"get_recharge_year_on_year_metrics failed due to invalid data: {e}")
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
