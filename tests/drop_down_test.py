import dash
from dash import html, dcc, Output, Input

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dropdown Example"),

    dcc.Dropdown(
        id='dropdown-id',
        options=[
            {'label': 'Option 1', 'value': 'opt1'},
            {'label': 'Option 2', 'value': 'opt2'},
            {'label': 'Option 3', 'value': 'opt3'}
        ],
        value='opt1',  # default value
        clearable=False
    ),

    html.Div(id='output-id')
])

@app.callback(
    Output('output-id', 'children'),
    Input('dropdown-id', 'value')
)
def update_output(value):
    return f'You selected: {value}'

if __name__ == '__main__':
    app.run_server(debug=True)
