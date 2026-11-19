import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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
            base = 300
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                base = 800
            elif 10 <= hour <= 16:
                base = 500
            else:
                base = 150

            flow = int(np.random.normal(base, base * 0.15))
            flow = max(flow, 20)

            speed = round(np.random.normal(45 - (flow / 100), 5), 1)
            speed = max(speed, 5)

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

df = pd.DataFrame(rows)
df.to_csv('city_traffic.csv', index=False, encoding='utf-8-sig')
print(df.head())
print(f'共生成 {len(df)} 条数据')