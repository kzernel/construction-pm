"""
Bid generation module for construction projects.

This module provides functions to estimate material and labor costs based on
quantity takeoff data. It defines a simple data structure for unit costs and
calculates line-item costs, overhead, contingency, and grand totals.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any


@dataclass
class UnitCost:
    material_cost_per_unit: float
    labor_hours_per_unit: float
    labor_rate: float  # hourly labor rate


@dataclass
class LineItem:
    item: str
    quantity: float
    material_cost: float
    labor_hours: float
    labor_cost: float
    total_cost: float


def generate_bid(
    quantities: Dict[str, float],
    cost_data: Dict[str, UnitCost],
    overhead_pct: float = 0.10,
    contingency_pct: float = 0.05,
) -> Dict[str, Any]:
    """
    Generate a bid estimate from quantity data and unit costs.

    Args:
        quantities: Mapping of item names to quantities extracted from drawings.
        cost_data: Mapping of item names to UnitCost definitions.
        overhead_pct: Percentage of direct costs added as overhead.
        contingency_pct: Percentage of direct costs added as contingency.

    Returns:
        A dictionary with line items and totals.
    """
    line_items: List[LineItem] = []
    total_material_cost = 0.0
    total_labor_hours = 0.0
    total_labor_cost = 0.0

    for item, quantity in quantities.items():
        if item not in cost_data:
            raise ValueError(f"No cost data defined for item '{item}'")
        unit = cost_data[item]
        material_cost = quantity * unit.material_cost_per_unit
        labor_hours = quantity * unit.labor_hours_per_unit
        labor_cost = labor_hours * unit.labor_rate
        total_cost = material_cost + labor_cost
        line_items.append(
            LineItem(
                item=item,
                quantity=quantity,
                material_cost=material_cost,
                labor_hours=labor_hours,
                labor_cost=labor_cost,
                total_cost=total_cost,
            )
        )
        total_material_cost += material_cost
        total_labor_hours += labor_hours
        total_labor_cost += labor_cost

    direct_cost = total_material_cost + total_labor_cost
    overhead = direct_cost * overhead_pct
    contingency = direct_cost * contingency_pct
    grand_total = direct_cost + overhead + contingency

    return {
        "line_items": [asdict(li) for li in line_items],
        "total_material_cost": total_material_cost,
        "total_labor_hours": total_labor_hours,
        "total_labor_cost": total_labor_cost,
        "direct_cost": direct_cost,
        "overhead": overhead,
        "contingency": contingency,
        "grand_total": grand_total,
    }


# Sample unit cost data for demonstration
COST_DATA: Dict[str, UnitCost] = {
    "wall_length": UnitCost(material_cost_per_unit=4.0, labor_hours_per_unit=0.5, labor_rate=50.0),
    "door": UnitCost(material_cost_per_unit=150.0, labor_hours_per_unit=3.0, labor_rate=50.0),
    "window": UnitCost(material_cost_per_unit=100.0, labor_hours_per_unit=2.0, labor_rate=50.0),
}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(
        description="Generate a bid estimate from quantity data."
    )
    parser.add_argument(
        "--quantities-file",
        help="Path to a JSON file containing quantity data.",
        required=False,
    )
    parser.add_argument(
        "--pdf",
        help=(
            "Path to a PDF file. If provided, attempt to extract quantities using "
            "takeoff_parser."
        ),
        required=False,
    )
    parser.add_argument(
        "--overhead",
        type=float,
        default=0.10,
        help="Overhead percentage as a decimal (default 0.10 for 10%)",
    )
    parser.add_argument(
        "--contingency",
        type=float,
        default=0.05,
        help="Contingency percentage as a decimal (default 0.05 for 5%)",
    )
    args = parser.parse_args()

    quantities: Dict[str, float] = {}
    if args.quantities_file:
        with open(args.quantities_file) as f:
            quantities = json.load(f)
    elif args.pdf:
        # Attempt to parse quantities from the PDF using takeoff_parser
        from takeoff_parser import parse_pdf_for_quantities

        quantities = parse_pdf_for_quantities(args.pdf)
    else:
        raise SystemExit("Please provide a --quantities-file or --pdf argument.")

    bid = generate_bid(
        quantities,
        COST_DATA,
        overhead_pct=args.overhead,
        contingency_pct=args.contingency,
    )
    print(json.dumps(bid, indent=2))
