def get_price_row_template():
    return """
    <tr>
        <td><strong>{pair}</strong></td>
        <td>${min_price:,.2f}</td>
        <td>${max_price:,.2f}</td>
        <td>${current:,.2f}</td>
        <td class="{change_class}">{change_text}</td>
    </tr>
    """


def get_graph_content_template(with_image=True):
    if with_image:
        return '<img src="{encoded_image}" alt="Bitcoin Price History Graph" />'
    else:
        return '<p style="color: #6c757d; font-style: italic;">Graph not available</p>'


def get_graph_container_template():
    return '<div style="text-align: center; margin: 20px 0;">{content}</div>'


def get_fallback_price_row_template():
    return "<tr><td>{pair}</td><td>${price:,.2f}</td></tr>"
