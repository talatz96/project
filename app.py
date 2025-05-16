import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

# ===============================
# CONFIG: Set dark theme
st.set_page_config(page_title="Bullying Dashboard", layout="wide")
st.markdown("<style>body { background-color: #111; color: white; }</style>", unsafe_allow_html=True)
# ===============================

# === Generate Dummy Data ===
data = {
    'id': [f"1kn{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4))}" for _ in range(50)],
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
    ] * 3,
    'text': [None]*50,
    'url': [f"https://newswebsite.com/article/{i}" for i in range(50)],
    'Score': [random.randint(100, 50000) for _ in range(50)],
    'Comments': [random.randint(5, 2000) for _ in range(50)],
    'Subreddit': random.choices(['news', 'politics', 'technology', 'education', 'socialmedia'], k=50),
    'timestamp_utc': [(datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(50)],
    'Platform': ['Reddit'] * 50,
    'Bullying': random.choices([0, 1], weights=[0.7, 0.3], k=50),
}

df = pd.DataFrame(data)
df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'], errors='coerce')
df['Date'] = df['timestamp_utc'].dt.date
df['Hour'] = df['timestamp_utc'].dt.hour

# === Sidebar Filters (no date) ===
st.sidebar.header("🔍 Filter Data")
platforms = st.sidebar.multiselect("Platforms", df['Platform'].unique(), default=df['Platform'].unique())
subreddits = st.sidebar.multiselect("Subreddits", df['Subreddit'].unique(), default=df['Subreddit'].unique())
bullying_only = st.sidebar.checkbox("Show only bullying posts")

# === Filter Data ===
mask = (df['Platform'].isin(platforms)) & (df['Subreddit'].isin(subreddits))
if bullying_only:
    mask &= df['Bullying'] == 1
filtered_df = df[mask]

# === Title ===
st.title("📊 Cyberbullying Trends Dashboard")

# === KPI Cards ===
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts", len(filtered_df))
col2.metric("Bullying %", f"{(filtered_df['Bullying'].mean()) * 100:.1f}%")
col3.metric("Top Subreddit", filtered_df['Subreddit'].mode()[0] if not filtered_df.empty else "N/A")
col4.metric("Platform", filtered_df['Platform'].mode()[0] if not filtered_df.empty else "N/A")

# === Bullying by Date Chart ===
st.subheader("📅 1. Bullying Posts by Date")
bully_by_date = filtered_df[filtered_df['Bullying'] == 1].groupby('Date').size().reset_index(name='Bullying Posts')
fig1 = px.bar(bully_by_date, x='Date', y='Bullying Posts', title='Bullying Posts Over Time', template='plotly_dark')
st.plotly_chart(fig1, use_container_width=True)

# === Subreddit Breakdown Pie ===
st.subheader("🥧 Bullying vs Non-Bullying by Subreddit")
bully_by_sub = filtered_df.groupby(['Subreddit', 'Bullying']).size().reset_index(name='Count')
fig2 = px.bar(bully_by_sub, x='Subreddit', y='Count', color='Bullying',
              barmode='group', title='Bullying vs Non-Bullying by Subreddit', template='plotly_dark')
st.plotly_chart(fig2, use_container_width=True)

# === Avg Comments & Posts ===
st.subheader("📈 3. Engagement Metrics")
agg_df = filtered_df.groupby('Bullying').agg({'Comments': 'mean', 'id': 'count'}).rename(columns={'id': 'Total Posts'}).reset_index()
agg_df['Bullying'] = agg_df['Bullying'].map({0: 'Non-Bullying', 1: 'Bullying'})
fig3 = px.bar(agg_df.melt(id_vars='Bullying', var_name='Metric', value_name='Average'),
              x='Bullying', y='Average', color='Metric', barmode='group',
              title='Avg. Comments & Posts by Bullying Label', template='plotly_dark')
st.plotly_chart(fig3, use_container_width=True)

# === Top Subreddits of the Month ===
st.subheader("⭐ 4. Top 5 Subreddits of the Month")
df['Month'] = df['timestamp_utc'].dt.strftime("%Y-%m")
month = st.selectbox("Select Month", sorted(df['Month'].unique(), reverse=True))
top5 = df[df['Month'] == month]['Subreddit'].value_counts().nlargest(5).reset_index(name='Post Count')
top5.columns = ['Subreddit', 'Post Count']
fig4 = px.bar(top5, x='Subreddit', y='Post Count', title=f'Top 5 Subreddits - {month}', template='plotly_dark')
st.plotly_chart(fig4, use_container_width=True)

# === Word Cloud ===
st.subheader("🌐 Word Cloud")
if not filtered_df.empty:
    text = ' '.join(filtered_df['Topic'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='Set2').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
else:
    st.warning("No text available for word cloud.")

# === Optional Raw Data ===
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)
