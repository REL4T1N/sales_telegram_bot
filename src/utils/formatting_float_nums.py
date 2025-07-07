def pretty_num(val):
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    if isinstance(val, float):
        return f"{val:.2f}".rstrip('0').rstrip('.')
    if isinstance(val, (int, str)):
        return str(val)
    # Если это Decimal
    try:
        as_float = float(val)
        if as_float.is_integer():
            return str(int(as_float))
        return f"{as_float:.2f}".rstrip('0').rstrip('.')
    except Exception:
        return str(val)