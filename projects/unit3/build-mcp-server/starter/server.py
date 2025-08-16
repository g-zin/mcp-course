#!/usr/bin/env python3
"""
Module 1: Basic MCP Server - Starter Code
TODO: Implement tools for analyzing git changes and suggesting PR templates
"""

import json
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("pr-agent")

# PR template directory (shared across all modules)
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


@mcp.tool()
async def analyze_file_changes(base_branch: str = "main", include_diff: bool = True, max_diff_lines: int=500) -> str:

    try:
        result = subprocess.run(
            ["git","diff",f"{base_branch}...HEAD"],
            capture_output=True,
            text=True
        )
        diff_output = result.stdout
        diff_lines = diff_output.split('\n')
        
        if len(diff_lines) > max_diff_lines:
            truncated_diff = '\n'.join(diff_lines[:max_diff_lines])
            truncated_diff += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
            diff_output = truncated_diff
        
        stats_result = subprocess.run(
            ["git","diff","--stat",f"{base_branch}...HEAD"],
            capture_output=True,
            text=True
        )
        
        # Temporary placeholder for changed files
        files_changed = []  

        return json.dumps({
            "stats": stats_result.stdout,
            "total_lines": len(diff_lines),
            "diff": diff_output if include_diff else "Use include_diff=true to see diff",
            "files_changed": files_changed
        })
    except Exception as e:
        return json.dumps({"error": str(e)})
   


@mcp.tool()
async def get_pr_templates() -> str:
    """List available PR templates with their content."""
   
    templates = {}
    for template_file in TEMPLATES_DIR.glob("*.md"):
        templates[template_file.name] = template_file.read_text()
    return json.dumps(templates, indent=2)
    



@mcp.tool()
async def suggest_template(changes_summary: str, change_type: str) -> str:
    """Let Claude analyze the changes and suggest the most appropriate PR template."""
    # Example: simple mapping
    template_mapping = {
        "bug": "bugfix_template.md",
        "feature": "feature_template.md",
        "docs": "docs_template.md",
        "refactor": "refactor_template.md",
        "test": "test_template.md"
    }
    template_file = template_mapping.get(change_type, "default_template.md")
    template_path = TEMPLATES_DIR / template_file
    if template_path.exists():
        return json.dumps({"template_name": template_file, "content": template_path.read_text()})
    else:
        return json.dumps({"error": "Template not found", "hint": f"Expected {template_file}"})


if __name__ == "__main__":
    mcp.run(transport='stdio')