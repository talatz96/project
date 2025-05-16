import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

# === Dummy Data Generation ===
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
}

df = pd.DataFrame(data)

# Format columns
df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
df['Date'] = df['timestamp_utc'].dt.date
df['Hour'] = df['timestamp_utc'].dt.hour
df['Bullying'] = pd.to_numeric(df['Bullying'], errors='coerce').fillna(0).astype(int)

# === Streamlit App ===
st.set_page_config(page_title="Social Media Bullying Dashboard", layout="wide")
st.title("📊 Social Media Bullying Trends Dashboard")

# === Sidebar Filters ===
st.sidebar.header("🔍 Filter Data")
date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])
platforms = st.sidebar.multiselect("Platforms", df['Platform'].unique(), default=df['Platform'].unique())
subreddits = st.sidebar.multiselect("Subreddits", df['Subreddit'].unique(), default=df['Subreddit'].unique())
bullying_only = st.sidebar.checkbox("Show only bullying posts")

# Apply Filters
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

# === KPIs ===
st.markdown("### 📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts", len(filtered_df))
col2.metric("% Bullying Posts", f"{(filtered_df['Bullying'].mean()) * 100:.1f}%" if not filtered_df.empty else "0.0%")
col3.metric("Most Active Subreddit", filtered_df['Subreddit'].mode().values[0] if not filtered_df.empty else "N/A")
col4.metric("Top Platform", filtered_df['Platform'].mode().values[0] if not filtered_df.empty else "N/A")

# === Interactive Date Range Slider for Chart ===
st.subheader("📅 Filter by Date Range")
min_date, max_date = df['Date'].min(), df['Date'].max()
selected_range = st.slider("Select Date Range", min_value=min_date, max_value=max_date,
                           value=(min_date, max_date), format="YYYY-MM-DD")
mask_date = (df['Date'] >= selected_range[0]) & (df['Date'] <= selected_range[1])
filtered_by_date_df = df[mask_date]

# === Chart 1: Bullying Posts by Date ===
st.subheader("1. Bullying Posts Over Time")
bully_by_date = filtered_by_date_df[filtered_by_date_df['Bullying'] == 1] \
    .groupby('Date').size().reset_index(name='Bullying Posts')
fig1 = px.bar(bully_by_date, x='Date', y='Bullying Posts',
              title='Bullying Posts Over Time (Filtered)',
              labels={'Bullying Posts': 'Count'})
st.plotly_chart(fig1, use_container_width=True)

# === Chart 2: Bullying vs Non-Bullying by Subreddit ===
st.subheader("2. Bullying vs Non-Bullying by Subreddit")
bully_by_subreddit = df.groupby(['Subreddit', 'Bullying']).size().reset_index(name='Count')
fig2 = px.bar(bully_by_subreddit, x='Subreddit', y='Count', color='Bullying',
              barmode='group', title='Post Distribution by Subreddit & Label')
st.plotly_chart(fig2, use_container_width=True)

# === Chart 3: Average Comments & Total Posts ===
st.subheader("3. Engagement: Avg Comments & Post Count")
agg_df = df.groupby('Bullying').agg({
    'Comments': 'mean',
    'id': 'count'
}).rename(columns={'id': 'Total Posts'}).reset_index()
agg_df['Bullying'] = agg_df['Bullying'].map({0: 'Non-Bullying', 1: 'Bullying'})
fig3 = px.bar(agg_df.melt(id_vars='Bullying', var_name='Metric', value_name='Average'),
              x='Bullying', y='Average', color='Metric', barmode='group',
              title='Average Comments & Total Posts by Label')
st.plotly_chart(fig3, use_container_width=True)

# === Chart 4: Top 5 Subreddits of Selected Month ===
st.subheader("4. Top 5 Subreddits This Month")
month = st.selectbox("Select Month", sorted(df['timestamp_utc'].dt.strftime("%Y-%m").unique(), reverse=True))
top_subs = df[df['timestamp_utc'].dt.strftime("%Y-%m") == month] \
    .groupby('Subreddit').size().nlargest(5).reset_index(name='Post Count')
fig4 = px.bar(top_subs, x='Subreddit', y='Post Count', title=f'Top 5 Subreddits in {month}')
st.plotly_chart(fig4, use_container_width=True)

# === Engagement Chart: Score vs Comments ===
st.subheader("5. Score vs Comments Engagement")
fig_engage = px.scatter(filtered_df, x='Score', y='Comments',
                        color=filtered_df['Bullying'].map({1: 'Bullying', 0: 'Non-Bullying'}),
                        hover_data=['Topic', 'Subreddit'],
                        title='Engagement: Score vs Comments')
st.plotly_chart(fig_engage, use_container_width=True)

# === Word Cloud ===
st.subheader("6. 🧠 Word Cloud of Topics")
if not filtered_df.empty and filtered_df['Topic'].notna().any():
    wordcloud_data = ' '.join(filtered_df['Topic'].dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(wordcloud_data)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
else:
    st.info("No text available to generate a word cloud.")

# === Raw Data Toggle ===
if st.checkbox("📄 Show Raw Data"):
    st.dataframe(df.head(20))
