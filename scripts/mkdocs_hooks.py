"""
MkDocs hooks to convert Terraform-style callouts to MkDocs admonitions.

Converts:
  -> **Note:** text     → !!! note
  ~> **Note:** text     → !!! warning
  !> **Warning:** text  → !!! danger
"""

import re


def on_page_markdown(markdown, page, config, files):
    """
    Process markdown to convert Terraform callouts before rendering.

    This hook is automatically called by MkDocs for each page.
    """
    # Pattern to match Terraform callouts at start of line
    pattern = r"^(->|~>|!>)\s+\*\*([^*]+):\*\*\s+(.+)$"

    def replace_callout(match):
        sigil = match.group(1)
        title_text = match.group(2)  # e.g., "Note" or "Warning"
        content = match.group(3)

        # Map Terraform sigils to MkDocs admonition types
        sigil_map = {
            "->": "note",  # Blue
            "~>": "warning",  # Orange/yellow
            "!>": "danger",  # Red
        }

        admonition_type = sigil_map.get(sigil, "note")

        # Build MkDocs admonition with proper indentation
        return f'!!! {admonition_type} "{title_text}"\n\n    {content}'

    # Process line by line
    lines = markdown.split("\n")
    result_lines = []

    for line in lines:
        match = re.match(pattern, line)
        if match:
            result_lines.append(replace_callout(match))
        else:
            result_lines.append(line)

    return "\n".join(result_lines)
