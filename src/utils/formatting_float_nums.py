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
    
def pretty_edit(old, new, suffix=""):
    old_str = pretty_num(old)
    if new is not None:
        new_str = pretty_num(new)
        return f"<i>{old_str}</i>{suffix} → <i>{new_str}</i>{suffix}"
    else:
        return f"<i>{old_str}</i>{suffix}"