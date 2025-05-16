import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

# --- Set dark theme ---
st.set_page_config(layout="wide", page_title="Cyberbullying Dashboard")
st.markdown("""
    <style>
        .main { background-color: #0e1117; color: white; }
        .st-bf, .st-ag, .st-af { background-color: #0e1117; color: white; }
        .st-c4 { color: white; }
    </style>
""", unsafe_allow_html=True)

# --- Generate dummy data ---
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
    'timestamp_utc': [(datetime.now() - timedelta(days=random.randint(0, 3), hours=random.randint(0, 23))) for _ in range(20)],
    'Platform': ['Reddit'] * 20,
    'Bullying': random.choices([0, 1], weights=[0.7, 0.3], k=20),
}

df = pd.DataFrame(data)
df['Hour'] = df['timestamp_utc'].dt.hour

# --- UI Title ---
st.title("📊 Social Media Cyberbullying Dashboard")

# === Top Filters ===
st.subheader("📅 Select Date Range")
min_date = df['timestamp_utc'].min().date()
max_date = df['timestamp_utc'].max().date()
date_range = st.slider(
    "Filter by Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# === Sidebar Filters ===
st.sidebar.header("🔍 Filter Options")
platforms = st.sidebar.multiselect("Platforms", df['Platform'].unique(), default=df['Platform'].unique())
subreddits = st.sidebar.multiselect("Subreddits", df['Subreddit'].unique(), default=df['Subreddit'].unique())
bullying_only = st.sidebar.checkbox("Show only bullying posts")

# === Filtering Data ===
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mask = (
    (df['timestamp_utc'].dt.date >= start_date.date()) &
    (df['timestamp_utc'].dt.date <= end_date.date()) &
    (df['Platform'].isin(platforms)) &
    (df['Subreddit'].isin(subreddits))
)
if bullying_only:
    mask &= df['Bullying'] == 1
filtered_df = df[mask]

# === KPIs ===
st.markdown("### 📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts", len(filtered_df))
col2.metric("% Bullying Posts", f"{(filtered_df['Bullying'].mean()) * 100:.1f}%")
col3.metric("Most Active Subreddit", filtered_df['Subreddit'].mode().values[0] if not filtered_df.empty else "N/A")
col4.metric("Top Platform", filtered_df['Platform'].mode().values[0] if not filtered_df.empty else "N/A")

# === Bullying Posts by Date ===
st.subheader("1. 📅 Number of Bullying Posts by Date")
bully_by_date = filtered_df[filtered_df['Bullying'] == 1].groupby(filtered_df['timestamp_utc'].dt.date).size().reset_index(name='Bullying Posts')
fig1 = px.bar(bully_by_date, x='timestamp_utc', y='Bullying Posts', title='Bullying Posts Over Time')
st.plotly_chart(fig1, use_container_width=True)

# === Bullying vs Non-Bullying by Subreddit ===
st.subheader("2. ⚖️ Bullying vs Non-Bullying by Subreddit")
bully_by_subreddit = filtered_df.groupby(['Subreddit', 'Bullying']).size().reset_index(name='Count')
fig2 = px.bar(bully_by_subreddit, x='Subreddit', y='Count', color='Bullying', barmode='group')
st.plotly_chart(fig2, use_container_width=True)

# === Average Engagement ===
st.subheader("3. 📊 Avg Comments & Posts by Bullying Status")
agg_df = filtered_df.groupby('Bullying').agg({'Comments': 'mean', 'id': 'count'}).rename(columns={'id': 'Total Posts'}).reset_index()
agg_df['Bullying'] = agg_df['Bullying'].map({0: 'Non-Bullying', 1: 'Bullying'})
fig3 = px.bar(agg_df.melt(id_vars='Bullying', var_name='Metric', value_name='Average'),
              x='Bullying', y='Average', color='Metric', barmode='group')
st.plotly_chart(fig3, use_container_width=True)

# === Top Subreddits of Month ===
st.subheader("4. 🏆 Top 5 Subreddits of the Month")
month = st.selectbox("Select Month", sorted(df['timestamp_utc'].dt.strftime("%Y-%m").unique(), reverse=True))
top_subs = filtered_df[df['timestamp_utc'].dt.strftime("%Y-%m") == month].groupby('Subreddit').size().nlargest(5).reset_index(name='Post Count')
fig4 = px.bar(top_subs, x='Subreddit', y='Post Count', title=f'Top 5 Subreddits in {month}')
st.plotly_chart(fig4, use_container_width=True)

# === Word Cloud ===
st.subheader("5. 🧠 Word Cloud of Topics")
if not filtered_df.empty and filtered_df['Topic'].notna().any():
    wordcloud_data = ' '.join(filtered_df['Topic'].dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='black').generate(wordcloud_data)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
else:
    st.warning("No topic data available for word cloud.")

# === Optional: Show raw data ===
if st.checkbox("Show raw data"):
    st.write(filtered_df.head(20))
