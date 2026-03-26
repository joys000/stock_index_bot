import yfinance as yf
import requests
import os
from datetime import datetime

# 1. 환경 변수 설정
DISCORD_WEBHOOK_URL = os.environ.get('MARKET_WEBHOOK')

# 2. 모니터링 대상 확장 (한국 지수 및 환율 추가)
INDEX_TICKERS = {
    "^IXIC": "나스닥 (Nasdaq)",
    "^SOX": "반도체 (SOX)",
    "^KS11": "코스피 (KOSPI)",
    "^KQ11": "코스닥 (KOSDAQ)",
    "USDKRW=X": "원/달러 환율",
    "^VIX": "공포지수 (VIX)"
}

def get_market_data():
    fields = []
    for ticker, name in INDEX_TICKERS.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="2d")
            if len(df) < 2: continue
            
            curr = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            change = ((curr - prev) / prev) * 100
            
            # 시각적 요소 설정
            emoji = "🔴" if change > 0 else "🔵"
            arrow = "▲" if change > 0 else "▼"
            
            # 환율 및 특정 지수 특수 처리
            if "환율" in name:
                emoji = "💵"
                status = "환율 상승" if change > 0 else "환율 하락"
                val_str = f"**{curr:,.2f}원**"
            elif name == "공포지수 (VIX)":
                emoji = "⚠️" if change > 0 else "✅"
                status = "불안" if change > 0 else "안정"
                val_str = f"**{curr:,.2f}**"
            else:
                status = "강세" if change > 0 else "약세"
                val_str = f"**{curr:,.2f}**"

            fields.append({
                "name": f"{emoji} {name}",
                "value": f"{val_str}\n({change:+.2f}%) {arrow}\n`{status}`",
                "inline": True
            })
        except Exception as e:
            print(f"❌ {name} 데이터 오류: {e}")
    return fields

def run():
    if not DISCORD_WEBHOOK_URL:
        print("❌ 에러: MARKET_WEBHOOK 설정이 누락되었습니다.")
        return

    fields = get_market_data()
    if not fields: return

    payload = {
        "embeds": [{
            "title": "🌡️ 글로벌 & 국내 시장 통합 기상도",
            "description": f"조회 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (KST)",
            "color": 3066993, # 에메랄드 그린
            "fields": fields,
            "footer": {"text": "실시간 데이터 요약 - 주린이 계산기 제공"}
        }]
    }
    
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
    print("✅ 통합 지수 브리핑 전송 완료!")

if __name__ == "__main__":
    run()
