from datetime import datetime

from query_stash.render import (
    ColumnSpec,
    RenderedPivotedTable,
    RenderedTable,
    clean_column_headers_for_rows,
    get_clean_headers,
    get_rendered_table,
    pretty_datetime,
    should_be_formatted_with_commas,
)


class TestPrettyDateTime:
    def test_it_returns_readable_string_for_datetime_object(self):
        some_sunday = datetime(2019, 3, 10, 15, 27, 34, 18)
        assert "2019-03-10 15:27:34" == pretty_datetime(some_sunday)

    def test_it_returns_null_char_if_none(self):
        assert "         ∅         " == pretty_datetime(None)
        assert "         ∅         " == pretty_datetime("∅")


class TestColumnSpec:
    def test_it_has_name_and_width(self):
        column = ColumnSpec("id", width=4)
        assert "id" == column.name
        assert 4 == column.width

    def test_it_has_an_optional_func(self):
        column = ColumnSpec("id", width=4)
        assert "hello" == column.func("hello")
        assert "" == column.func("")
        assert 7 == column.func(7)

        func = lambda x: x.upper()
        column = ColumnSpec("id", width=4, func=func)
        assert "HELLO" == column.func("hello")


class TestGetCleanHeaders:
    def test_it_handles_count_with_star(self):
        headers = ["count(*)"]
        assert ["count"] == get_clean_headers(headers)

    def test_it_handles_count_distinct(self):
        headers = ["count(distinct wombats)"]
        assert ["count_distinct_wombats"] == get_clean_headers(headers)

    def test_it_handles_sum(self):
        headers = ["sum(wombats)"]
        assert ["sum_wombats"] == get_clean_headers(headers)


class TestCleanColumnHeaadesForRows:
    def test_it(self):
        rows = [{"id": 1, "count(distinct barcode)": 27596962761}]
        it = clean_column_headers_for_rows(rows)
        assert it == [{"id": 1, "count_distinct_barcode": 27596962761}]


class TestRenderedTable:
    @property
    def id_column(self):
        return ColumnSpec("id", width=4)

    @property
    def name_column(self):
        return ColumnSpec("name", width=8)

    @property
    def it(self):
        rows = [
            {"id": 1, "name": "Sam"},
            {"id": 2, "name": "Layla"},
            {"id": 3, "name": "Jack Gabriel"},
        ]

        column_specs = (self.id_column, self.name_column)
        return RenderedTable(column_specs=column_specs, rows=rows)

    def test_it_knows_how_to_format_the_header_row(self):
        assert "| id   | name     |" == self.it.header_row

    def test_it_knows_how_to_format_break_lines(self):
        assert "| ---- | -------- |" == self.it.break_line

    def test_it_knows_how_to_print_itself(self):
        expected = """\
| id   | name     |
| ---- | -------- |
| 1    | Sam      |
| 2    | Layla    |
| 3    | Jack Ga… |
| ---- | -------- |"""
        assert expected == str(self.it)


class TestRenderedPivotedTable:
    @property
    def id_column(self):
        return ColumnSpec("id", width=2)

    @property
    def name_column(self):
        return ColumnSpec("name", width=3)

    @property
    def it(self):
        rows = [
            {"id": 1, "name": "Sam"},
        ]

        column_specs = (self.id_column, self.name_column)
        return RenderedPivotedTable(column_specs=column_specs, rows=rows)

    def test_it_knows_key_columns(self):
        assert self.it.keys == ["id", "name"]

    def test_it_knows_key_column_width(self):
        assert self.it.key_column_width == 4

    def test_it_knows_vals_columns(self):
        assert self.it.values == [1, "Sam"]

    def test_it_knows_values_column_width(self):
        assert self.it.values_column_width == 3

    def test_it_can_calculate_a_break_line(self):
        assert self.it.break_line == "| ---- | --- |"

    def test_it_can_make_a_printable_row(self):
        actual = self.it.make_printable_row(self.id_column)
        assert "| id   | 1   |" == actual

        actual = self.it.make_printable_row(self.name_column)
        assert "| name | Sam |" == actual

    def test_it_knows_how_to_print_itself(self):
        expected = """\
| ---- | --- |
| id   | 1   |
| name | Sam |
| ---- | --- |"""
        assert expected == str(self.it)


class TestShouldBeFormattedWithCommas:
    def test_it_formats_count_columns_with_commas(self):
        assert should_be_formatted_with_commas("count(*)") is True
        assert should_be_formatted_with_commas("count_this_thing") is True
        assert should_be_formatted_with_commas("this_thing_count") is True

    def test_it_formats_sum_columns_with_commas(self):
        assert should_be_formatted_with_commas("sum(*)") is True
        assert should_be_formatted_with_commas("sum_this_thing") is True
        assert should_be_formatted_with_commas("this_thing_sum") is True

    def test_it_formats_total_columns_with_commas(self):
        assert should_be_formatted_with_commas("total") is True
        assert should_be_formatted_with_commas("total_this_thing") is True
        assert should_be_formatted_with_commas("total_groups") is True
        assert should_be_formatted_with_commas("this_thing_total") is True

    def test_it_formats_columns_that_end_with_s_with_commas(self):
        assert should_be_formatted_with_commas("groups") is True

    def test_it_formats_knows_when_not_to_format_with_commas(self):
        assert should_be_formatted_with_commas("zcountz(*)") is False


class TestGuessRowCollection:
    def test_it_handles_count(self):
        rows = [{"id": 1, "count(distinct barcode)": 27596962761}]
        row_collection = get_rendered_table(rows)
        expected = """\
| id | count_distinct_barcode |
| -- | ---------------------- |
| 1  | 27,596,962,761         |
| -- | ---------------------- |\
"""
        assert expected == str(row_collection)

    def test_it_handles_plural_integers(self):
        rows = [{"id": 1, "groups": 27596962761}]
        row_collection = get_rendered_table(rows)
        expected = """\
| id | groups         |
| -- | -------------- |
| 1  | 27,596,962,761 |
| -- | -------------- |\
"""
        actual = str(row_collection)
        assert expected == actual

    def test_it_handles_column_names_with_question_marks(self):
        rows = [{"one?": 1}]
        row_collection = get_rendered_table(rows)
        expected = """\
| one |
| --- |
| 1   |
| --- |\
"""
        assert expected == str(row_collection)
