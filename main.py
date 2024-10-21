import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import sys


df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

df = preprocessor.preprocess(df, region_df)
df_medalists = df.dropna(subset=['Medal'])

st.sidebar.title("Olympics Data Analysis")
user_menu = st.sidebar.radio(
    'Select An Option',
    ("Medal Tally","Home Advantage Analysis","India Analysis","Overall Analysis")
)

if user_menu == "Medal Tally":
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Years", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    else:
        st.title(f"{selected_country} in {selected_year} olympics!")
    st.table(medal_tally)

if user_menu == "Home Advantage Analysis":
    st.sidebar.header("Home Advantage Analysis")

    # Country selection
    years,country = helper.country_year_list1(df)

    selected_country = st.sidebar.selectbox("Select Country", country)

    # Perform home advantage analysis for the selected country
    home_medals, away_medals = helper.home_advantage_analysis(df, df_medalists, selected_country)
    
    # Plot the results
    helper.plot_home_advantage(home_medals, away_medals, selected_country)

# India Analysis Page
if user_menu == "India Analysis":
    st.sidebar.header("India's Olympic Performance")
    selected_country = "India"
    india_medal_trend = helper.india_analysis(df_medalists)
    helper.plot_india_analysis(india_medal_trend)
    st.title('Most Successful Player In {}'.format(selected_country))
    top_temp_df = helper.most_successful_countrywise(df,selected_country)
    st.table(top_temp_df)
if user_menu == 'Overall Analysis':
    st.title('Top Statistics')
    athletes = df.Name.unique().shape[0]
    country = df.region.unique().shape[0]
    events = df.Event.unique().shape[0]
    sports = df.Sport.unique().shape[0]
    cities = df.City.unique().shape[0]
    editions = df.Year.unique().shape[0] - 1

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header('Editions')
        st.title(editions)
    with col2:
        st.header('Hosts')
        st.title(cities)
    with col3:
        st.header('Sports')
        st.title(sports)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header('Events')
        st.title(events)
    with col2:
        st.header('Nations')
        st.title(country)
    with col3:
        st.header('Athletes')
        st.title(athletes)

    st.title('Participating Nations Over The Year')
    nations_over_time_df = helper.data_over_time(df, 'region', 'countries')
    
    plt.figure(figsize=(10, 5))
    plt.plot(nations_over_time_df['year'], nations_over_time_df['countries'], marker='o')
    plt.title('Participating Nations Over The Years')
    plt.xlabel('Year')
    plt.ylabel('Number of Countries')
    plt.grid()
    st.pyplot(plt)

    st.title('Events Over The Year')
    nations_over_time_df = helper.data_over_time(df, 'Event', 'events')
    
    plt.figure(figsize=(10, 5))
    plt.plot(nations_over_time_df['year'], nations_over_time_df['events'], marker='o', color='orange')
    plt.title('Events Over The Years')
    plt.xlabel('Year')
    plt.ylabel('Number of Events')
    plt.grid()
    st.pyplot(plt)

    st.title('Athletes Over The Year')
    nations_over_time_df = helper.data_over_time(df, 'Name', 'athletes')
    
    plt.figure(figsize=(10, 5))
    plt.plot(nations_over_time_df['year'], nations_over_time_df['athletes'], marker='o', color='green')
    plt.title('Athletes Over The Years')
    plt.xlabel('Year')
    plt.ylabel('Number of Athletes')
    plt.grid()
    st.pyplot(plt)

    st.title('No Of Events Overtime Of Sports')
    fig, ax = plt.subplots(figsize=(25, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int), annot=True, ax=ax)
    plt.title('Number of Events Over Time by Sport')
    st.pyplot(fig)

    st.title('Most Successful Players')
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select A Sport', sport_list)
    st.table(helper.most_successful(df, selected_sport))