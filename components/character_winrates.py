from dash import html, get_asset_url, dcc
import dash_bootstrap_components as dbc

import plotly.express as px 

from utils.game_stats import get_all_character_stats

class CharacterWinRates():
    def __init__(self, results, player) -> None:
        self.player = player
        self.winrates = get_all_character_stats(results, player).sort_values(by=['Win Rate'])

    def get_fig(self):

        fig = px.bar(
            self.winrates,
            x='Win Rate',
            y=f'{self.player} Character',
            hover_data=['Win Rate', 'Games Played'],
            color='Games Played',
            text_auto='.2s',
            orientation='h',
            height=1000
        )
        return fig

    def component(self):
        return dcc.Graph(
            figure=self.get_fig()
        )