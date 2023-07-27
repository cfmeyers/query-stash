import math
import re
from datetime import datetime
from decimal import Decimal
from typing import Callable, List, NamedTuple, Optional, Sequence

from query_stash.types import RowDict

NULL_CHAR = "∅"
COMMA_SUBSTRINGS = (
    "sum",
    "count",
    "total",
    "num",
    "SUM",
    "COUNT",
    "TOTAL",
    "NUM",
    "ct",
    "CT",
)


def pretty_datetime(d: Optional[datetime]) -> str:
    if d == NULL_CHAR or d is None:
        return NULL_CHAR.center(19)
    hours_minutes_seconds = d.strftime("%H:%M:%S")
    pretty = d.strftime(f"%Y-%m-%d {hours_minutes_seconds}")
    return pretty.ljust(19)


def pretty_money(amount) -> str:
    rounded_str = "${0:,.2f}".format(amount)
    return rounded_str


def pretty_generic_decimal(amount) -> str:
    if amount == NULL_CHAR:
        return NULL_CHAR
    rounded_str = "{0:,.8f}".format(amount)
    no_trailing_zeros = rounded_str.rstrip("0")
    if no_trailing_zeros[-1] == ".":
        return no_trailing_zeros + "0"
    return no_trailing_zeros
    # return rounded_str


def pretty_int(amount) -> str:
    int_str = "{0:,.0f}".format(amount)
    return int_str

def is_nan(item):
    try:
        return math.isnan(item)
    except:
        return False

class ColumnSpec(NamedTuple):
    """An object that renders all the values for a particular column in a table"""

    name: str
    func: Callable = lambda x: x
    width: int = 10

    def transform(self, item, width: Optional[int] = None) -> str:
        if width is None:
            width = self.width
        if item is None or is_nan(item):
            item = NULL_CHAR
        transformed = self.func(item)
        if type(transformed) != str:
            transformed = str(transformed)
        transformed = transformed.replace("\n", "")  # for arrays, variants/json
        if len(transformed) <= width:
            return transformed.ljust(width)
        else:
            truncated = transformed[: width - 1] + "…"
            return truncated.ljust(width)


def get_clean_headers(original_headers: List[str]) -> List[str]:
    cleaned_headers = []
    for header in original_headers:
        cleaned_header = header.replace("(*)", "")
        cleaned_header = re.sub(r"\W", "_", header)
        cleaned_header = cleaned_header.strip("_")
        cleaned_headers.append(cleaned_header)
    return cleaned_headers


def clean_column_headers_for_rows(old_rows: List[RowDict]) -> List[RowDict]:
    rows = old_rows.copy()
    headers = list(old_rows[0].keys())
    cleaned_headers = get_clean_headers(headers)
    for row in rows:
        for old_header, new_header in zip(headers, cleaned_headers):
            if old_header != new_header:
                row[new_header] = row.pop(old_header)
    return rows


def should_be_formatted_with_commas(column_name: str) -> bool:
    comma_keywords = "|".join(COMMA_SUBSTRINGS)
    starts_with_comma_word = bool(re.search("^(" + comma_keywords + ")_?", column_name))
    ends_with_comma_word = bool(re.search("_(" + comma_keywords + ")$", column_name))
    ends_with_s = bool(re.search(r"s$", column_name))
    return starts_with_comma_word or ends_with_comma_word or ends_with_s


def get_max_width_of_items(items, with_commas=False) -> int:
    max_width = 0
    if with_commas:
        string_function = pretty_int
    else:
        string_function = str
    for item in items:
        try:
            item_length = len(string_function(item))
        except:
            item_length = len(str(item))
        if item_length > max_width:
            max_width = item_length
    return max_width


class RenderedTable(NamedTuple):
    """
    An object that knows how to render its rows (list of dicts)

    Can turn:
        rows = [
            {"id": 1, "name": "Sam"},
            {"id": 2, "name": "Layla"},
            {"id": 3, "name": "Jack Gabriel"},
        ]

    into:
        | id   | name     |
        | ---- | -------- |
        | 1    | Sam      |
        | 2    | Layla    |
        | 3    | Jack Ga… |
        | ---- | -------- |
    """

    column_specs: Sequence[ColumnSpec]
    rows: List[RowDict]

    @property
    def headers(self):
        return self.rows[0].keys()

    def _join_items_to_pipes(self, items: List[str]) -> str:
        inner_cols = " | ".join(i for i in items)
        return f"| {inner_cols} |"

    @property
    def header_row(self) -> str:
        header_row_items = []
        for col_spec, header in zip(self.column_specs, self.headers):
            width = col_spec.width
            if len(header) <= width:
                header_row_items.append(header.ljust(width).lower())
            else:
                truncated_header = header[: width - 1] + "…"
                header_row_items.append(truncated_header.ljust(width))
        return self._join_items_to_pipes(header_row_items)

    @property
    def break_line(self) -> str:
        break_line_items = []
        for col_spec in self.column_specs:
            col_break_line = "-" * col_spec.width
            break_line_items.append(col_break_line)
        return self._join_items_to_pipes(break_line_items)

    def make_printable_row(self, row: RowDict) -> str:
        row_items = []
        for col_spec, item in zip(self.column_specs, row.values()):
            row_items.append(col_spec.transform(item))
        return self._join_items_to_pipes(row_items)

    @property
    def printable_rows(self) -> str:
        return "\n".join(self.make_printable_row(row) for row in self.rows)

    def __str__(self):
        return f"""\
{self.header_row}
{self.break_line}
{self.printable_rows}
{self.break_line}"""

    def __getitem__(self, position):
        return self.rows[position]

    def __len__(self):
        return len(self.rows)


class RenderedPivotedTable(NamedTuple):
    """
    An object that knows how to render its rows (list of dicts)

    Can turn:
        rows = [
            {"id": 1, "name": "Sam"},
        ]

    into:
        | ---- | --- |
        | id   | 1   |
        | name | Sam |
        | ---- | --- |
    """

    column_specs: Sequence[ColumnSpec]
    rows: List[RowDict]

    @property
    def keys(self):
        return list(self.rows[0].keys())

    @property
    def key_column_width(self):
        return max(len(x) for x in self.keys)

    @property
    def values(self):
        return list(self.rows[0].values())

    @property
    def values_column_width(self):
        return max(cs.width for cs in self.column_specs)

    def _join_items_to_pipes(self, items: List[str]) -> str:
        inner_cols = " | ".join(i for i in items)
        return f"| {inner_cols} |"

    @property
    def break_line(self) -> str:
        key_line = "-" * self.key_column_width
        value_line = "-" * self.values_column_width
        return f"| {key_line} | {value_line} |"

    def make_printable_row(self, col_spec: ColumnSpec) -> str:
        row = self.rows[0]
        key = col_spec.name.ljust(self.key_column_width).lower()
        value = col_spec.transform(row[col_spec.name], width=self.values_column_width)
        return self._join_items_to_pipes([key, value])

    @property
    def printable_rows(self) -> str:
        return "\n".join(
            self.make_printable_row(col_spec) for col_spec in self.column_specs
        )

    def __str__(self):
        return f"""\
{self.break_line}
{self.printable_rows}
{self.break_line}"""

    def __getitem__(self, position):
        return self.rows[position]

    def __len__(self):
        return len(self.rows)

def guess_column_type(rows: List[RowDict], column_name: str):
    """Hack because pandas (for duckdb connector) mixes float and str types"""
    first_row_type = type(rows[0][column_name])
    last_row_type = type(rows[-1][column_name])
    if str in (first_row_type, last_row_type):
        return str
    else:
        return first_row_type

def get_rendered_table(rows: List[RowDict]) -> RenderedTable:
    """Get a RenderedTable with standard ColumnSpecs
    - comma-formatted integer columns
    - cleanly-formatted datetimes
    """
    rows = clean_column_headers_for_rows(rows)
    col_specs = []
    column_names = rows[0].keys()
    for column_name in column_names:
        column_type = guess_column_type(rows, column_name)
        values = [r[column_name] for r in rows if r[column_name] is not None]
        if column_type == datetime:
            spec = ColumnSpec(column_name, width=19, func=pretty_datetime)
        elif column_type in (Decimal, float):
            spec = ColumnSpec(
                column_name,
                # width=get_max_width_of_items([column_name] + values) + 6,
                width=get_max_width_of_items([column_name] + values),
                func=pretty_generic_decimal,
            )
        elif column_type == int and should_be_formatted_with_commas(column_name):
            spec = ColumnSpec(
                column_name,
                width=get_max_width_of_items([column_name] + values, with_commas=True),
                func=pretty_int,
            )

        elif column_type == int:
            spec = ColumnSpec(
                column_name, width=get_max_width_of_items([column_name] + values)
            )
        else:
            spec = ColumnSpec(
                column_name, width=get_max_width_of_items([column_name] + values)
            )
        col_specs.append(spec)
    if len(rows) == 1:
        return RenderedPivotedTable(column_specs=col_specs, rows=rows)
    else:
        return RenderedTable(column_specs=col_specs, rows=rows)
