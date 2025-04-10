def write_xml(data, indent_size=2):
    """
    Convert JSON data to XML with each attribute on a new line

    Parameters:
    - json_data: Dictionary representing JSON data
    - indent_size: Number of spaces for each indentation level

    Returns: formatted XML string
    """
    result = []
    result.append('<?xml version="1.0" encoding="UTF-8"?>')

    def _process_element(element_name, element_data, indent_level=0):
        lines = []
        indent = "    " * indent_level

        # Start tag
        opening = f"{indent}<{element_name}"

        # Check for attributes
        attributes = {}
        if "@attributes" in element_data:
            attributes = element_data["@attributes"]

        if attributes:
            lines.append(opening)
            attr_indent = " " * len(opening)

            # Add each attribute on a new line
            attr_items = list(attributes.items())
            for i, (key, value) in enumerate(attr_items):
                lines.append(f"{attr_indent}{key}=\"{value}\"")

            # Close the opening tag after the last attribute
            lines[-1] += ">"
        else:
            lines.append(f"{opening}>")

        # Process child elements and text content
        for key, value in element_data.items():
            # Skip attributes as they are already processed
            if key == "@attributes":
                continue

            # Handle comments
            elif key == "Comment":
                lines.append(f"{indent}{' ' * indent_size}<!-- {value} -->")

            # Handle arrays/lists
            elif isinstance(value, list):
                for item in value:
                    child_lines = _process_element(key, item, indent_level + indent_size)
                    lines.extend(child_lines)

            # Handle nested objects
            elif isinstance(value, dict):
                child_lines = _process_element(key, value, indent_level + indent_size)
                lines.extend(child_lines)

            # Handle simple values (text content)
            else:
                lines.append(f"{indent}{' ' * indent_size}{value}")

        # End tag
        lines.append(f"{indent}</{element_name}>")
        return lines

    # Process the root element (there should be only one)
    root_name = next(iter(data))
    result.extend(_process_element(root_name, data[root_name]))

    return "\n".join(result)
