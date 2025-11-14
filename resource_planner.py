#!/usr/bin/env python3
"""
Resource planning utility for construction project management software.

This script provides a function to estimate the number of resources (people)
needed to complete a project given the estimated total labor hours, start date,
end date, working hours per day, number of working days per week, and an optional
list of holidays.

This is an initial proof-of-concept to demonstrate the logic and is not intended
for production use without further refinement and error handling.
"""
import datetime
import math
from typing import List, Optional


def calculate_resources(total_hours: float,
                        start_date: str,
                        end_date: str,
                        hours_per_day: int = 8,
                        days_per_week: int = 5,
                        holidays: Optional[List[str]] = None) -> int:
    """
    Calculate the number of resources required to complete the project.

    :param total_hours: Estimated total labor hours required.
    :param start_date: Project start date in YYYY-MM-DD format.
    :param end_date: Project end date in YYYY-MM-DD format.
    :param hours_per_day: Number of working hours in a day.
    :param days_per_week: Number of working days per week (5 for Monday–Friday,
                          6 for Monday–Saturday, etc.).
    :param holidays: List of holiday dates in YYYY-MM-DD format.
    :return: Number of resources required as an integer.
    """
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if end < start:
        raise ValueError("End date must be on or after start date")

    # Prepare a set of holiday dates for quick lookup
    holiday_dates: set = set()
    if holidays:
        holiday_dates = {datetime.datetime.strptime(h, "%Y-%m-%d").date() for h in holidays}

    # Determine which weekdays are considered working days
    # Python weekday() returns 0 for Monday ... 6 for Sunday
    working_weekdays = set(range(days_per_week))  # e.g., {0,1,2,3,4} for 5-day week

    # Count working days between start and end, excluding holidays
    working_days_count = 0
    current_date = start
    while current_date <= end:
        if current_date.weekday() in working_weekdays and current_date not in holiday_dates:
            working_days_count += 1
        current_date += datetime.timedelta(days=1)

    available_hours = working_days_count * hours_per_day
    if available_hours <= 0:
        raise ValueError("No available working hours between start and end dates")

    # Calculate resources required and round up to the nearest whole number
    resources_required = math.ceil(total_hours / available_hours)
    return resources_required


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="Calculate required resources for a project.")
    parser.add_argument("total_hours", type=float, help="Estimated total labor hours required")
    parser.add_argument("start_date", type=str, help="Project start date (YYYY-MM-DD)")
    parser.add_argument("end_date", type=str, help="Project end date (YYYY-MM-DD)")
    parser.add_argument("--hours-per-day", type=int, default=8, help="Working hours per day")
    parser.add_argument("--days-per-week", type=int, default=5, help="Working days per week")
    parser.add_argument("--holidays", nargs="*", default=[], help="Holiday dates (YYYY-MM-DD)")

    args = parser.parse_args()

    resources = calculate_resources(
        total_hours=args.total_hours,
        start_date=args.start_date,
        end_date=args.end_date,
        hours_per_day=args.hours_per_day,
        days_per_week=args.days_per_week,
        holidays=args.holidays
    )
    print(f"Estimated resources required: {resources}")
