import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Cyberbullying Dashboard", layout="wide")

# Dummy data generation
data = {
    'id': [f"1kn{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4))}" for _ in range(20)],
    'Topic': [
        "US reportedly plans to slash bank rules", "More than 1,000 Starbucks baristas go on strike",
        "Harvard’s copy of Magna Carta is accessible", "Mother allegedly buys ammunition, tactical gear",
        "UnitedHealth under criminal probe", "State leaders prepare for post Roe v. Wade",
        "Walmart warns of higher prices", "Girl escapes captivity from New Jersey",
        "US transportation secretary changed wife’s file", "Mayor proposes anti-theft policy",
        "Viral TikTok shows looting in broad daylight", "Online trolls target transgender student",
        "High school student assaulted", "Online bullying spikes after school closure",
        "Reddit user shares suicide story", "News outlet covers school shooting aftermath",
        "Teen victim speaks out about bullying", "Local protest against online abuse",
        "AI-generated fake news spreads hate", "Platform rolls out new safety feature"
    ],
    'text': [None]*20,
    'url': [f"https://newswebsite.com/article/{i}" for i in range(20)],
    'Score': [random.randint(100, 50000) for _ in range(20)],
    'Comments': [random.randint(5, 2000) for _ in range(20)],
    'Subreddit': random.choices(['news', 'politics', 'technology', 'education', 'socialmedia'], k=20),
    'timestamp_utc': [(datetime.now() - timedelta(days=random.randint(0, 3), hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(20)],
    'Platform': ['Reddit'] * 20,
    'Bullying': random.choices([0, 1], weights=[0.7, 0.3], k=20),
    'Date': [(datetime.now() - timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d') for _ in range(20)],
    'Hour': [random.randint(0, 23) for _ in range(20)],
}
df = pd.DataFrame(data)
df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'], errors='coerce')
df['Date'] = pd.to_datetime(df['timestamp_utc'].dt.date)
df['Hour'] = df['timestamp_utc'].dt.hour

# === Sidebar Filters ===
st.sidebar.header("🔍 Filter Data")
date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])
platforms = st.sidebar.multiselect("Platforms", df['Platform'].unique(), default=df['Platform'].unique())
subreddits = st.sidebar.multiselect("Subreddits", df['Subreddit'].unique(), default=df['Subreddit'].unique())
bullying_only = st.sidebar.checkbox("Show only bullying posts")

# === Apply Filters ===
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mask = (
    (df['timestamp_utc'] >= start_date) &
    (df['timestamp_utc'] <= end_date) &
    (df['Platform'].isin(platforms)) &
    (df['Subreddit'].isin(subreddits))
)
if bullying_only:
    mask &= df['Bullying'] == 1

filtered_df = df[mask]

# === Title and KPIs ===
st.title("📊 Cyberbullying Monitoring Dashboard")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Posts", len(filtered_df))
kpi2.metric("% Bullying Posts", f"{(filtered_df['Bullying'].mean()) * 100:.1f}%")
kpi3.metric("Active Subreddits", filtered_df['Subreddit'].nunique())

# === Donut Chart: Bullying vs Non-Bullying ===
st.markdown("### 🧩 Bullying Distribution")
bullying_counts = filtered_df['Bullying'].value_counts().rename(index={0: 'Non-Bullying', 1: 'Bullying'})
fig_pie = go.Figure(data=[go.Pie(labels=bullying_counts.index, values=bullying_counts.values, hole=.4)])
st.plotly_chart(fig_pie, use_container_width=True)

# === Word Cloud ===
st.markdown("### ☁️ Word Cloud of Post Topics")
if not filtered_df.empty and filtered_df['Topic'].notna().any():
    wordcloud_data = ' '.join(filtered_df['Topic'].dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(wordcloud_data)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
else:
    st.warning("No text data available for the word cloud with the current filters.")

# === Bullying Trend Over Time ===
st.markdown("### 📈 Bullying Trend Over Time")
trend_df = filtered_df.copy()
trend_df['Month'] = trend_df['timestamp_utc'].dt.to_period('M').astype(str)
trend = trend_df[trend_df['Bullying'] == 1].groupby('Month').size().reset_index(name='Bullying Posts')
fig_trend = px.line(trend, x='Month', y='Bullying Posts', title="Bullying Trend Over Months")
st.plotly_chart(fig_trend, use_container_width=True)

# === Score vs Comments Scatter ===
st.markdown("### 🔥 Engagement (Score vs Comments)")
fig_engage = px.scatter(
    filtered_df,
    x='Score',
    y='Comments',
    color=filtered_df['Bullying'].map({1: 'Bullying', 0: 'Non-Bullying'}),
    hover_data=['Topic', 'Subreddit'],
    title="Engagement Level by Post Type"
)
st.plotly_chart(fig_engage, use_container_width=True)

# === Subreddit Analysis ===
st.markdown("### 📌 Subreddit Contribution")
subreddit_bars = filtered_df.groupby(['Subreddit', 'Bullying']).size().reset_index(name='Count')
fig_sub_bar = px.bar(
    subreddit_bars,
    x='Subreddit',
    y='Count',
    color=subreddit_bars['Bullying'].map({1: 'Bullying', 0: 'Non-Bullying'}),
    barmode='group',
    title="Post Count by Subreddit"
)
st.plotly_chart(fig_sub_bar, use_container_width=True)

# === Hourly Trend ===
st.markdown("### ⏰ Posting Hour Distribution")
hourly_dist = filtered_df.groupby(['Hour', 'Bullying']).size().reset_index(name='Posts')
fig_hour = px.bar(hourly_dist, x='Hour', y='Posts', color=hourly_dist['Bullying'].map({1: 'Bullying', 0: 'Non-Bullying'}),
                  barmode='group', title='Posts Distribution by Hour')
st.plotly_chart(fig_hour, use_container_width=True)

# === Raw Data Toggle ===
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df)
