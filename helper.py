import numpy as np 
import pandas as pd
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots




# Medal tally
        
def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    if year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    if year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    if year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == year) & (medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
       ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    x['Gold'] = x['Gold'].astype('int')
    x['Silver'] = x['Silver'].astype('int')
    x['Bronze'] = x['Bronze'].astype('int')
    x['total'] = x['total'].astype('int')

    return x


def home_advantage_analysis(df, df_medalists, selected_country):
    city_country_map = {
        # Summer Olympics
        "Athens": "Greece",
        "Beijing": "China",
        "Berlin": "Germany",
        "Barcelona": "Spain",
        "London": "UK",
        "Rio de Janeiro": "Brazil",
        "Tokyo": "Japan",
        "Los Angeles": "USA",
        "Atlanta": "USA",
        "Sydney": "Australia",
        "Seoul": "South Korea",
        "Mexico City": "Mexico",
        "Moscow": "Russia",
        "Rome": "Italy",
        "Montreal": "Canada",
        "Amsterdam": "Netherlands",
        "Helsinki": "Finland",
        "Melbourne": "Australia",
        "Paris": "France",
        "Stockholm": "Sweden",
        # Winter Olympics
        "Sapporo": "Japan",
        "Calgary": "Canada",
        "Nagano": "Japan",
        "Salt Lake City": "USA",
        "Turin": "Italy",
        "Vancouver": "Canada",
        "Sochi": "Russia",
        "Pyeongchang": "South Korea",
    }

     # Calculate medals won by the host country
    host_countries = df[['Year', 'City']].drop_duplicates()
    host_countries['Host_Country'] = host_countries['City'].map(city_country_map)
    # Ensure 'Year' columns are the same data type
     # Ensure 'Year' columns are the same data type
    df_medalists['Year'] = df_medalists['Year'].astype(int)
    host_countries['Year'] = host_countries['Year'].astype(int)

    # Merge medalists data with host country information
    df_medalists = pd.merge(df_medalists, host_countries[['Year', 'Host_Country']], on='Year', how='left')

    # Convert 'Team' column to string for comparison
    df_medalists['Team'] = df_medalists['Team'].astype(str)

    # Handle NaN values in 'Team' column
    df_medalists = df_medalists.dropna(subset=['Team'])

    # Filter data for the selected country
    country_data = df_medalists[df_medalists['Team'] == selected_country]

    # Calculate home and away performance
    medals_at_home = country_data[country_data['Host_Country'] == selected_country]
    medals_away = country_data[country_data['Host_Country'] != selected_country]

    home_medals_count = medals_at_home['Medal'].count()
    away_medals_count = medals_away['Medal'].count()

    # Check if the selected country has hosted the Olympics
    hosted = host_countries[host_countries['Host_Country'] == selected_country]

    if hosted.empty:
        st.write(f"{selected_country} has never hosted the Olympics.")
        home_medals_count = 0  # No home medals if they never hosted

    return home_medals_count, away_medals_count

def india_analysis(df_medalists):
    india_data = df_medalists[df_medalists['Team'] == 'India']
    top_performers = india_data.groupby('Name')['Medal'].count().nlargest(5)
    india_medal_trend = india_data.groupby('Year')['Medal'].count().reset_index()
    return india_medal_trend

def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years,country

def country_year_list1(df):
    years = df['Year'].unique().tolist()
    years.sort()

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()

    return years,country



def plot_overall_tally(tally):
    st.write("### Overall Medal Tally by Country")
    st.dataframe(tally)

def plot_india_analysis(india_medal_trend):
    st.write("### India's Medal Trend")
    sns.lineplot(x='Year', y='Medal', data=india_medal_trend)
    st.pyplot()

def plot_home_advantage(home_medals, away_medals, selected_country):
  # Create subplots: 1 row, 2 columns
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'xy'}]], 
                        subplot_titles=('Medal Distribution', 'Home vs. Avg Away Medals'))

    # Pie chart
    labels = ['Home Medals', 'Away Medals']
    values = [home_medals, away_medals]

    fig.add_trace(go.Pie(labels=labels, values=values, hole=.3, domain={'column': 0}), 1, 1)

    # Calculate average away medals per Olympics
    total_olympics = home_medals + away_medals  # Assuming each medal represents one Olympics participation
    avg_away_medals = away_medals / (total_olympics - 1) if total_olympics > 1 else away_medals

    # Bar chart
    fig.add_trace(go.Bar(x=['Home Medals', 'Avg Away Medals'], 
                         y=[home_medals, avg_away_medals], 
                         text=[f'{home_medals:.0f}', f'{avg_away_medals:.2f}'],
                         textposition='auto'), 
                  row=1, col=2)

    # Update layout
    fig.update_layout(
        title_text=f"Olympic Performance Analysis for {selected_country}",
        annotations=[dict(text=f'Total Medals: {home_medals + away_medals}', x=0.20, y=0.5, font_size=14, showarrow=False)],
        height=500,
        width=900
    )

    # Show the plot
    st.plotly_chart(fig)
    st.write(f"Medals won at home: {home_medals}")
    st.write(f"Medals won away: {away_medals}")



def most_successful_countrywise(df,Country):
    temp_df =df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == Country]
    temp_df =temp_df['Name'].value_counts().reset_index().head(15).merge(df,on='Name',how='left')[['Name','Sport','count']].drop_duplicates('Name')
    temp_df.rename(columns={'count':'Medal'},inplace=True)
    return temp_df
def data_over_time (df,column,name):

    data_over_time_df = df.drop_duplicates(['Year',column])['Year'].value_counts().reset_index()

    data_over_time_df.rename(columns={'Year':'year','count':name},inplace=True)
    return data_over_time_df
def most_successful(df,sport):
    temp_df =df.dropna(subset=['Medal'])
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]
    x =temp_df.groupby('Name').sum()[['Gold','Silver','Bronze']]
    x['total']=x['Gold']+x['Bronze']+x['Silver']
    x =x.sort_values(['total','Gold','Silver','Bronze'],ascending=False)
    return x.reset_index().head(15)