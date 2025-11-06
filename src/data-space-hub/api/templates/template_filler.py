import re
import json
from typing import Dict, Any

_PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

def render_json_template_string(template: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render a JSON template stored as a Python string with placeholders like {issuer}, {vc}, {issued_at}.
    - Replaces only placeholders matching {name} where name matches [A-Za-z_][A-Za-z0-9_]*
    - Replacement values are json.dumps(value, ensure_ascii=False) so types are preserved (dict -> object, str -> "string").
    - Finally parses the rendered text with json.loads and returns the dict/list.
    Raises json.JSONDecodeError if rendered text is not valid JSON.
    """
    def _repl(m: re.Match) -> str:
        key = m.group(1)
        if key not in context:
            # choose behaviour: raise KeyError so caller notices missing placeholder
            raise KeyError(f"Missing template context key: {key}")
        # json.dumps ensures proper escaping / quoting / types
        return json.dumps(context[key], ensure_ascii=False)

    rendered = _PLACEHOLDER_RE.sub(_repl, template)
    print(rendered)
    # parse to validate and return structured object
    return json.loads(rendered)