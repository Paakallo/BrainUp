from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Hello, World!'),
    html.P(children='This is a simple example.')
])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
