import json
from pathlib import Path

from poetry.core import json as poetry_json

SCHEMA_FILE_NAME = "poetry-schema.json"


def main():
    poetry_schema_path = Path(poetry_json.SCHEMA_DIR) / SCHEMA_FILE_NAME
    if not poetry_schema_path.exists():
        raise ValueError(f"{poetry_schema_path} does not exist")

    content = json.loads(poetry_schema_path.read_text())
    content["properties"]["workspace"] = {
        "type": "object",
        "description": "Information about the Poetry workspace.",
        "additionalProperties": False,
        "properties": {
            "include": {
                "type": "array",
                "description": "A list of folders to include.",
            },
            "exclude": {
                "type": "array",
                "description": "A list of folders to exclude.",
            },
        },
    }

    plugin_schema_path = Path(__file__).parent / SCHEMA_FILE_NAME
    plugin_schema_path.write_text(json.dumps(content, indent=2))


if __name__ == "__main__":
    main()
