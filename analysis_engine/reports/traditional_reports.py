from typing import Optional

from analysis_engine.contracts import HormoneAnalysisResult


def build_descriptive_hormone_report(result: HormoneAnalysisResult) -> dict[str, Optional[str]]:
    summary = result.summary or {}
    tables_by_name = {table["name"]: table["rows"] for table in result.tables} 

    hormone_rows = tables_by_name.get("hormone_statistics", [])
    hormone_performance_rows = tables_by_name.get("hormone_performance_statistics", [])
    hormone_dysmenorrhea_rows = tables_by_name.get("hormone_dysmenorrhea_statistics", [])
    hormone_dysmenorrhea_performance_rows = tables_by_name.get("hormone_dysmenorrhea_performance_statistics", [])

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
            lines.append(f"\t- n={row['observation_count']} ")
            lines.append(f"\t- mean={row['mean']}, median={row['median']}, sd={row['standard_deviation']}")

    if hormone_performance_rows:
        lines.extend(["", "## Hormone by Performance Type"])
        for row in sorted(
            hormone_performance_rows,
            key=lambda item: (item["performance_type"], item["hormone_name"]),
        ):
            lines.append(f"- {row['hormone_name']} in '{row['performance_type']}': ")
            lines.append(f"\t- n={row['observation_count']} ")
            lines.append(f"\t- mean={row['mean']}, median={row['median']}, sd={row['standard_deviation']}")

    if hormone_dysmenorrhea_rows:
        lines.extend(["", "## Hormone by Dysmenorrhea Presence"])
        for row in sorted(
            hormone_dysmenorrhea_rows,
            key=lambda item: (item["hormone_name"], item["dysmenorrhea_present"]),
        ):
            dys_label = "dysmenorrhea present" if row["dysmenorrhea_present"] else "dysmenorrhea absent"
            lines.append(f"- {row['hormone_name']} with {dys_label}: ")
            lines.append(f"\t- n={row['observation_count']} ")
            lines.append(f"\t- mean={row['mean']}, median={row['median']}, sd={row['standard_deviation']}")

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
            dys_label = "dysmenorrhea present" if row["dysmenorrhea_present"] else "dysmenorrhea absent"
            lines.append(f"- {row['hormone_name']} in '{row['performance_type']}' with {dys_label}: ")
            lines.append(f"\t- n={row['observation_count']} ")
            lines.append(f"\t- mean={row['mean']}, median={row['median']}, sd={row['standard_deviation']}")

    if result.conclusions:
        lines.extend(["", "## Conclusions"])
        for conclusion in result.conclusions[:12]:
            lines.append(f"- {conclusion}")

    hormones = sorted({row["hormone_name"] for row in hormone_rows})
    performance_types = sorted({row["performance_type"] for row in hormone_performance_rows})

    lines.extend(["",
                  "## Coverage",
                  f"- Hormones covered: {', '.join(hormones) if hormones else 'None'}",
                  f"- Performance types covered: {', '.join(performance_types) if performance_types else 'None'}"])
    
    return {"report_text": "\n".join(lines),
            "summary_text": summary_text,}
