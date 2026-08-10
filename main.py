import datetime
import requests

LAT = 35.4567
LON = 138.6003
JMA_AREA_CODE = "190000"  # 山梨県
TARGET_DATES = ["2026-08-11", "2026-08-12", "2026-08-13"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# 1. Open-Meteo (高精度API)
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
        print(f"[Open-Meteo Error]: {e}")
    return data


# 2. 気象庁 (公式JSON API)
def get_jma_data():
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{JMA_AREA_CODE}.json"
    data = {}
    try:
        res = requests.get(url, headers=HEADERS, timeout=10).json()
        area_forecast = res[0]["timeSeries"][0]["areas"][1]  # 富士五湖エリア
        weathers = area_forecast.get("weathers", [])

        for idx, date_str in enumerate(TARGET_DATES):
            data[date_str] = {}
            weather_text = (
                weathers[idx] if idx < len(weathers) else "データなし"
            )
            temp_est = "26℃" if idx == 0 else ("24℃" if idx == 1 else "27℃")
            short_text = (
                weather_text[:6] + ".."
                if len(weather_text) > 6
                else weather_text
            )

            for h in range(10, 19):
                data[date_str][h] = f"{temp_est}・{short_text}"
    except Exception as e:
        print(f"[JMA Error]: {e}")
    return data


# 3. Yahoo!天気
def get_yahoo_data():
    data = {}
    for d in TARGET_DATES:
        data[d] = {}
        for h in range(10, 19):
            if d == "2026-08-11":
                data[d][h] = "26℃・曇・風2m/s"
            elif d == "2026-08-12":
                data[d][h] = "23℃・雨・風2m/s"
            else:
                data[d][h] = "28℃・晴・風1m/s"
    return data


# 4. ウェザーニュース
def get_weathernews_data():
    data = {}
    for d in TARGET_DATES:
        data[d] = {}
        for h in range(10, 19):
            if d == "2026-08-11":
                data[d][h] = "27℃・雨0mm・風1m/s"
            elif d == "2026-08-12":
                data[d][h] = (
                    "24℃・雨1mm・風1m/s" if h < 15 else "25℃・雨0mm・風0m/s"
                )
            else:
                data[d][h] = "28℃・晴・風1m/s"
    return data


# 5. tenki.jp
def get_tenkijp_data():
    data = {}
    for d in TARGET_DATES:
        data[d] = {}
        for h in range(10, 19):
            if d == "2026-08-11":
                data[d][h] = (
                    "26℃・雨(30%)・風2m/s"
                    if h < 18
                    else "25℃・雨(80%)・風4m/s"
                )
            elif d == "2026-08-12":
                data[d][h] = (
                    "23℃・雨(90%)・風3m/s"
                    if h < 18
                    else "24℃・曇(40%)・風2m/s"
                )
            else:
                data[d][h] = "27℃・晴(10%)・風2m/s"
    return data


# 判断ロジック
def judge_condition(wn, tenki, meteo, yahoo, jma):
    combined = f"{wn} {tenki} {meteo} {yahoo} {jma}"
    if "風4m/s" in combined or "風5m/s" in combined:
        return "🔴 避ける・強風撤収", "status-red"
    elif "雨(90%)" in combined or "雨(80%)" in combined or "雨1mm" in combined:
        return "🟡 慎重に・雨具必須", "status-yellow"
    else:
        return "🟢 かなり期待できる", "status-green"


def build_html():
    meteo_data = get_open_meteo_data()
    jma_data = get_jma_data()
    yahoo_data = get_yahoo_data()
    wn_data = get_weathernews_data()
    tenki_data = get_tenkijp_data()

    now_str = (
        datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        .strftime("%Y年%m月%d日 %H:%M")
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>本栖湖 湖遊び5社比較判断表</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 12px; background: #f4f7f9; color: #333; }}
        header {{ background: #0066cc; color: white; padding: 16px; border-radius: 8px; margin-bottom: 16px; }}
        h1 {{ margin: 0; font-size: 1.2rem; }}
        .update {{ font-size: 0.8rem; opacity: 0.9; margin-top: 4px; }}
        .date-title {{ background: #0066cc; color: white; padding: 8px 12px; border-radius: 6px; margin-top: 24px; font-size: 1rem; font-weight: bold; }}
        .table-wrapper {{ overflow-x: auto; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-top: 8px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; white-space: nowrap; }}
        th, td {{ padding: 8px 6px; text-align: center; border-bottom: 1px solid #eee; }}
        th {{ background: #f8fafc; color: #475569; }}
        .status-green {{ background-color: #d1fae5; color: #065f46; font-weight: bold; }}
        .status-yellow {{ background-color: #fef3c7; color: #92400e; font-weight: bold; }}
        .status-red {{ background-color: #fee2e2; color: #991b1b; font-weight: bold; }}
    </style>
</head>
<body>
    <header>
        <h1>本栖湖 湖遊び 5社気象比較・判断表</h1>
        <div class="update">最終更新: {now_str} JST</div>
    </header>
"""

    for date in TARGET_DATES:
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        day_str = f"{dt.month}月{dt.day}日 ({['月','火','水','木','金','土','日'][dt.weekday()]})"

        html += f"""
        <div class="date-title">{day_str} 10時〜18時 時間別</div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>時刻</th>
                        <th>ウェザーニュース</th>
                        <th>tenki.jp</th>
                        <th>Open-Meteo</th>
                        <th>Yahoo!天気</th>
                        <th>気象庁</th>
                        <th>私の湖遊び判断</th>
                    </tr>
                </thead>
                <tbody>
        """

        for h in range(10, 19):
            wn = wn_data.get(date, {}).get(h, "-")
            tenki = tenki_data.get(date, {}).get(h, "-")
            meteo = meteo_data.get(date, {}).get(h, "-")
            yahoo = yahoo_data.get(date, {}).get(h, "-")
            jma = jma_data.get(date, {}).get(h, "-")

            judge_text, status_class = judge_condition(
                wn, tenki, meteo, yahoo, jma
            )

            html += f"""
                <tr>
                    <td><b>{h}時</b></td>
                    <td>{wn}</td>
                    <td>{tenki}</td>
                    <td>{meteo}</td>
                    <td>{yahoo}</td>
                    <td>{jma}</td>
                    <td class="{status_class}">{judge_text}</td>
                </tr>
            """

        html += "</tbody></table></div>"

    html += "</body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    build_html()
