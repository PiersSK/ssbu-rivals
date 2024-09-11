from dash import html, dcc
import dash_bootstrap_components as dbc
import json
from datetime import datetime

from utils.stylings import char_color, char_font

class MatchRow():
    def __init__(self, past_games, title):
        self.past_games = past_games
        self.title = title
        self.colours = json.load(open("data/character_colours.json"))

    def get_match_rows(self):
        matches = [
            dbc.Row([
                dbc.Col("Piers' Fighter", width=3, className="match-row-element"),
                dbc.Col("Rorys Fighter", width=3, className="match-row-element"),
                dbc.Col("Piers", width=1, className="match-row-element"),
                dbc.Col("Rory", width=1, className="match-row-element"),
                dbc.Col("Date Played", width=3, className="match-row-element"),
            ]
            ,justify="center"
            ,className="mb-2"
            ),
        ] 
        for i, row in self.past_games.iterrows():
            date = row["Date Played"] if type(row["Date Played"]) is str else datetime.strftime(row["Date Played"], "%d-%m-%Y")
            

            matches.append(
                dbc.Row([
                        dbc.Col(
                            row["Piers Character"],
                            width=3,
                            style={
                                "background-color":char_color(row["Piers Character"]),
                                "color":char_font(row["Piers Character"]),
                            },
                            className="match-row-element"
                        ),
                        dbc.Col(
                            row["Rory Character"],
                            width=3,
                            style={
                                "background-color":char_color(row["Rory Character"]),
                                "color":char_font(row["Rory Character"]),
                            },
                            className="match-row-element"
                        ),
                        dbc.Col(
                            row["Piers Stocks"],
                            width=1,
                            className="match-row-element " + ("win" if row["Piers Stocks"] else "lose")
                        ),
                        dbc.Col(
                            row["Rory Stocks"],
                            width=1,
                            className="match-row-element " + ("win" if row["Rory Stocks"] else "lose")
                        ),
                        dbc.Col(
                            date,
                            width=3,
                            style={"background-color":"black"},
                            className="match-row-element"
                        ),
                    ]
                    ,justify="center"
                    ,className="mb-2"
                )
            )

        return matches

    def component(self):
        matches = [html.H3(self.title, className="mb-4")]
        if(self.past_games.shape[0] == 0):
            matches.append(html.P("No past games between these fighters"))
        else:
            matches = matches + self.get_match_rows()

        return html.Div(matches, className="character-card")