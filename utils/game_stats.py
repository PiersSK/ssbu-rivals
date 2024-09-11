import random

def get_all_character_stats(results, player):
    df = results.copy()
    
    df['was_win'] = df['Winner'].apply(lambda x: 1 if x == player else 0)

    df = df.groupby(f'{player} Character').agg({'was_win': lambda x: x.sum(), 'Piers Stocks': lambda x: x.count()}).reset_index()
    df['Win Rate'] = df['was_win']/df['Piers Stocks']*100
    df['Games Played'] = df['Piers Stocks'].apply(lambda x: float(x))

    df['ImageUrl'] = df[f'{player} Character'].apply(lambda x: f'portraits/{x}.png')


    df['RandWeight'] = df['Games Played'].apply(lambda x: 1/(1+x))

    return df 

def get_character_stats(results, character, player):
    df = results.copy()
    df = df[df[f"{player} Character"] == character]
    
    df['was_win'] = df['Winner'].apply(lambda x: 1 if x == player else 0)

    df = df.groupby(f'{player} Character').agg({'was_win': lambda x: x.sum(), 'Piers Stocks': lambda x: x.count()}).reset_index()
    df['Win Rate'] = df['was_win']/df['Piers Stocks']*100
    df['Games Played'] = df['Piers Stocks'].apply(lambda x: float(x))

    df['ImageUrl'] = df[f'{player} Character'].apply(lambda x: f'portraits/{x}.png')


    df['RandWeight'] = df['Games Played'].apply(lambda x: 1/(1+x))

    return df 

def get_next_character(seed, df, player, weight=True):
    print(seed)
    random.seed(seed)
    weights = df['RandWeight'].values
    n = random.choices(range(0, df.shape[0]), weights=weights, k=1)[0] if weight else random.randrange(0, df.shape[0])
    return df[f'{player} Character'].iloc[n]

# def overall_win_rates(df):
