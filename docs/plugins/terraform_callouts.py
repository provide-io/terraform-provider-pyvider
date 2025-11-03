"""
MkDocs plugin to convert Terraform-style callouts to MkDocs admonitions.

Converts:
  -> **Note:** text     → !!! note
  ~> **Note:** text     → !!! warning
  !> **Warning:** text  → !!! danger
"""
import re
from mkdocs.plugins import BasePlugin


class TerraformCalloutsPlugin(BasePlugin):
    """Convert Terraform callouts to MkDocs admonitions."""

    def on_page_markdown(self, markdown, **kwargs):
        """
        Process markdown to convert Terraform callouts.

        Terraform callout format:
          -> **Note:** This is a note (blue)
          ~> **Note:** This is a warning (yellow/orange)
          !> **Warning:** This is danger (red)

        MkDocs admonition format:
          !!! note
              This is a note
        """
        # Pattern to match Terraform callouts at start of line
        # Captures: sigil (-> ~> !>) and the rest of the line
        pattern = r'^(->|~>|!>)\s+\*\*([^*]+):\*\*\s+(.+)$'

        def replace_callout(match):
            sigil = match.group(1)
            title_text = match.group(2)  # e.g., "Note" or "Warning"
            content = match.group(3)

            # Map Terraform sigils to MkDocs admonition types
            sigil_map = {
                '->': 'note',      # Blue
                '~>': 'warning',   # Orange/yellow
                '!>': 'danger'     # Red
            }

            admonition_type = sigil_map.get(sigil, 'note')

            # Build MkDocs admonition
            # Use empty title ("") to show icon without custom title text
            return f'!!! {admonition_type} "{title_text}"\n\n    {content}'

        # Process line by line to handle multi-line properly
        lines = markdown.split('\n')
        result_lines = []

        for line in lines:
            match = re.match(pattern, line)
            if match:
                result_lines.append(replace_callout(match))
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)
