import streamlit as st
import pandas as pd
import altair as alt
import requests
import gspread

# Set page config
st.set_page_config(page_title="AZL TOURNAMENT: STATS", page_icon=":soccer:")
st.title("AZL TOURNAMENT: STATS ⚽")
st.write("Analysis of player performance from AZL Tournament soccer games")

r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key=1tPCnVRoxTh597qqxCGqZ5PpFVw8JhvJW1ODo0jH9lA0&output=csv')
open('dataset.csv', 'wb').write(r.content)
df = pd.read_csv('dataset.csv')
players_df = pd.read_csv('players.csv')
players_df['Team'] = pd.to_numeric(players_df['Team'], errors='coerce')
players_df['Skill'] = pd.to_numeric(players_df['Skill'], errors='coerce')
players_df = players_df[['Name', 'Quirk', 'Team', 'Skill']]
players_df['Name Normalized'] = players_df['Name'].str.upper().str.strip()

df['Player Name Normalized'] = df['Player Name'].str.upper().str.strip()
merged_df = pd.merge(
    players_df,
    df[['Player Name Normalized', 'Games Played', 'Goals', 'Assists']],
    left_on='Name Normalized',
    right_on='Player Name Normalized',
    how='left'
).drop(columns=['Name Normalized', 'Player Name Normalized'])

merged_df['Goals'] = merged_df['Goals'].fillna(0).astype('Int64')
merged_df['Assists'] = merged_df['Assists'].fillna(0).astype('Int64')
merged_df['Games Played'] = merged_df['Games Played'].fillna(0).astype('Int64')
merged_df['Goals per Game'] = merged_df.apply(
    lambda row: row['Goals'] / row['Games Played'] if row['Games Played'] > 0 else 0,
    axis=1
)
merged_df['Assists per Game'] = merged_df.apply(
    lambda row: row['Assists'] / row['Games Played'] if row['Games Played'] > 0 else 0,
    axis=1
)
merged_df['G/A per Game'] = merged_df.apply(
    lambda row: (row['Goals'] + row['Assists']) / row['Games Played'] if row['Games Played'] > 0 else 0,
    axis=1
)

# Sort the dataframes
f_df = df.copy()
f_df['Goals per Game'] = f_df['Goals'] / f_df['Games Played']
f_df['Assists per Game'] = f_df['Assists'] / f_df['Games Played']
f_df['G/A per Game'] = (f_df['Goals'] + f_df['Assists']) / f_df['Games Played']

goals_per_game_df = f_df[['Player Name', 'Goals per Game']].sort_values(by='Goals per Game', ascending=False)
assists_per_game_df = f_df[['Player Name', 'Assists per Game']].sort_values(by='Assists per Game', ascending=False)
total_goals_df = f_df[['Player Name', 'Goals']].sort_values(by='Goals', ascending=False)
total_assists_df = f_df[['Player Name', 'Assists']].sort_values(by='Assists', ascending=False)

player_goals_per_game_df = merged_df[['Name', 'Quirk', 'Team', 'Skill', 'Goals per Game']].sort_values(by='Goals per Game', ascending=False)
player_total_goals_df = merged_df[['Name', 'Quirk', 'Team', 'Skill', 'Goals']].sort_values(by='Goals', ascending=False)
player_assists_per_game_df = merged_df[['Name', 'Quirk', 'Team', 'Skill', 'Assists per Game']].sort_values(by='Assists per Game', ascending=False)
player_total_assists_df = merged_df[['Name', 'Quirk', 'Team', 'Skill', 'Assists']].sort_values(by='Assists', ascending=False)

players_sorted_df = players_df.sort_values(by=['Team', 'Skill', 'Name'], ascending=[True, False, True])
quirk_counts_df = players_df['Quirk'].value_counts().rename_axis('Quirk').reset_index(name='Count')
team_skill_df = players_df.groupby('Team', as_index=False)['Skill'].mean().sort_values(by='Skill', ascending=False)


st.header("Player List")
show_players = st.checkbox("Show Player List")
if show_players:
    st.table(players_sorted_df)

st.header("Player Quirk Counts")
st.table(quirk_counts_df)

st.header("Average Skill by Team")
st.table(team_skill_df)

st.header("26-Player Metrics")
selected_tab = st.selectbox(
    "Choose a metric",
    [
        "Goals per Game",
        "Total Goals",
        "Assists per Game",
        "Total Assists"
    ]
)

if selected_tab == "Goals per Game":
    st.subheader("26-player Goals per Game")
    st.table(player_goals_per_game_df)
elif selected_tab == "Total Goals":
    st.subheader("26-player Total Goals")
    st.table(player_total_goals_df)
elif selected_tab == "Assists per Game":
    st.subheader("26-player Assists per Game")
    st.table(player_assists_per_game_df)
else:
    st.subheader("26-player Total Assists")
    st.table(player_total_assists_df)