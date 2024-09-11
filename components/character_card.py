from dash import html, get_asset_url, dcc
import dash_bootstrap_components as dbc
import json

from utils.game_stats import get_character_stats

class CharacterCard():
    def __init__(self, character, results, player, left = True):
        self.character = character
        self.results = results
        self.player = player
        self.left = left

        self.colours = json.load(open("data/character_colours.json"))
        self.stats = get_character_stats(results, character, player)
    
    def get_last_games(self):
        df = self.results.copy()
        df['Win'] = df['Winner'].apply(lambda x: 'W' if x == self.player else 'L')
        last_5 = df[df[f'{self.player} Character'] == self.character]['Win'].tail(5).values.tolist()
        last_5 = ['-' for i in range(0,(5-len(last_5)))] + last_5

        cols = []

        for result in last_5:
            class_suffix = "win" if result == "W" else "lose" if result == "L" else "missing"
            cols.append(
                dbc.Col(html.P(result, className=f'pastgame {class_suffix}'))
            )
        
        return cols
    
    def get_font_color(self, color):
        color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        intensity = rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114
        return "white" if intensity < 186 else "black"

    def component(self):

        portrait = html.Img(
            src = get_asset_url(f'portraits/{self.character}.png'),
            className="character-img-big",
            style={"background-color":self.colours[self.character]}
        )

        stats = [
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Win Rate"),
                        dbc.CardBody(f"{int(self.stats['Win Rate'].iloc[0])}%")
                    ])
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Games Played"),
                        dbc.CardBody(f"{int(self.stats['Games Played'].iloc[0])}")
                    ])
                )
            ]),
            html.P("Last 5 Games", style={"margin":"5%"}),
            dbc.Row(self.get_last_games()),
            html.P("Final Stocks", style={"margin":"5%"}),
            dcc.Dropdown([0,1,2,3], 0, id=f"{self.player}-finalstocks", className="stock-dropdown")
        ]

        body = [dbc.Col(portrait), dbc.Col(stats)] if self.left else [dbc.Col(stats), dbc.Col(portrait)]

        return html.Div([
            html.Div(
                html.H2(
                    self.character,
                    className="character-title",
                    style={
                        "background-color":self.colours[self.character],
                        "color":self.get_font_color(self.colours[self.character]),
                        "text-align":"left" if self.left else "right"
                    }
                )
            ),
            dbc.Row(body)
            ]
            ,className = "character-card"
        )
        
