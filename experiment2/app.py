import st_launch
st_launch.launch()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# ==================== 页面配置 ====================
st.set_page_config(page_title='城市交通数据看板', layout='wide')

# ==================== 初始化数据 ====================
if 'traffic_df' not in st.session_state:
    np.random.seed(42)
    regions = ['城东区', '城西区', '城南区', '城北区', '市中心']
    road_segments = {
        '城东区': ['东大街', '东环路', '东站路'],
        '城西区': ['西大街', '西环路', '西站路'],
        '城南区': ['南大街', '南环路', '南站路'],
        '城北区': ['北大街', '北环路', '北站路'],
        '市中心': ['中山路', '人民路', '解放路'],
    }
    transport_modes = ['私家车', '公交车', '地铁', '出租车', '网约车']
    start = datetime(2024, 6, 1)
    rows = []
    for day in range(7):
        for hour in range(24):
            for region in regions:
                if 7 <= hour <= 9 or 17 <= hour <= 19:
                    base = 800
                elif 10 <= hour <= 16:
                    base = 500
                else:
                    base = 150
                flow = max(int(np.random.normal(base, base * 0.15)), 20)
                speed = max(round(np.random.normal(45 - flow / 100, 5), 1), 5)
                congestion = round(min(flow / 1000 * 10, 10), 1)
                rows.append({
                    '日期': (start + timedelta(days=day)).strftime('%Y-%m-%d'),
                    '小时': hour,
                    '区域': region,
                    '路段': np.random.choice(road_segments[region]),
                    '交通方式': np.random.choice(transport_modes),
                    '车流量': flow,
                    '平均车速': speed,
                    '拥堵指数': congestion,
                    '事故数': np.random.poisson(1 if congestion > 7 else 0.2),
                })
    st.session_state.traffic_df = pd.DataFrame(rows)

df = st.session_state.traffic_df

# ==================== 侧边栏：主题 & 刷新设置 ====================
with st.sidebar:
    st.header('🎨 主题模式')
    theme = st.radio('选择主题', ['亮色', '暗色'], horizontal=True)

    st.markdown('---')
    st.header('⚙️ 实时刷新')
    auto_refresh = st.checkbox('开启自动刷新', value=False)
    refresh_interval = st.slider('刷新间隔（秒）', 3, 60, 5)
    if st.button('🔄 手动新增一批数据'):
        new_rows = []
        for region in df['区域'].unique():
            base = np.random.randint(200, 900)
            new_rows.append({
                '日期': datetime.now().strftime('%Y-%m-%d'),
                '小时': datetime.now().hour,
                '区域': region,
                '路段': np.random.choice(df[df['区域'] == region]['路段'].unique()),
                '交通方式': np.random.choice(df['交通方式'].unique()),
                '车流量': base,
                '平均车速': max(round(45 - base / 100 + np.random.normal(0, 3), 1), 5),
                '拥堵指数': round(min(base / 1000 * 10, 10), 1),
                '事故数': np.random.poisson(1 if base > 700 else 0.2),
            })
        st.session_state.traffic_df = pd.concat(
            [st.session_state.traffic_df, pd.DataFrame(new_rows)],
            ignore_index=True
        )
        st.rerun()

    st.markdown('---')
    st.header('🔍 筛选条件')
    date_list = sorted(df['日期'].unique())
    selected_dates = st.multiselect('选择日期', options=date_list, default=date_list)
    region_list = sorted(df['区域'].unique())
    selected_regions = st.multiselect('选择区域', options=region_list, default=region_list)
    mode_list = sorted(df['交通方式'].unique())
    selected_modes = st.multiselect('选择交通方式', options=mode_list, default=mode_list)

# ==================== 主题样式注入 ====================
if theme == '亮色':
    st.markdown("""
    <style>
        .main { animation: fadeIn 1s ease-in; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        div[data-testid="stMetric"] {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .warning-blink {
            animation: blink 1s infinite;
            color: #d9534f;
            font-weight: bold;
            font-size: 18px;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        .main { animation: fadeIn 1s ease-in; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        div[data-testid="stMetric"] {
            background-color: #1c1f26;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(255,255,255,0.05);
            color: #fafafa;
        }
        h1, h2, h3, h4, h5, h6, p, span, label { color: #fafafa !important; }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .warning-blink {
            animation: blink 1s infinite;
            color: #ff6b6b;
            font-weight: bold;
            font-size: 18px;
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== 筛选数据 ====================
df_filtered = df[
    (df['日期'].isin(selected_dates)) &
    (df['区域'].isin(selected_regions)) &
    (df['交通方式'].isin(selected_modes))
]

if df_filtered.empty:
    st.warning('当前筛选条件下没有数据，请调整筛选条件。')
    st.stop()

# ==================== 标题 ====================
st.title('🚦 城市交通数据看板')
st.markdown('---')

# ==================== 预警监控 ====================
CONGESTION_THRESHOLD = 7.0
ACCIDENT_THRESHOLD = 5

avg_congestion_now = df_filtered['拥堵指数'].mean()
total_accidents_now = df_filtered['事故数'].sum()

warn_col1, warn_col2 = st.columns(2)
with warn_col1:
    if avg_congestion_now > CONGESTION_THRESHOLD:
        st.markdown('<p class="warning-blink">🚨 拥堵指数超阈值，请立即关注！</p>', unsafe_allow_html=True)
    else:
        st.success(f"✅ 当前平均拥堵指数 {avg_congestion_now:.2f}，处于正常范围。")
with warn_col2:
    if total_accidents_now > ACCIDENT_THRESHOLD:
        st.warning(f"⚠️ 事故总数 {total_accidents_now}，高于警戒值 {ACCIDENT_THRESHOLD}。")
    else:
        st.success(f"✅ 当前事故总数 {total_accidents_now}，处于正常范围。")

# ==================== 数据概览区 ====================
col1, col2, col3, col4 = st.columns(4)
col1.metric('总车流量', f"{df_filtered['车流量'].sum():,}")
col2.metric('平均车速', f"{df_filtered['平均车速'].mean():.1f} km/h")
col3.metric(
    '平均拥堵指数',
    f"{avg_congestion_now:.2f}",
    delta=f"{avg_congestion_now - CONGESTION_THRESHOLD:.2f}",
    delta_color="inverse"
)
col4.metric('事故总数', f"{total_accidents_now}")

st.markdown('---')

# ==================== 维度统计区 ====================
col_left, col_right = st.columns(2)
with col_left:
    region_flow = df_filtered.groupby('区域')['车流量'].sum().reset_index()
    fig_bar = px.bar(region_flow, x='区域', y='车流量', title='各区域车流量对比')
    st.plotly_chart(fig_bar, use_container_width=True)
with col_right:
    mode_flow = df_filtered.groupby('交通方式')['车流量'].sum().reset_index()
    fig_pie = px.pie(mode_flow, names='交通方式', values='车流量', title='交通方式占比')
    st.plotly_chart(fig_pie, use_container_width=True)

# ==================== 趋势分析区 ====================
col_left2, col_right2 = st.columns(2)
with col_left2:
    hour_flow = df_filtered.groupby('小时')['车流量'].sum().reset_index()
    fig_line = px.line(hour_flow, x='小时', y='车流量', title='24小时车流量趋势')
    st.plotly_chart(fig_line, use_container_width=True)
with col_right2:
    road_congestion = df_filtered.groupby('路段')['拥堵指数'].mean().reset_index()
    road_congestion = road_congestion.sort_values('拥堵指数', ascending=True).tail(10)
    fig_road = px.bar(road_congestion, x='拥堵指数', y='路段', orientation='h', title='路段拥堵排名')
    st.plotly_chart(fig_road, use_container_width=True)

st.markdown('---')

# ==================== 多维度分析区 ====================
st.subheader('🔥 区域-小时车流量热力图')
heatmap_data = df_filtered.pivot_table(
    index='区域', columns='小时', values='车流量', aggfunc='sum'
)
fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x='小时', y='区域', color='车流量'),
    color_continuous_scale='YlOrRd',
    aspect='auto'
)
st.plotly_chart(fig_heatmap, use_container_width=True)

col_r1, col_r2 = st.columns(2)
with col_r1:
    st.subheader('🕸️ 各区域综合指标雷达图')
    radar_data = df_filtered.groupby('区域').agg({
        '车流量': 'sum',
        '平均车速': 'mean',
        '拥堵指数': 'mean',
        '事故数': 'sum'
    }).reset_index()
    for c in ['车流量', '平均车速', '拥堵指数', '事故数']:
        mx, mn = radar_data[c].max(), radar_data[c].min()
        radar_data[c] = (radar_data[c] - mn) / (mx - mn) if mx > mn else 0.5
    fig_radar = px.line_polar(
        radar_data.melt(id_vars='区域', var_name='指标', value_name='数值'),
        r='数值', theta='指标', color='区域', line_close=True
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_r2:
    st.subheader('📊 平均拥堵指数仪表盘')
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_congestion_now,
        title={'text': '平均拥堵指数'},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': 'orange'},
            'steps': [
                {'range': [0, 4], 'color': '#d4f5d4'},
                {'range': [4, 7], 'color': '#fff3cd'},
                {'range': [7, 10], 'color': '#f8d7da'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': CONGESTION_THRESHOLD
            }
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown('---')

# ==================== 区域钻取 ====================
st.subheader('🔎 区域数据钻取')
drill_region = st.selectbox('选择一个区域查看详情', df_filtered['区域'].unique())
drill_df = df_filtered[df_filtered['区域'] == drill_region]
st.write(f"**{drill_region}** 共 {len(drill_df)} 条记录，总车流量 {drill_df['车流量'].sum():,}")
st.dataframe(drill_df.head(50), use_container_width=True)

st.markdown('---')

# ==================== 明细数据区 ====================
st.subheader('📋 明细数据')

sort_col1, sort_col2 = st.columns([2, 1])
with sort_col1:
    sort_col = st.selectbox('排序字段', ['车流量', '平均车速', '拥堵指数', '事故数'])
with sort_col2:
    sort_order = st.radio('排序方式', ['降序', '升序'], horizontal=True)

ascending = (sort_order == '升序')
sorted_df = df_filtered.sort_values(sort_col, ascending=ascending)
st.dataframe(sorted_df.head(100), use_container_width=True)

# ==================== 数据导出 ====================
csv = sorted_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label='📥 下载当前筛选数据（CSV）',
    data=csv,
    file_name=f'city_traffic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
    mime='text/csv'
)

# ==================== 自动刷新 ====================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()