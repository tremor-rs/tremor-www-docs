from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import json
import sys
from pathlib import Path
from io import StringIO

PREFIX = """
## Document Status

Work in Progress

## Well known API endpoints

This document summarises the Tremor REST API
"""

ENDPOINT_TABLE_HEADER = """
|Url|Description|
|---|---|
"""


def main():
    openyaml_path = Path(sys.argv[-1])
    if not openyaml_path.exists():
        raise Exception(f"\"{openyaml_path}\" does not exist.")
    with openyaml_path.open() as openyaml:
        api = load(openyaml, Loader=Loader)

    data = StringIO()
    data.write(PREFIX)
    data.write(ENDPOINT_TABLE_HEADER)

    for server in api["servers"]:
        url = server.get("url", "No URL.")
        description = server.get("description", "No description.")
        data.write(f"|{url}|{description}|\n")
    data.write("\n\n")
    data.write("""
## Paths

The endpoint paths supported by the Tremor REST API

    """)
    for path, methods in api["paths"].items():
        for method, endpoint in methods.items():
            summary = endpoint.get("summary", "No summary.")
            description = endpoint.get("description", "No description.")
            operation_id = endpoint.get("operationId", "No operationId.")
            returns = endpoint.get("responses")
            data.write(f"""
### __{method.upper()}__ {path}

{summary}

*Description:*

{description}

*OperationId:*

{operation_id}

*Returns:*

> |Status Code|Content Type|Schema Type|
> |---|---|---|
""")
            for code, ret in returns.items():
                content_types = ret.get("content", {})
                if len(content_types) == 0:
                    data.write(f"> |{code}|empty|no content|\n")
                else:
                    for content_type, content in content_types.items():
                        schema_type = content["schema"]["$ref"]
                        schema_name = schema_type.split("/")[-1]

                        data.write(
                            f"> |{code}|{content_type}|[{schema_type}](#schema-{schema_name})|\n")
            data.write("\n")
    # write schemas
    data.write("""
## Schemas

JSON Schema for types defioned in the Tremor REST API
    """)
    schemas = api.get("components", {}).get("schemas", {})
    for schema_name, schema in schemas.items():
        description = schema.get("description", "No description.")
        data.write(f"""
### Schema for type: __{schema_name}__
<a name="schema-{schema_name}"></a>

{description}

```json
""")
        schema = json.dumps(schema, indent=4, sort_keys=True)
        data.write(schema)
        data.write("\n```\n")

    print(data.getvalue())


if __name__ == "__main__":
    main()
