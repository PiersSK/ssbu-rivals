import streamlit as st
import gspread
import pandas as pd
import numpy as np
import random
from datetime import datetime
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('ashborn-ff-48ba96983ef1.json', scope)
google_client = gspread.authorize(creds)

if 'current_player' not in st.session_state.keys(): st.session_state['current_player'] = None

def get_ssbu_results():
    sheet = google_client.open("SSBU Results").sheet1
    df = get_as_dataframe(sheet)
    st.session_state.seed = df.shape[0]
    random.seed(df.shape[0])

    df = df[['Piers Character', 'Rory Character', 'Piers Stocks', 'Rory Stocks', 'Date Played']].copy()
    df['Winner'] = df['Piers Stocks'].apply(lambda x: 'Piers' if x > 0 else 'Rory')
    df = df[df['Piers Stocks'] >= 0]

    st.session_state['current_player'] = None
    st.session_state['raw_df'] = df


def get_overall_winrates():
    df = st.session_state['raw_df']
    return pd.DataFrame({
        'Piers': [df[df['Winner'] == 'Piers'].shape[0] / df.shape[0]],
        'Rory': [df[df['Winner'] == 'Rory'].shape[0] / df.shape[0]]
    })

def get_player_character_stats(df, player):
    df['was_win'] = df['Winner'].apply(lambda x: 1 if x == player else 0)

    df = df.groupby(f'{player} Character').agg({'was_win': lambda x: x.sum(), 'Piers Stocks': lambda x: x.count()}).reset_index()
    df['Win Rate'] = df['was_win']/df['Piers Stocks']*100
    df['Games Played'] = df['Piers Stocks'].apply(lambda x: float(x))

    df['ImageUrl'] = df[f'{player} Character'].apply(lambda x: f'portraits/{x}.png')


    df['RandWeight'] = df['Games Played'].apply(lambda x: 1/(1+x))

    return df                     

with st.form("Get/Refresh Data"):
    st.write("Get data from the spreadsheet")
    st.form_submit_button("Get Data", on_click=get_ssbu_results())

results_df = st.session_state['raw_df']

st.title("SSBU Results Explorer")

st.subheader("Last 5 Games")
st.dataframe(results_df.tail(5), use_container_width=True)

st.subheader("Overall Win Rates")
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Piers: {round(get_overall_winrates()['Piers'].iloc[0]*100,2)}%")
with col2:
    st.subheader(f"Rory: {round(get_overall_winrates()['Rory'].iloc[0]*100,2)}%")

st.bar_chart(get_overall_winrates(), horizontal=True, stack=True)


st.subheader("Player Character Win Rates")
player = st.selectbox('Player', ['Piers', 'Rory'])
if player != st.session_state['current_player']:
    st.session_state['current_player'] = player
    st.session_state['character_df'] = get_player_character_stats(results_df, player)

st.dataframe(
    st.session_state['character_df'][[f'{player} Character', 'Win Rate', 'Games Played']],
    column_config={
        f"{player} Character": "Character Played",
        "Win Rate": st.column_config.ProgressColumn('Win Rate', format="%.1f%%", min_value=0, max_value=100),
        "Games Played": st.column_config.ProgressColumn('Games Played', format= "%.0f", min_value=0, max_value=st.session_state['character_df']['Games Played'].max()),
    },
    hide_index=True, 
    use_container_width=True   
)

def character_block(player, left=True):
    games_df = st.session_state['raw_df'].copy()
    games_df['Win'] = games_df['Winner'].apply(lambda x: 'W' if x == player else 'L')
    df = get_player_character_stats(games_df, player)
    char = get_rand_char(player, df)
    wr = round(df[df[f'{player} Character'] == char]['Win Rate'].iloc[0],1)
    gp = df[df[f'{player} Character'] == char]['Games Played'].iloc[0]

    last_5 = games_df[games_df[f'{player} Character'] == char]['Win'].tail(5).values.tolist()
    if len(last_5) < 5:
        last_5 = ['-' for i in range(0,(5-len(last_5)))] + last_5

    col1, col2 = st.columns(2)
    with col1:
        if left:
            st.subheader(char)
            st.image(f"portraits/{char}.png")
        else: 
            st.write(f"Win Rate: {wr}%")
            st.write(f"Games Played: {int(gp)}")
            st.write(f"Last 5: {' '.join(last_5)}")
    with col2:
        if left:
            st.write(f"Win Rate: {wr}%")
            st.write(f"Games Played: {int(gp)}")
            st.write(f"Last 5: {' '.join(last_5)}")
        else:
            st.subheader(char)
            st.image(f"portraits/{char}.png")
    
    return char


def get_rand_char(player, df):
    random.seed(st.session_state.seed)
    weights = df['RandWeight'].values
    n = random.choices(range(0, df.shape[0]), weights=weights, k=1)[0]
    return df[f'{player} Character'].iloc[n]

def save_result(new_data, check):
    if not check: return
    p_stock = new_data['Piers Stocks'].iloc[0]
    r_stock = new_data['Rory Stocks'].iloc[0]

    if p_stock > 0 and r_stock > 0:
        st.error("Someone must have lost! Ensure one stock value is at 0")
    elif p_stock == 0 and r_stock == 0:
        st.error("Someone must have won! Ensure one stock value is above 0")
    else:
        sheet = google_client.open("SSBU Results").sheet1
        df = get_as_dataframe(sheet)

        dfmerged = pd.concat([df, new_data], ignore_index=True, sort=False)
        sheet.clear()
        set_with_dataframe(sheet, dfmerged)
        get_ssbu_results()

with st.container(border=True):
    st.title("Next Game")

    col1, col2 = st.columns(2)
    with col1:
        p_char = character_block("Piers")
    with col2:
        r_char = character_block("Rory", left=False)
    
    past_games = results_df[(results_df['Piers Character'] == p_char) & (results_df['Rory Character'] == r_char)]

    if past_games.shape[0] > 0:
        st.dataframe(results_df[(results_df['Piers Character'] == p_char) & (results_df['Rory Character'] == r_char)])
    else:
        st.write("No past games between these two characters")
    
with st.form("Next Game", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        p_stock = st.number_input("Piers Stocks", step=1, min_value=0, max_value=3)
    with col2:
        r_stock = st.number_input("Rory Stocks", step=1, min_value=0, max_value=3)

    new_data = pd.DataFrame({
        'Piers Character': [p_char],
        'Rory Character': [r_char],
        'Piers Stocks': [p_stock],
        'Rory Stocks': [r_stock],
        'Winner': ['Piers' if p_stock > 0 else 'Rory'],
        'Date Played': [datetime.now()]
    })

    check = st.checkbox("Game Completed?", value=False)
    st.form_submit_button("Save Result", on_click=save_result(new_data, check))

