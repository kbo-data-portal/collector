from logger import get_logger

logger = get_logger()


def convert_column_name(column_name: str) -> str | None:
    """
    Converts a column name to a standardized column key.

    Args:
        column_name (str): The original column name.

    Returns:
        str | None: The converted column name in format,
                    or None if the column should be skipped.
    """
    if column_name in ["순위", "A_INITIAL_LK", "H_INITIAL_LK"]:
        return None

    column_mapping: dict[str, str] = {
        "선수명": "P_NM",
        "팀명": "TEAM_NM",
        "타수": "AB",
        "안타": "H",
        "타점": "RBI",
        "득점": "R",
        "타율": "AVG",
        "등판": "POS",
        "결과": "W_L",
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
        "날짜": "G_DT",
        "요일": "DAY_NM",
        "홈": "HOME_NM",
        "방문": "AWAY_NM",
        "구장": "S_NM",
        "관중수": "S_CNT",
        "상대": "OPP",
        "구분": "SIT",
    }

    return column_mapping.get(
        column_name,
        column_name.replace("/", "_").replace("-", "_").replace(" ", "_").upper(),
    )


def convert_to_data(value) -> float | int | str | None:
    """
    Converts a string (including fractions or formatted numbers) into float or int if possible.

    Args:
        value (str | any): The value to convert, typically a string from HTML.

    Returns:
        float | int | str | None: The converted number, or the original value on failure.
    """
    if not isinstance(value, str):
        return value

    value = value.strip()
    if value in {"", "-", "&nbsp;"}:
        return None

    try:
        # Case: mixed number like '1 1/3'
        if " " in value and "/" in value:
            whole, fraction = value.split(" ")
            numerator, denominator = map(int, fraction.split("/"))
            return round(int(whole) + (numerator / denominator), 2)

        # Case: simple fraction like '2/3'
        if "/" in value:
            numerator, denominator = map(int, value.split("/"))
            return round(numerator / denominator, 2)

        # Case: number with comma (e.g., "1,234")
        if "," in value:
            cleaned = value.replace(",", "")
            if cleaned.isdigit():
                return int(cleaned)

        # Case: digit string (e.g., "123")
        if value.isdigit():
            return int(value)

        # Default: try float conversion (e.g., "12.34")
        return float(value)

    except ValueError:
        return value


def convert_row_data(
    headers: list[str], values: list[str]
) -> dict[str, float | int | str | None]:
    """
    Converts a row of raw HTML data into a dictionary with standardized keys and cleaned values.

    Args:
        headers (list[str]): List of Korean column names.
        values (list[str]): List of string values corresponding to the headers.

    Returns:
        dict[str, float | int | str | None]: Dictionary with standardized keys and cleaned values.
    """
    row_data = {}

    for header, value in zip(headers, values):
        key = convert_column_name(header)
        if key:
            row_data[key] = convert_to_data(value)

    return row_data
