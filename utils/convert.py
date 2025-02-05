def convert_column_name(column_str):
    """
    Convert column names to a standardized format.
    """
    if column_str == "순위":
        return None
    column_map = {
        "선수명": "P_NM",
        "팀명": "TEAM_NM",
        "타수": "AB",
        "안타": "H",
        "타점": "RBI",
        "득점": "R",
        "타율": "AVG",
        "등판": "POS",
        "결과": "W/L",
        "승": "W",
        "패": "L",
        "세": "SV",
        "이닝": "IP",
        "타자": "TBF",
        "투구수": "NP",
        "피안타": "H",
        "홈런": "HR",
        "4사구": "BB",
        "삼진": "SO",
        "실점": "R",
        "자책": "ER",
        "평균자책점": "ERA",
    }
    return column_map.get(column_str, column_str.upper())

def convert_to_data(fraction_str):
    """
    Convert a fraction string to a decimal number. If the input is not in fraction format, 
    convert it to float or string as needed.
    """
    if not isinstance(fraction_str, str):  
        return fraction_str

    fraction_str = fraction_str.strip()

    if fraction_str == "-" or fraction_str == "&nbsp;":
        return None

    try:
        if ' ' in fraction_str and '/' in fraction_str:
            whole, fraction = fraction_str.split(' ')
            numerator, denominator = map(int, fraction.split('/'))
            decimal_value = int(whole) + (numerator / denominator)
            return round(decimal_value, 2)

        if '/' in fraction_str:
            numerator, denominator = map(int, fraction_str.split('/'))
            return round(numerator / denominator, 2)

        if ',' in fraction_str:
            cleaned_number = fraction_str.replace(",", "")
            if cleaned_number.isdigit():
                return int(cleaned_number)
            
        if fraction_str.isdigit():
            return int(fraction_str)
            
        return float(fraction_str)

    except ValueError:
        return fraction_str

def convert_row_data(headers, values):
    """
    Convert a list of headers and corresponding row values into a standardized dictionary.
    """
    converted_data = {}
    for header, value in zip(headers, values):
        column_name = convert_column_name(header)
        if column_name:
            converted_data[column_name] = convert_to_data(value)
    return converted_data
