from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from datetime import datetime
import pandas as pd

from utils.google_sheets import get_ssbu_results, save_results
from utils.game_stats import get_all_character_stats, get_next_character
from components.character_card import CharacterCard
from components.match_row import MatchRow
from components.game_preview import GamePreview
from components.character_winrates import CharacterWinRates

app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'style.css']
)

results_df = get_ssbu_results()
next_characters = {
    "Piers": "",
    "Rory": ""
}
for player in next_characters.keys():
    char_df = get_all_character_stats(results_df, player)
    next_characters[player] = get_next_character(results_df.shape[0], char_df, player)

past_games = results_df[(results_df['Piers Character'] == next_characters["Piers"]) & (results_df['Rory Character'] == next_characters["Rory"])]
last_5 = results_df.tail(5)

def up_next(df):
    next = []
    current = df.shape[0]
    for i in range(1,5):
        piers = get_next_character(current+i, get_all_character_stats(df, "Piers"), "Piers")
        rory = get_next_character(current+i, get_all_character_stats(df, "Rory"), "Rory")
        next.append(dbc.Col(GamePreview(piers, rory).component(), width=2))

    return next

app.layout = html.Div([
    html.H1('SSBU Rivals'),
    dbc.Row([
        dbc.Col(html.H1("Piers", className="character-title"), width=5),
        dbc.Col(html.H1("VS", className="character-title"), width=2),
        dbc.Col(html.H1("Rory", className="character-title"), width=5)
    ]),
    dcc.Loading([
        dbc.Row([
            dbc.Col(html.Div(CharacterCard(next_characters["Piers"], results_df, "Piers").component(), id='p_char_card')),
            dbc.Col(html.Div(CharacterCard(next_characters["Rory"], results_df, "Rory", False).component(), id='r_char_card'))
        ]),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "Save Result!",
                    color="dark",
                    id="save-result-btn",
                    style={"width":"100%"}
                ), 
                width=4
            ),
            justify="center"
        ),
        dbc.Row(
            dbc.Col(MatchRow(past_games, "Past Matchup Games").component(), width=9),
            justify="center"
        ),
        dbc.Row(dbc.Col(html.P("Upcoming Matches", className="character-title"),width=4),justify="center"),
        dbc.Row(
            up_next(results_df)
            ,justify="center"
            ,id="up-next"
        ),
        dbc.Alert(
            "Game not saved! Make sure at least one player has 0 stocks and the other has 1 or more!",
            id="save-failed-alert",
            is_open=False,
            color="danger",
            duration=4000,
        ),
        
        html.H1("Lifetime Stats"),
        dbc.Row(
            dbc.Col(MatchRow(last_5, "Last 5 Games").component(), width=9),
            justify="center",
            id='last-5-games'
        ),
        dbc.Row([
            dbc.Col(
                CharacterWinRates(results_df, "Piers").component(), id="p-char-stats"
            ),
            dbc.Col(
                CharacterWinRates(results_df, "Rory").component(), id="r-char-stats",
            )]
        )
    ])
])

@app.callback(
    Output("save-failed-alert", "is_open"),
    Output("p_char_card", "children"),
    Output("r_char_card", "children"),
    Output("last-5-games", "children"),
    Output("up-next", "children"),
    Output("p-char-stats", "children"),
    Output("r-char-stats", "children"),
    Input("save-result-btn", 'n_clicks'),
    State("Piers-finalstocks", "value"),
    State("Rory-finalstocks", "value"),
    State("p_char_card", "children"),
    State("r_char_card", "children"),
    prevent_initial_call=True
)
def save_match(n, piers_stocks, rory_stocks, p_char, r_char):
    valid = True
    if piers_stocks == 0 and rory_stocks == 0:
        valid = False
    elif piers_stocks > 0 and rory_stocks > 0:
        valid = False

    if valid:
        results_df = save_results(
            next_characters["Piers"],
            next_characters["Rory"],
            piers_stocks,
            rory_stocks
        )

        for player in next_characters.keys():
            char_df = get_all_character_stats(results_df, player)
            next_characters[player] = get_next_character(results_df.shape[0], char_df, player)
        
        p_char = CharacterCard(next_characters["Piers"], results_df, "Piers").component()
        r_char = CharacterCard(next_characters["Rory"], results_df, "Rory", False).component()
        last_games = dbc.Col(MatchRow(results_df.tail(5), "Last 5 Games").component(), width=9)

    return not valid, p_char, r_char, last_games, up_next(results_df), CharacterWinRates(results_df, "Piers").component(), CharacterWinRates(results_df, "Rory").component()

if __name__ == '__main__':
    app.run_server(debug=True)