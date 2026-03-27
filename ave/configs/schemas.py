"""Per-category attribute schemas for the WDC-PAVE benchmark.

Each category maps to a fixed list of attribute names.  During gold JSON
construction every attribute in the schema appears as a key; missing
attributes are set to ``null``.
"""

CATEGORY_SCHEMAS: dict[str, list[str]] = {
    "Computers And Accessories": [
        "Generation",
        "Part Number",
        "Product Type",
        "Cache",
        "Processor Type",
        "Processor Core",
        "Interface",
        "Manufacturer",
        "Capacity",
        "Ports",
        "Rotational Speed",
    ],
    "Home And Garden": [
        "Product Type",
        "Color",
        "Length",
        "Width",
        "Height",
        "Depth",
        "Manufacturer Stock Number",
        "Retail UPC",
    ],
    "Office Products": [
        "Product Type",
        "Color(s)",
        "Pack Quantity",
        "Length",
        "Width",
        "Height",
        "Depth",
        "Paper Weight",
        "Manufacturer Stock Number",
        "Retail UPC",
    ],
    "Jewelry": [
        "Product Type",
        "Brand",
        "Model Number",
    ],
    "Grocery And Gourmet Food": [
        "Product Type",
        "Brand",
        "Pack Quantity",
        "Retail UPC",
        "Size/Weight",
    ],
}


def build_json_schema(category: str) -> dict:
    """Build a JSON Schema for constrained decoding of *category*'s output.

    Each attribute value may be ``null``, a ``string``, or an ``array``
    of ≥ 2 strings (multi-value).
    """
    attrs = CATEGORY_SCHEMAS[category]
    properties = {}
    for attr in attrs:
        properties[attr] = {
            "oneOf": [
                {"type": "null"},
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}, "minItems": 2},
            ]
        }
    return {
        "type": "object",
        "properties": properties,
        "required": attrs,
        "additionalProperties": False,
    }


def all_json_schemas() -> dict[str, dict]:
    """Return ``{category: json_schema}`` for every category."""
    return {cat: build_json_schema(cat) for cat in CATEGORY_SCHEMAS}
