def get_price_row_template():
    return """
    <tr>
        <td style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;"><strong>{pair}</strong></td>
        <td style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">${min_price:,.2f}</td>
        <td style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">${max_price:,.2f}</td>
        <td style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">${current:,.2f}</td>
        <td style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd; color: {color}; font-weight: 600;">{change_text}</td>
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
    return '<tr><td style="padding: 10px; text-align: left;">{pair}</td><td style="padding: 10px; text-align: left;">${price:,.2f}</td><td style="padding: 10px; text-align: left;">-</td><td style="padding: 10px; text-align: left;">-</td><td style="padding: 10px; text-align: left;">-</td></tr>'
