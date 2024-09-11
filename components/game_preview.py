from dash import html, get_asset_url, dcc
import dash_bootstrap_components as dbc
from utils.stylings import char_color

class GamePreview:
    def __init__(self, piers, rory):
        self.piers = piers
        self.rory = rory
        pass

    def component(self):
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src = get_asset_url(f'portraits/{self.piers}.png'),
                                className="character-img-big",
                                style={"background-color":char_color(self.piers)}
                            ),
                            width=6
                        ),
                        dbc.Col(
                            html.Img(
                                src = get_asset_url(f'portraits/{self.rory}.png'),
                                className="character-img-big",
                                style={"background-color":char_color(self.rory)}
                            ),
                            width=6
                        )
                    ],
                    justify="center",
                    className="game-preview"
                )
            ]
        )