def write_xml(root_element, indent_size=2, xml_declaration=True):
    """
    Write an XML structure with attributes on separate lines

    Parameters:
    - root_element: dict with keys:
        - 'tag': element name (string)
        - 'attributes': dict of attributes (optional)
        - 'text': element text content (optional)
        - 'children': list of child elements with same structure (optional)
    - indent_size: number of spaces for each indentation level
    - xml_declaration: whether to include XML declaration

    Returns: formatted XML string
    """
    result = []

    if xml_declaration:
        result.append('<?xml version="1.0" encoding="UTF-8"?>')

    def _write_element(element, indent_level=0):
        indent = " " * indent_level
        lines = []

        # Start tag
        tag_name = element['tag']
        opening = f"{indent}<{tag_name}"

        attributes = element.get('attributes', {})
        if attributes:
            lines.append(opening)
            attr_indent = " " * len(opening)

            # Add each attribute on a new line
            attr_items = list(attributes.items())
            for i, (key, value) in enumerate(attr_items):
                # Escape attribute values
                escaped_value = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"",
                                                                                                                   "&quot;")
                attr_line = f"{attr_indent}{key}=\"{escaped_value}\""
                if i == len(attr_items) - 1:  # Last attribute
                    attr_line += ">"
                lines.append(attr_line)
        else:
            lines.append(f"{opening}>")

        # Element content
        if 'text' in element and element['text']:
            # Escape text content
            text = str(element['text'])
            escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            lines.append(f"{indent}{' ' * indent_size}{escaped_text}")

        # Process children
        children = element.get('children', [])
        for child in children:
            child_lines = _write_element(child, indent_level + indent_size)
            lines.extend(child_lines)

        # End tag
        lines.append(f"{indent}</{tag_name}>")

        return lines

    result.extend(_write_element(root_element))
    return "\n".join(result)


# Example usage
if __name__ == "__main__":
    # Example XML structure
    document = {
        'tag': 'root',
        'attributes': {
            'version': '1.0'
        },
        'children': [
            {
                'tag': 'person',
                'attributes': {
                    'id': '123',
                    'firstName': 'John',
                    'lastName': 'Doe',
                    'age': '30',
                    'email': 'john.doe@example.com'
                },
                'text': 'This is a person element'
            },
            {
                'tag': 'metadata',
                'attributes': {
                    'created': '2025-04-10',
                    'modified': '2025-04-10',
                    'author': 'XMLWriter'
                }
            }
        ]
    }

    xml_output = write_xml(document)
    print(xml_output)
