import yfinance as yf
import requests
import os
from datetime import datetime

# 설정: 새로운 웹훅 URL (시장 기상청 채널용)
DISCORD_WEBHOOK_URL = os.environ.get('MARKET_WEBHOOK')

# 모니터링할 지수 리스트 (나스닥, S&P500, 반도체, VIX)
INDEX_TICKERS = {
    "^IXIC": "나스닥 (Nasdaq)",
    "^GSPC": "S&P 500",
    "^SOX": "반도체 (SOX)",
    "^VIX": "공포지수 (VIX)"
}

def get_index_data():
    embed_fields = []
    overall_color = 0x2b2d31 # 기본 다크 모드 색상
    
    for ticker, name in INDEX_TICKERS.items():
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="2d")
            if len(data) < 2: continue
            
            curr = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2]
            change = ((curr - prev) / prev) * 100
            
            # 상승/하락에 따른 이모지 및 상태
            arrow = "🔺" if change > 0 else "🔻"
            if name == "공포지수 (VIX)":
                status = "🟢 안정" if change < 0 else "⚠️ 주의"
            else:
                status = "🚀 강세" if change > 0 else "🧊 약세"

            embed_fields.append({
                "name": f"{name}",
                "value": f"**{curr:,.2f}** ({change:+.2f}%) {arrow}\n`상태: {status}`",
                "inline": True
            })
        except Exception as e:
            print(f"❌ {name} 데이터 오류: {e}")

    return embed_fields

def send_to_discord():
    fields = get_index_data()
    if not fields: return

    payload = {
        "embeds": [{
            "title": "🌍 글로벌 주요 지수 실시간 기상도",
            "description": f"업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (KST)",
            "fields": fields,
            "color": 3447003, # 파란색 계열
            "footer": {"text": "주린이 계산기 - 데이터 지연 약 15분"}
        }]
    }
    
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    send_to_discord()
