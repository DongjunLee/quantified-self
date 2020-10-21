import arrow

import dash_core_components as dcc
import dash_html_components as html


DATE_PICKER_STYLE = {
    "text-align": "center",
    "width": "100%",
    "margin-bottom": "15px",
}


def date_picker_with_chart_card(date_picker_id, chart_cards, date=arrow.now()):
    date_picker_html = html.Div(
        [
            html.Span(
                "Date:", style={"font-size": "1.5em", "margin-right": "5px"}
            ),
            dcc.DatePickerSingle(
                id=date_picker_id,
                date=date.datetime,
                max_date_allowed=arrow.now().datetime,
            ),
        ],
        style=DATE_PICKER_STYLE,
    )

    items = [date_picker_html] + chart_cards
    return row_card(items)


def date_range_with_chart_card(date_range_id, chart_cards, start_date=arrow.now().shift(days=-30), end_date=arrow.now()):
    date_range_html = html.Div(
        [
            html.Span(
                "DateRange:", style={"font-size": "1.5em", "margin-right": "5px"}
            ),
            dcc.DatePickerRange(
                id=date_range_id,
                first_day_of_week=1,  # Monday
                start_date=start_date.datetime,
                end_date=end_date.datetime,
                max_date_allowed=end_date.datetime,
            ),
        ],
        style=DATE_PICKER_STYLE,
    )

    items = [date_range_html] + chart_cards
    return row_card(items)


def chart_card(graph_id, title_text=None, description_text=None, size=6, control_item=None):
    items = [
        dcc.Graph(id=graph_id),
    ]
    if control_item is not None:
        items.insert(0, control_item)

    return make_card_html(
        items,
        title_text=title_text,
        description_text=description_text,
        size=size,
    )


def simple_value_card(
    card_id,
    value_id,
    title_text,
    description_text=None,
    size=2
):
    return make_card_html(
        [
            html.P(id=value_id),
        ],
        card_id=card_id,
        title_text=title_text,
        description_text=description_text,
        size=size,
    )


def row_card(item, title_text=None, description_text=None):
    return make_card_html(
        item,
        title_text=title_text,
        description_text=description_text,
        card_body_style={
            "display": "flex",
            "flex-wrap": "wrap",
        }
    )


def make_card_html(
    body,
    card_id=None,
    title_text=None,
    description_text=None,
    size=12,
    background_color="white",
    class_name="",
    card_body_style={},
):

    card_html = html.Div(
        [html.Div([], className="card mb-3 text-center")],
        className=f"col-sm-{size}",
    )

    card_body_style["background-color"] = background_color

    if card_id is None:
        div = html.Div(
            body,
            className="card-body " + class_name,
            style=card_body_style,
        )
    else:
        div = html.Div(
            body,
            id=card_id,
            className="card-body " + class_name,
            style=card_body_style,
        )

    card_html.children[0].children.append(div)

    if description_text is not None:
        description = html.P(description_text, className="col-sm-12")
        card_html.children[0].children[0].children.insert(0, description)

    if title_text is not None:
        if size == 12:
            H_html = html.H4
        else:
            H_html = html.H5
        title = H_html(title_text, className="card-title col-sm-12")
        card_html.children[0].children[0].children.insert(0, title)

    return card_html
