from typing import Optional

from analysis_engine.contracts import HormoneAnalysisResult

def build_descriptive_hormone_report(result: HormoneAnalysisResult) -> dict[str, Optional[str]]:
    summary = result.summary or {}
    tables_by_name = {table["name"]: table["rows"] for table in result.tables} 

    hormone_rows = tables_by_name.get("hormone_statistics", [])
    hormone_performance_rows = tables_by_name.get("hormone_performance_statistics", [])
    hormone_dysmenorrhea_rows = tables_by_name.get("hormone_dysmenorrhea_statistics", [])
    hormone_dysmenorrhea_performance_rows = tables_by_name.get("hormone_dysmenorrhea_performance_statistics", [])
    comparative_hormone_performance_rows = tables_by_name.get("comparative_hormone_performance_statistics", [])
    comparative_hormone_dysmenorrhea_rows = tables_by_name.get("comparative_hormone_dysmenorrhea_statistics", [])
    comparative_hormone_dysmenorrhea_performance_rows = tables_by_name.get("comparative_hormone_dysmenorrhea_performance_statistics", [])

    summary_text = (f"Descriptive hormone analysis produced "
                    f"{summary.get('total_grouped_row_count', 0)} grouped summaries across "
                    f"{summary.get('hormone_row_count', 0)} hormones.")
    
    lines = ["# Traditional Descriptive Hormone Report",
             "",
             summary_text,
             "",
             "## Overview",
             f"- Hormone observations: {summary.get('hormone_row_count', 0)}",
             f"- Hormone + performance observations: {summary.get('hormone_performance_row_count', 0)}",
             f"- Hormone + dysmenorrhea observations: {summary.get('hormone_dysmenorrhea_row_count', 0)}",
             f"- Hormone + dysmenorrhea + performance observations: {summary.get('hormone_dysmenorrhea_performance_row_count', 0)}"]
    
    if hormone_rows:
        lines.extend(["",
                      "## Hormone Summary"])
        for row in sorted(hormone_rows,
                          key=lambda item: item["hormone_name"]):
            lines.append(f"- {row['hormone_name']}: ")
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
            dys_label_a = "dysmenorrhea present" if str(row.get("dysmenorrhea_present_a")).lower() == "true" else "dysmenorrhea absent"
            dys_label_b = "dysmenorrhea present" if str(row.get("dysmenorrhea_present_b")).lower() == "true" else "dysmenorrhea absent"
            lines.append(f"- {row['hormone_name']} in ['{dys_label_a}', '{dys_label_b}'] "
                            f"comparing performance types ['{row.get('performance_type_a', 'Unknown')}', '{row.get('performance_type_b', 'Unknown')}']")
            lines.extend(create_multiple_parameter_summary_states_lines(row))

    if result.conclusions:
        lines.extend(["", "## Conclusions"])
        for conclusion in result.conclusions:
            lines.append(f"- {conclusion}")

    hormones = sorted({row["hormone_name"] for row in hormone_rows})
    performance_types = sorted({row["performance_type"] for row in hormone_performance_rows})

    lines.extend(["",
                  "## Coverage",
                  f"- Hormones covered: {', '.join(hormones) if hormones else 'None'}",
                  f"- Performance types covered: {', '.join(performance_types) if performance_types else 'None'}"])
    
    return {"report_text": "\n".join(lines),
            "summary_text": summary_text,}

# HELPERS
def create_single_parameter_summary_stats_lines(row) -> list:
    lines = []
    lines.append(f"\t- n={row['observation_count']} ")
    lines.append(f"\t- mean={row['mean']}, median={row['median']}, sd={row['standard_deviation']}")
    return lines

def create_multiple_parameter_summary_states_lines(row) -> list:
    lines = []
    lines.append(f"\t- n={row['observation_count']} ")
    lines.append(f"\t- cohen's d={row['cohens_d']}, independent t={row['independent_t']}")
    lines.append(f"\t- cohen's d interpretation: {interpret_cohen(row['cohens_d'])}"
                 f"\t- independent t interpretation: {interpret_t_statistic(row['independent_t'])}")
    return lines

def create_dysmenorrhea_label(row) -> str:
    if "dysmenorrhea_present" in row.keys():
        return "dysmenorrhea present" if row["dysmenorrhea_present"] else "dysmenorrhea absent"
    if "dysmenorrhea_present_a" in row.keys() and "dysmenorrhea_present_b" in row.keys():
        return "dysmenorrhea present" if row["dysmenorrhea_present_a"] else "dysmenorrhea absent", \
            "dysmenorrhea present" if row["dysmenorrhea_present_b"] else "dysmenorrhea absent"
    
def interpret_cohen(value: Optional[float]) -> Optional[str]:
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
    if value is None:
        return None
    if abs(value) < 2:
        return "not statistically significant"
    else:
        return "statistically significant"
