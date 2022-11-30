# -------------
import os
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk
import time
import altair as alt
from altair import Chart, X, Y, Axis, SortField, OpacityValue

DATE_COLUMN = 'time'


def count_rows(rows):
    return len(rows)


def get_dom(dt):
    return dt.day


def get_weekday(dt):
    return dt.weekday


def get_hour(dt):
    return dt.hour


def get_month(dt):
    return dt.month


# ------------------------------------------------------------------

# YOUTUBE HISTORY
path = 'watch-history.json'
df = pd.read_json(path)

# RESEARCH HISTORY
path3 = 'search-history.json'
df_search = pd.read_json(path3)
df_search = df_search.drop(['header', 'products', 'titleUrl'], axis=1)

# YOUTUBE SUBSCRIPTION
path2 = 'subscriptions.csv'
df_sub = pd.read_csv(path2)

# GOOGLE MAP
df_map = pd.read_json("Location History.json")

df = df.drop(['header', 'subtitles', 'products', 'details', 'titleUrl'], axis=1)

# ------------------------------------------------------------------
# -------------- LOCATION HISTORY TREATMENT --------------------------
list_dico = df_map.values.tolist()
new_df = pd.DataFrame([list_of_dico[0] for list_of_dico in list_dico])
new_df['timestampMs'] = pd.to_datetime(new_df['timestampMs'], unit='ms')
new_df['latitudeE7'] = new_df['latitudeE7'].map(lambda X: X / 1E7)
new_df['longitudeE7'] = new_df['longitudeE7'].map(lambda X: X / 1E7)

layer = pdk.Layer(
    "HexagonLayer",
    new_df.dropna(),
    get_position=['longitudeE7', 'latitudeE7'],
    auto_highlight=True,
    elevation_scale=50,
    pickable=True,
    elevation_range=[0, 3000],
    extruded=True,
    coverage=1,
)

# Combined all of it and render a viewport
r = pdk.Deck(
    layers=[layer],
    # map_style = pdk.map_styles.DARK_NO_LABELS,
    tooltip={'html': '<b> Nomber of Observation:<b> {elevationValue}'}
)

fig = px.scatter_mapbox(new_df, lat="latitudeE7", lon="longitudeE7",
                        color_discrete_sequence=["fuchsia"], zoom=3, height=300)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# --------------------------------------------------------------------
df["time"] = pd.to_datetime(df["time"])
df_search['time'] = pd.to_datetime(df["time"])
df['day'] = df['time'].map(get_dom)
df['weekday'] = df['time'].map(get_weekday)
df['hour'] = df['time'].map(get_hour)
df['month'] = df['time'].map(get_month)

# Name days of the week
df["day"] = df["time"].dt.day_name()
df["month"] = df["time"].dt.month_name()

# ---------------------- GROUP BY -------------------------
by_month = df.groupby('month').apply(count_rows)
by_day = df.groupby('day').apply(count_rows)
by_hour = df.groupby('hour').apply(count_rows)

# Reorder the weekday
week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
by_day = by_day.reindex(week)

# reorder the month
months = ["May", "June", "July", "August", "September", "October"]
by_month = by_month.reindex(months)

df['time'] = df.time.dt.tz_convert('UTC').dt.tz_convert('Etc/GMT-2')  # pytz.all_timezones
df_search['time'] = df_search.time.dt.tz_convert('UTC').dt.tz_convert('Etc/GMT-2')  # pytz.all_timezones

# ---------------------- FUNCTIONS -------------------------


def zoom_month(month_choice, data, param):
    df_month = data.loc[df['month'] == month_choice]
    by_month_choice = df_month.groupby(param).apply(count_rows)
    return by_month_choice


def plot_choice(plot, data):
    if plot == 'Line plot':
        st.subheader('Line plot')
        st.line_chart(data)
    elif plot == 'Bar chart':
        st.subheader('Bar chart')
        st.bar_chart(data)


def plot_days_in_month(month, data, selection):
    df_month = zoom_month(month, data, 'day')
    for n in range(len(selection)):
        plot_choice(selection[n], df_month)


def plot_all_months(data, selection):
    for n in range(len(selection)):
        plot_choice(selection[n], data)


def plot_pie_chart(label, values):
    st.subheader('Pie chart')
    labels = label
    sizes = values

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, )
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig1.set_facecolor('white')
    fig1.legend()
    st.pyplot(fig1)


def main():
    option2 = ''
    # layout
    #  st.set_page_config(layout="wide")
    # -------------------------- SIDE BAR -----------------------------------
    menu = ['Florence Nguyen','Overview', 'General infos', 'Graphics', 'Google map']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Florence Nguyen':
        st.title('Florence NGUYEN')

        st.write('M1 student Major Data & Artificial Intelligence - DS3 Group -  promotion 2023')

        st.markdown('**LINKEDIN**')
        st.info('[/Florence Nguyen](https://www.linkedin.com/in/florence-nguyen-010a2716a/)')

        st.markdown('**GITHUB**')
        st.info('[/lylynator] (https://github.com/lylynator)')


    if choice == 'General infos':
        st.title('General information')
        image = Image.open('youtube.png')
        st.image(image)

        c1, c2 = st.columns((1, 1))
        with c1:

            st.subheader('How many videos in my history ? ')
            st.write(df.shape[0], 'videos')

            st.subheader('What is the period ?')
            st.write(by_month.shape[0], 'months')

            st.subheader('Last video seen')
            df_m = df.loc[df['month'] == 'October']
            st.write(df_m.head(1))

            thumbnail2 = Image.open('miniature2.png')
            st.image(thumbnail2)

            st.subheader('Last research i did')
            vid1 = df_search.head(1).title
            st.write(vid1)
        with c2:
            st.subheader('How many channel subscription ?')
            st.write(df_sub.shape[0], 'subscriptions')
            st.subheader('Most viewed video in the month')
            df_m = df.loc[df['month'] == 'October']
            st.write(df_m.title.value_counts().head(1))
            thumbnail1 = Image.open('miniature1.png')
            st.image(thumbnail1)

    if choice == 'Graphics':
        sns.set_theme(style="ticks")
        sns.set_theme(style="darkgrid")

        st.title('Facetting diagrams of my youtube datas through May to October 2021')

        h = sns.displot(
            df, x="hour", col="day", row="month",
            binwidth=3, height=5, facet_kws=dict(margin_titles=True),
        )
        st.pyplot(h)

    if choice == 'Overview':
        st.title('Overview of my youtube consumption')
        st.text('I am a huge cosumer of youtube, I watch youtube videos everyday (or almost).\nI use youtube to learn new skills or to review some school notions that i didnt get it. \nBesides, I like entertainment videos and music videos. \nFor me, youtube is a powerful tool to discover many artists. \nSo now, lets see my youtube data to understand my behaviour, \nyou can select the month day or hour parameters, as weel as the type of plot in left side.')
        sns.set_theme(style="whitegrid")
        data = Image.open('data.jpg')
        st.image(data)

        # Load the diamonds dataset

        c2, c3, c4 = st.columns((1, 1, 2))

        st.sidebar.subheader("Parameters")
        option = st.sidebar.selectbox(
            'Choose a parameter',
            ('Month', 'Day', 'Hour')
        )

        if option == 'Month':
            option2 = st.sidebar.selectbox(
                'You can choose a month',
                ('May', 'June', 'July', 'August', 'September', 'October', 'All')
            )

        selection = st.sidebar.multiselect(
            'Plotting choices',
            ['Line plot', 'Pie chart', 'Bar chart']
        )

        with c2:
            # st.subheader('Description')
            if option == 'Month' and option2 == 'All':
                st.markdown('**MEAN**')
                st.info(by_month.mean())

                st.markdown('**MAX**')
                st.info(by_month.max())
            if option == 'Hour':
                st.markdown('**HIGH**')
                st.info('7pm')

                st.markdown('**LOW**')
                st.info('2am')

            if option == 'Day':
                st.markdown('**HIGH**')
                st.info('Monday')

                st.markdown('**LOW**')
                st.info('Thursday')
        with c3:
            if option == 'Month' and option2 == 'All':
                st.markdown('**MIN**')
                st.info(by_month.min())

                st.markdown('**MEDIAN**')
                st.info(by_month.median())

        with c4:
            if option == 'Hour':
                st.markdown('**Description**')
                st.info(
                    'During the evening I watch the most video especially at 7pm, because I usually eat at this time. I dont watch many videos at night time because I sleep')
            if option == 'Day':
                st.markdown('**Description**')
                st.info(
                    'I watch the most videos on Monday because it was the summer. And since back to school, we just have one class each mondays. the repartition is quite equal for the reste of the week')

            if option == 'Month' and option2 == 'All':
                st.markdown('**Description**')
                st.info(
                    'The highest month is June and the lowest is May. The mean is 720, but since my datas are inequals (i couldnt recover all my datas in may) this number is not significant.'
                    'In general i watch more videos during school time than summertime. ')

            if option2 == 'May'and len(selection) != 0:
                st.markdown('**Description**')
                st.info('Not much videos because of the lack of datas. We can see that I saw 4 videos on Monday')
            if option2 == 'June':
                st.markdown('**Description**')
                st.info('It is the month I saw the most videos. ')
            if option2 == 'July':
                st.subheader('Description')
                st.info('I was on vacation so i watched less videos ')

            if option2 == 'August':
                st.markdown('**Description**')
                st.info('')
            if option2 == 'September':
                st.markdown('**Description**')
                st.info(
                    'Back to school, so I watched more video than during summer. Mostly to understand somes '
                    'courses and notion that we see on classes')
            if option2 == 'October':
                st.markdown('**Description**')
                st.info('On progress ... not sufficient datas yet')

        # --------------------------------- MONTHS -----------------------------------

        if option == 'Month' and option2 == 'All':
            plot_all_months(by_month, selection)
            if "Pie chart" in selection:
                plot_pie_chart(months, by_month.values)

        if option == 'Month' and option2 != 'All':
            plot_days_in_month(option2, df, selection)

        # --------------------------------- DAY-----------------------------------
        if option == 'Day':
            plot_all_months(by_day, selection)
            if "Pie chart" in selection:
                plot_pie_chart(week, by_day.values)

        # --------------------------------- HOUR-----------------------------------
        if option == 'Hour':
            plot_all_months(by_hour, selection)


if __name__ == '__main__':
    main()
