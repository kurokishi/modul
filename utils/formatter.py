# utils/formatter.py
def format_rupiah(value):
    try:
        return f"Rp {value:,.0f}"
    except:
        return value

def format_percentage(value):
    try:
        return f"{value:.2f}%"
    except:
        return value

def color_negative_red(val):
    if isinstance(val, str) and '%' in val:
        try:
            num_val = float(val.replace('%', ''))
            color = 'red' if num_val < 0 else 'green'
        except:
            color = 'black'
    elif isinstance(val, str) and 'Rp' in val:
        try:
            num_val = float(val.replace('Rp', '').replace(',', '').strip())
            color = 'red' if num_val < 0 else 'green'
        except:
            color = 'black'
    else:
        color = 'black'
    return f'color: {color}'
