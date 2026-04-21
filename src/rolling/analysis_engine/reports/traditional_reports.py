from typing import Optional, Iterable
import re

from rolling.analysis_engine.contracts import HormoneAnalysisResult

def build_descriptive_hormone_report(result: HormoneAnalysisResult) -> dict[str, Optional[str]]:
    """
    Builds a traditional descriptive hormone report based on the provided analysis result.

    Args:
        result (HormoneAnalysisResult): An analysis result containing summary statistics, tables of statistics, and conclusions from a descriptive hormone analysis.

    Returns:
        dict[str, Optional[str]]: A dictionary containing the report content.
            - "report_text": A string containing the formatted report text.
            - "summary_text": A string containing a summary of the analysis results.
    """
    summary = result.summary or {}
    tables_by_name = {table["name"]: table["rows"] for table in result.tables} 

    hormone_rows = tables_by_name.get("hormone_statistics", [])
    hormone_phase_rows = tables_by_name.get("hormone_phase_statistics", [])
    hormone_performance_rows = tables_by_name.get("hormone_performance_statistics", [])
    hormone_dysmenorrhea_rows = tables_by_name.get("hormone_dysmenorrhea_statistics", [])
    hormone_dysmenorrhea_performance_rows = tables_by_name.get("hormone_dysmenorrhea_performance_statistics", [])
    comparative_hormone_phase_rows = tables_by_name.get("comparative_hormone_phase_statistics", [])
    comparative_hormone_performance_rows = tables_by_name.get("comparative_hormone_performance_statistics", [])
    comparative_hormone_dysmenorrhea_rows = tables_by_name.get("comparative_hormone_dysmenorrhea_statistics", [])
    comparative_hormone_dysmenorrhea_performance_rows = tables_by_name.get("comparative_hormone_dysmenorrhea_performance_statistics", [])
    comparative_hormone_dysmenorrhea_phase_rows = tables_by_name.get("comparative_hormone_dysmenorrhea_phase_statistics", [])

    summary_text = (f"Descriptive hormone analysis produced "
                    f"{summary.get('total_grouped_row_count', 0)} grouped summaries across "
                    f"{summary.get('hormone_row_count', 0)} hormones.")
    
    lines = ["# Traditional Descriptive Hormone Report",
             "",
             summary_text,
             "",
             "## Overview",
             f"- Hormone observations: {summary.get('hormone_row_count', 0)}",
             f"- Hormone + cycle phase observations: {summary.get('hormone_phase_row_count', 0)}",
             f"- Hormone + performance observations: {summary.get('hormone_performance_row_count', 0)}",
             f"- Hormone + dysmenorrhea observations: {summary.get('hormone_dysmenorrhea_row_count', 0)}",
             f"- Hormone + dysmenorrhea + performance observations: {summary.get('hormone_dysmenorrhea_performance_row_count', 0)}",
             f"- Hormone + dysmenorrhea + cycle phase observations {summary.get('comparative_hormone_dysmenorrhea_phase_row_count', 0)}"]
    
    if hormone_rows:
        lines.extend(["",
                      "## Hormone Summary"])
        for row in sorted(hormone_rows,
                          key=lambda item: item["hormone_name"]):
            lines.append(f"- {row['hormone_name']}: ")
            lines.extend(create_single_parameter_summary_stats_lines(row))

    if hormone_phase_rows:
        lines.extend(["",
                      "## Hormone by Cycle Phase"])
        for row in sorted(hormone_phase_rows,
                          key=lambda item: (item["cycle_phase"], item["hormone_name"]),
                          ):
            lines.append(f"- {row['hormone_name']} in '{row['cycle_phase']}': ")
            lines.extend(create_single_parameter_summary_stats_lines(row))

    if hormone_performance_rows:
        lines.extend(["", "## Hormone by Performance Type"])
        for row in sorted(
            hormone_performance_rows,
            key=lambda item: (item["performance_type"], item["hormone_name"]),
        ):
            lines.append(f"- {row['hormone_name']} in '{row['performance_type']}': ")
            lines.extend(create_single_parameter_summary_stats_lines(row))

    if comparative_hormone_performance_rows:
        lines.extend(["", "## Hormone by Comparing Performance Types"])
        for row in sorted(
            comparative_hormone_performance_rows,
            key=lambda item: item["hormone_name"]
        ):
            lines.append(f"- {row['hormone_name']} in ['{row['performance_type_a']}', '{row['performance_type_b']}']: ")
            lines.extend(create_multiple_parameter_summary_states_lines(row))

    if hormone_dysmenorrhea_rows:
        lines.extend(["", "## Hormone by Dysmenorrhea Presence"])
        for row in sorted(
            hormone_dysmenorrhea_rows,
            key=lambda item: (item["hormone_name"], item["dysmenorrhea_present"]),
        ):
            dys_label = create_dysmenorrhea_label(row)
            lines.append(f"- {row['hormone_name']} with {dys_label}: ")
            lines.extend(create_single_parameter_summary_stats_lines(row))

    if comparative_hormone_phase_rows:
        lines.extend(["", "## Hormone by Comparing Cycle Phases"])
        for row in sorted(
            comparative_hormone_phase_rows,
            key=lambda item: item["hormone_name"]
        ):
            lines.append(f"- {row['hormone_name']} in ['{row['cycle_phase_a']}', '{row['cycle_phase_b']}']: ")
            lines.extend(create_multiple_parameter_summary_states_lines(row))

    if comparative_hormone_dysmenorrhea_rows:
        lines.extend(["", "## Hormone by Comparing Dysmenorrhea Presence"])
        for row in sorted(
            comparative_hormone_dysmenorrhea_rows,
            key=lambda item: item["hormone_name"]
        ):
            dys_label_a, dys_label_b = create_dysmenorrhea_label(row)
            lines.append(f"- {row['hormone_name']} in ['{dys_label_a}', '{dys_label_b}']: ")
            lines.extend(create_multiple_parameter_summary_states_lines(row))

    if hormone_dysmenorrhea_performance_rows:
        lines.extend(["", "## Hormone by Dysmenorrhea Presence and Performance Type"])
        for row in sorted(
            hormone_dysmenorrhea_performance_rows,
            key=lambda item: (
                item["performance_type"],
                item["hormone_name"],
                item["dysmenorrhea_present"],
            ),
        ):
            dys_label = create_dysmenorrhea_label(row)
            lines.append(f"- {row['hormone_name']} in '{row['performance_type']}' with {dys_label}: ")
            lines.extend(create_single_parameter_summary_stats_lines(row))

    if comparative_hormone_dysmenorrhea_performance_rows:
        lines.extend(["", "## Hormone by Comparing Dysmenorrhea Presence and Performance Types"])
        for row in sorted(
            comparative_hormone_dysmenorrhea_performance_rows,
            key=lambda item: item["hormone_name"]
        ):
            if row.get("dysmenorrhea_present") is None:
                dys_label_a = "dysmenorrhea present" if str(row.get("dysmenorrhea_present_a")).lower() == "true" else "dysmenorrhea absent"
                dys_label_b = "dysmenorrhea present" if str(row.get("dysmenorrhea_present_b")).lower() == "true" else "dysmenorrhea absent"
                lines.append(f"- {row['hormone_name']} in '{row.get('performance_type')}'"
                             f" comparing dysmenorrhea experience [{dys_label_a}, {dys_label_b}]")
                lines.extend(create_multiple_parameter_summary_states_lines(row))
            else:
                dys_label = "dysmenorrhea present" if str(row.get("dysmenorrhea_present")).lower() == "true" else "dysmenorrhea absent"
                lines.append(f"- {row['hormone_name']} with {dys_label} "
                             f"comparing performance types ['{row.get('performance_type_a', 'Unknown')}', '{row.get('performance_type_b', 'Unknown')}']")
                lines.extend(create_multiple_parameter_summary_states_lines(row))

    if comparative_hormone_dysmenorrhea_phase_rows:
        lines.extend(["", "## Hormone by Comparing Dysmenorrhea Presence and Cycle Phases"])
        for row in sorted(
            comparative_hormone_dysmenorrhea_phase_rows,
            key=lambda item: item["hormone_name"]
        ):
            if row.get("dysmenorrhea_present") is None:
                dys_label_a = "dysmenorrhea present" if str(row.get("dysmenorrhea_present_a")).lower() == "true" else "dysmenorrhea absent"
                dys_label_b = "dysmenorrhea present" if str(row.get("dysmenorrhea_present_b")).lower() == "true" else "dysmenorrhea absent"
                lines.append(f"- {row['hormone_name']} during the '{row.get('cycle_phase')}'"
                             f" comparing dysmenorrhea experience [{dys_label_a}, {dys_label_b}]")
                lines.extend(create_multiple_parameter_summary_states_lines(row))
            else:
                dys_label = "dysmenorrhea present" if str(row.get("dysmenorrhea_present")).lower() == "true" else "dysmenorrhea absent"
                lines.append(f"- {row['hormone_name']} {dys_label} "
                             f"comparing cycle phases ['{row.get('cycle_phase_a', 'Unknown')}', '{row.get('cycle_phase_b', 'Unknown')}']")
                lines.extend(create_multiple_parameter_summary_states_lines(row))

    hormones = sorted({row["hormone_name"] for row in hormone_rows})
    performance_types = sorted({row["performance_type"] for row in hormone_performance_rows})

    lines.extend(["",
                  "## Coverage",
                  f"- Hormones covered: {', '.join(hormones) if hormones else 'None'}",
                  f"- Performance types covered: {', '.join(performance_types) if performance_types else 'None'}"])
    
    return {"report_text": "\n".join(lines),
            "summary_text": summary_text,}

# HELPERS
def create_single_parameter_summary_stats_lines(row: dict) -> list:
    """
    Creates lines for a single parameter summary statistics report.
    
    Args:
        row (dict): A dictionary containing the observation count and statistical values for a particular statistic summary.
        
    Returns:
        list: A list of strings containing a more readable summary of the statistics."""
    lines = []
    lines.append(f"\t- n={row['observation_count']} ")
    lines.append(f"\t- mean={row['mean']}, median={row['median']}, sd={row['standard_deviation']}")
    return lines

def create_multiple_parameter_summary_states_lines(row) -> list:
    """
    Creates lines for a multiple parameter summary statistics report.
    
    Args:
        row (dict): A dictionary containing the observation count and statistical values for a particular statistic summary.
        
    Returns:
        list: A list of strings containing a more readable summary of the statistics.
    """
    lines = []
    lines.append(f"\t- n={row['observation_count']} ")
    lines.append(f"\t- mean difference percentage={row['mean_diff_pct']}%")
    lines.append(f"\t- mean difference percentage interpretation: {interpret_mean_diff_pct(row['mean_diff_pct'])}")
    lines.append(f"\t- hedges' g={row['hedges_g']}, independent t={row['independent_t']}")
    lines.append(f"\t- hedges' g interpretation: {interpret_cohen(row['hedges_g'])}"
                 f"\t- independent t interpretation: {interpret_t_statistic(row['independent_t'])}")
    return lines

def create_dysmenorrhea_label(row) -> str:
    """
    Creates a dysmenorrhea label based on the boolean value of dysmenorrhea_present.

    Args:
        row (dict): A dictionary containing the observation count and statistical values for a particular statistic summary.

    Returns:
        str: "dysmenorrhea present" if dysmenorrhea was present in the group. "dysmenorrhea absent" otherwise.
    """
    if "dysmenorrhea_present" in row.keys():
        return "dysmenorrhea present" if row["dysmenorrhea_present"] else "dysmenorrhea absent"
    if "dysmenorrhea_present_a" in row.keys() and "dysmenorrhea_present_b" in row.keys():
        return "dysmenorrhea present" if row["dysmenorrhea_present_a"] else "dysmenorrhea absent", \
            "dysmenorrhea present" if row["dysmenorrhea_present_b"] else "dysmenorrhea absent"
    
def interpret_cohen(value: Optional[float]) -> Optional[str]:
    """
    Returns an interpretation of a Cohen's d.
    
    Args:
        value (:obj:float, optional): Cohen's d for effect size.
        
    Returns:
        Optional[str]: An interpretation of the effect-size value, if value is not None. Otherwise, returns None.
    """
    if value is None:
        return None
    if abs(value) < 0.2:
        return "negligible"
    elif abs(value) < 0.5:
        return "small"
    elif abs(value) < 0.8:
        return "medium"
    else:
        return "large"
    
def interpret_t_statistic(value: Optional[float]) -> Optional[str]:
    """
    Returns an interpretation of the t-statistic from Welch's test.

    Args:
        value (:obj:float, optional): T-statistic from Welch's test.
        
    Returns:
        Optinoal[str]: An interpretation of the value, if value is not None. Otherwise, returns None.
    """
    if value is None:
        return None
    if abs(value) < 2:
        return "not statistically significant"
    else:
        return "statistically significant"
    
def interpret_mean_diff_pct(value: Optional[float]) -> Optional[str]:
    """
    Returns an interpretation of the mean difference percentage.
    
    Args:
        value (Optional[float]): A mean difference percentage.
        group_a_label (Optional[str]): The label for group A.
        group_b_label (Optional[str]): The label for group B. This works as the reference.
        
    Returns:
        Optional[str]: An interpretation of the value, if the value is not None. Otherwise, returns None.
    """
    if value is None:
        return None
    if value < 0:
        return f"Group A was LOWER than Group B by {value}%."
    else:
        return f"Group A was HIGHER than Group B by {value}%."
        
        
PAT_A = re.compile(r'_a$')
PAT_B = re.compile(r'_b$')

def find_a_and_b(values: Iterable[str]) -> tuple[list[str], list[str]]:
    """
    Scan *values* and return two lists:
        • items that end with “_a”
        • items that end with “_b”

    Non‑string items are ignored.

    Args"
        values : Iterable[str]
            Any iterable (list, tuple, generator, …) containing strings.

    Returns:
        tuple[list[str], list[str]]
            (a_items, b_items)
    """
    a_items: list[str] = []
    b_items: list[str] = []

    for v in values:
        if not isinstance(v, str):
            continue                # skip non‑strings safely

        if PAT_A.search(v):
            a_items.append(v)
        elif PAT_B.search(v):
            b_items.append(v)

    return a_items, b_items
