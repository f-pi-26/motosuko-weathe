import datetime
import requests

LAT = 35.4567
LON = 138.6003
TARGET_DATES = ["2026-08-11", "2026-08-12", "2026-08-13"]


def get_open_meteo_data():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,precipitation,wind_speed_10m&timezone=Asia%2FTokyo"
    data = {}
    try:
        res = requests.get(url, timeout=10).json()
        hourly = res.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        precip = hourly.get("precipitation", [])
        wind = hourly.get("wind_speed_10m", [])

        for t, temp, p, w in zip(times, temps, precip, wind):
            date_str, time_str = t.split("T")
            hour = int(time_str.split(":")[0])
            if date_str not in data:
                data[date_str] = {}
            wind_ms = round(w / 3.6, 1) if w is not None else 0
            data[date_str][
                hour
            ] = f"{temp}℃・雨{p}mm・風{wind_ms}m/s"
    except Exception as e:
        print(f"API Error: {e}")
    return data


def judge_condition(meteo_text):
    if "風4" in meteo_text or "風5" in meteo_text:
        return "🔴 避ける・撤収推奨", "status-red"
    elif "雨1" in meteo_text or "雨2" in meteo_text:
        return "🟡 慎重に・雨具必須", "status-yellow"
    else:
        return "🟢 良好・遊べそう", "status-green"


def build_html():
    meteo_data = get_open_meteo_data()
    now_str = (
        datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        .strftime("%Y年%m月%d日 %H:%M")
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>本栖湖 湖遊び判断表</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 12px; background: #f4f7f9; color: #333; }}
        header {{ background: #0066cc; color: white; padding: 16px; border-radius: 8px; margin-bottom: 16px; }}
        h1 {{ margin: 0; font-size: 1.2rem; }}
        .update {{ font-size: 0.8rem; opacity: 0.9; margin-top: 4px; }}
        .table-wrapper {{ overflow-x: auto; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; white-space: nowrap; }}
        th, td {{ padding: 8px; text-align: center; border-bottom: 1px solid #eee; }}
        th {{ background: #f8fafc; }}
        .status-green {{ background-color: #d1fae5; color: #065f46; font-weight: bold; }}
        .status-yellow {{ background-color: #fef3c7; color: #92400e; font-weight: bold; }}
        .status-red {{ background-color: #fee2e2; color: #991b1b; font-weight: bold; }}
    </style>
</head>
<body>
    <header>
        <h1>本栖湖 湖遊び気象判断表</h1>
        <div class="update">最終更新: {now_str} JST</div>
    </header>
"""
    for date in TARGET_DATES:
        html += f"""
        <h3>{date} 時間別予報</h3>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr><th>時刻</th><th>Open-Meteo(予報)</th><th>湖遊び判断</th></tr>
                </thead>
                <tbody>
        """
        for h in range(10, 19):
            meteo = meteo_data.get(date, {}).get(h, "データなし")
            judge_text, status_class = judge_condition(meteo)
            html += f"<tr><td><b>{h}時</b></td><td>{meteo}</td><td class='{status_class}'>{judge_text}</td></tr>"
        html += "</tbody></table></div>"

    html += "</body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    build_html()
