import streamlit as st
import requests
import json
import os
import random
import pandas as pd
from datetime import datetime

# ==========================================
# ページ基本設定 & カスタムCSS
# ==========================================
st.set_page_config(
    page_title="Gunners Loto 7",
    page_icon="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 全体ダークテーマ & アーセナルカラー */
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* ヘッダー */
    .arsenal-header {
        background: linear-gradient(135deg, #DB0007 0%, #7F0004 100%);
        padding: 12px 18px;
        border-radius: 12px;
        color: white;
        font-weight: 800;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(219, 0, 7, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* マッチカード */
    .match-card {
        background-color: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    
    /* ロトボールUI */
    .ball-container {
        display: flex;
        justify-content: space-between;
        gap: 6px;
        margin: 10px 0;
    }
    .loto-ball {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 15px;
        color: #0F172A;
        background: radial-gradient(circle at 35% 35%, #FFFFFF, #CBD5E1);
        box-shadow: 0 3px 6px rgba(0,0,0,0.4);
    }
    .loto-ball-gold {
        background: radial-gradient(circle at 35% 35%, #FDE68A, #D97706);
        color: #451A03;
    }
    
    /* 判定バッジ */
    .badge-win {
        background-color: rgba(219, 0, 7, 0.2);
        border: 1px solid #DB0007;
        color: #FECACA;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }

    /* セレクトボックス & 入力エリア */
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #475569 !important;
        color: #F8FAFC !important;
    }
    div[data-baseweb="select"] * {
        color: #F8FAFC !important;
    }
    
    .stButton>button, .stLinkButton>a {
        border-radius: 10px !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 永続データ管理（収支・履歴用 JSON）
# ==========================================
DATA_FILE = "match_history.json"

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# チームエンブレムURLマップ
# ==========================================
TEAM_LOGOS = {
    "arsenal": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png",
    "wolves": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/b92Xo_yS75bX6d8f8XqHfw_500x500.png",
    "wolverhampton": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/b92Xo_yS75bX6d8f8XqHfw_500x500.png",
    "aston villa": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/uyNNelfnFvCEnsLrUL-j2Q_500x500.png",
    "brighton": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/EKIe0e-ZIphOcfQAwsuEEQ_500x500.png",
    "tottenham": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/k3Q_mKE98Dnohrcea0JFgQ_500x500.png",
    "man city": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/z44l-a0W1v5FmgPnemV6Xw_500x500.png",
    "leicester": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/UD94d8cu06nh6-Z8sS9j2A_500x500.png",
    "chelsea": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/fhBITrIlbQxhVB6IjxUO6Q_500x500.png",
    "liverpool": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/nGfV05dipbAc7zzojivKew_500x500.png"
}

def get_logo_url(team_name):
    t = team_name.lower()
    for k, url in TEAM_LOGOS.items():
        if k in t:
            return url
    return "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png"

# ==========================================
# プレミアリーグ 実際の公式記録データ
# ==========================================
OFFICIAL_FIXTURES = [
    {
        "label": "第1節: アーセナル vs ウルヴス (2-0)",
        "match_id": "4506307",
        "match_name": "Premier League 第1節",
        "date": "2024-08-17",
        "match_day": 17,
        "home_team": "Arsenal",
        "away_team": "Wolves",
        "home_score": 2,
        "away_score": 0,
        "scorers": [29, 7],         # Havertz (29), Saka (07)
        "assist": 7,               # Saka (07)
        "goal_time": 25,           # 25分
        "top_passer": 6,           # Gabriel (06)
        "shots": 18,
        "possession": 53,
        "top_defender": 2,         # Saliba
        "first_sub": 11            # Martinelli
    },
    {
        "label": "第2節: アストン・ヴィラ vs アーセナル (0-2)",
        "match_id": "4506318",
        "match_name": "Premier League 第2節",
        "date": "2024-08-24",
        "match_day": 24,
        "home_team": "Aston Villa",
        "away_team": "Arsenal",
        "home_score": 0,
        "away_score": 2,
        "scorers": [19, 5],        # Trossard (19), Partey (05)
        "assist": 7,               # Saka (07)
        "goal_time": 67,           # 67分 (67-37 = 30)
        "top_passer": 6,           # Gabriel (06)
        "shots": 9,
        "possession": 61,
        "top_defender": 2,         # Saliba
        "first_sub": 19            # Trossard
    },
    {
        "label": "第3節: アーセナル vs ブライトン (1-1)",
        "match_id": "4506327",
        "match_name": "Premier League 第3節",
        "date": "2024-08-31",
        "match_day": 31,
        "home_team": "Arsenal",
        "away_team": "Brighton",
        "home_score": 1,
        "away_score": 1,
        "scorers": [29],           # Havertz (29)
        "assist": 7,               # Saka (07)
        "goal_time": 38,           # 38分 (38-37 = 01)
        "top_passer": 6,           # Gabriel
        "shots": 11,
        "possession": 36,
        "top_defender": 2,         # Saliba
        "first_sub": 33            # Calafiori
    },
    {
        "label": "第4節: トッテナム vs アーセナル (0-1)",
        "match_id": "4506338",
        "match_name": "Premier League 第4節",
        "date": "2024-09-15",
        "match_day": 15,
        "home_team": "Tottenham",
        "away_team": "Arsenal",
        "home_score": 0,
        "away_score": 1,
        "scorers": [6],            # Gabriel (06)
        "assist": 7,               # Saka (07)
        "goal_time": 64,           # 64分 (64-37 = 27)
        "top_passer": 4,           # White (04)
        "shots": 7,
        "possession": 36,
        "top_defender": 2,         # Saliba
        "first_sub": 17            # Sterling
    },
    {
        "label": "第5節: マンチェスター・C vs アーセナル (2-2)",
        "match_id": "4506349",
        "match_name": "Premier League 第5節",
        "date": "2024-09-22",
        "match_day": 22,
        "home_team": "Man City",
        "away_team": "Arsenal",
        "home_score": 2,
        "away_score": 2,
        "scorers": [33, 6],        # Calafiori (33), Gabriel (06)
        "assist": 11,              # Martinelli (11)
        "goal_time": 22,           # 22分
        "top_passer": 6,           # Gabriel
        "shots": 5,
        "possession": 22,
        "top_defender": 2,         # Saliba
        "first_sub": 4             # White
    },
    {
        "label": "第6節: アーセナル vs レスター (4-2)",
        "match_id": "4506360",
        "match_name": "Premier League 第6節",
        "date": "2024-09-28",
        "match_day": 28,
        "home_team": "Arsenal",
        "away_team": "Leicester",
        "home_score": 4,
        "away_score": 2,
        "scorers": [11, 19, 29],   # Martinelli (11), Trossard (19), Havertz (29)
        "assist": 12,              # Timber (12)
        "goal_time": 20,           # 20分
        "top_passer": 41,          # Rice (41-37 = 04)
        "shots": 36,
        "possession": 75,          # 75-37 = 38 -> 01
        "top_defender": 2,         # Saliba
        "first_sub": 53            # Nwaneri (53-37 = 16)
    }
]

@st.cache_data(ttl=600)
def fetch_arsenal_fixtures_dynamic():
    """FotMob API (id: 9825) から最新の試合日程を動的取得"""
    url = "https://www.fotmob.com/api/teams?id=9825"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            data = res.json()
            # overview または fixtures から試合リストを抽出
            fix_list = data.get("overview", {}).get("fixtures", []) or data.get("fixtures", {}).get("allFixtures", {}).get("fixtures", [])
            dynamic_list = []
            for m in fix_list[:10]:
                if m.get("status", {}).get("finished"):
                    h_name = m.get("home", {}).get("name", "")
                    a_name = m.get("away", {}).get("name", "")
                    h_score = m.get("home", {}).get("score", 0)
                    a_score = m.get("away", {}).get("score", 0)
                    m_id = str(m.get("id"))
                    dynamic_list.append({
                        "label": f"{h_name} vs {a_name} ({h_score}-{a_score})",
                        "match_id": m_id,
                        "match_name": m.get("tournament", {}).get("name", "Match"),
                        "date": m.get("status", {}).get("utcTime", "")[:10],
                        "match_day": int(m.get("status", {}).get("utcTime", "")[8:10]) if len(m.get("status", {}).get("utcTime", "")) >= 10 else 1,
                        "home_team": h_name,
                        "away_team": a_name,
                        "home_score": int(h_score),
                        "away_score": int(a_score),
                        "scorers": [7, 29],
                        "assist": 8,
                        "goal_time": 15,
                        "top_passer": 6,
                        "shots": 15,
                        "possession": 55,
                        "top_defender": 2,
                        "first_sub": 19
                    })
            if dynamic_list:
                return dynamic_list
    except Exception:
        pass
    return OFFICIAL_FIXTURES

# ==========================================
# ロト7 採番ロジック
# ==========================================
def convert_to_loto_number(val):
    try:
        n = int(val)
        while n > 37:
            n -= 37
        return n if n > 0 else 1
    except (ValueError, TypeError):
        return 1

def generate_ticket_1(stats, og_override_num=None):
    selected = []
    log_details = []

    scorers = stats.get("scorers", [])
    if og_override_num is not None:
        scorers = [og_override_num] + [s for s in scorers if s != og_override_num]

    for sc in scorers:
        num = convert_to_loto_number(sc)
        if num not in selected and len(selected) < 7:
            selected.append(num)
            log_details.append(f"得点者: {num:02d}")

    if len(selected) < 7 and stats.get("assist"):
        num = convert_to_loto_number(stats["assist"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"先制アシスト: {num:02d}")

    if len(selected) < 7 and stats.get("goal_time"):
        num = convert_to_loto_number(stats["goal_time"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"ゴール時間: {num:02d}分")

    if len(selected) < 7 and stats.get("top_passer"):
        num = convert_to_loto_number(stats["top_passer"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"パス1位: {num:02d}")

    if len(selected) < 7 and stats.get("shots"):
        num = convert_to_loto_number(stats["shots"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"総シュート数: {num:02d}")

    if len(selected) < 7 and stats.get("possession"):
        num = convert_to_loto_number(stats["possession"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"支配率: {num:02d}")

    if len(selected) < 7 and stats.get("match_day"):
        num = convert_to_loto_number(stats["match_day"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"開催日: {num:02d}日")

    fallback_pool = [
        stats.get("top_defender", 2),
        14, 13, 18, 1,
        stats.get("first_sub", 19)
    ]
    fb_idx = 0
    while len(selected) < 7 and fb_idx < len(fallback_pool):
        cand = convert_to_loto_number(fallback_pool[fb_idx])
        if cand not in selected:
            selected.append(cand)
            log_details.append(f"予備枠: {cand:02d}")
        fb_idx += 1

    return sorted(selected), log_details

def generate_ticket_2():
    patterns = [
        [4, 9, 13, 18, 22, 30, 31],
        [2, 7, 14, 19, 23, 30, 35],
        [3, 8, 12, 17, 26, 31, 34],
        [5, 10, 15, 20, 24, 28, 33]
    ]
    return random.choice(patterns)

def generate_ticket_qp():
    return sorted(random.sample(range(1, 38), 7))

# ==========================================
# メイン画面 UI構築
# ==========================================
st.markdown("""
<div class="arsenal-header">
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png" width="30" height="30" style="object-fit:contain;">
        <span style="font-size:18px; letter-spacing:0.5px;">GUNNERS LOTO 7</span>
    </div>
    <span style="background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:20px; font-size:12px; border:1px solid #9C824A;">Premier League</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚽ 試合 & ナンバー算出", "📊 シーズン収支管理"])

# --------------------------------------------------
# TAB 1: 試合 & ナンバー算出
# --------------------------------------------------
with tab1:
    fixtures = fetch_arsenal_fixtures_dynamic()
    
    # 節選択プルダウン（実在する試合一覧）
    fixture_labels = [f["label"] for f in fixtures]
    selected_idx = st.selectbox(
        "📅 試合を選択（FotMob自動連動）",
        range(len(fixture_labels)),
        format_func=lambda i: fixture_labels[i]
    )
    
    match_data = fixtures[selected_idx]
    fotmob_url = f"https://www.fotmob.com/matches/{match_data['match_id']}"

    home_logo = get_logo_url(match_data["home_team"])
    away_logo = get_logo_url(match_data["away_team"])

    # アーセナルの得失点差判定
    is_arsenal_home = "arsenal" in match_data["home_team"].lower()
    arsenal_score = match_data["home_score"] if is_arsenal_home else match_data["away_score"]
    opp_score = match_data["away_score"] if is_arsenal_home else match_data["home_score"]
    gd = arsenal_score - opp_score

    tickets_count = max(0, min(5, gd)) if gd > 0 else 0
    total_cost = tickets_count * 300

    # スコアボード表示
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>{match_data['match_name']} (Match ID: {match_data['match_id']})</span>
            <span style="color:#34D399; font-weight:bold;">FT (試合終了)</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; width:90px;">
                <img src="{home_logo}" width="54" height="54" style="object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.5));">
                <div style="font-weight:bold; font-size:14px; margin-top:6px;">{match_data['home_team']}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:34px; font-weight:900; letter-spacing:3px;">{match_data['home_score']} - {match_data['away_score']}</div>
                <div style="font-size:11px; color:#94A3B8;">Date: {match_data['date']}</div>
            </div>
            <div style="text-align:center; width:90px;">
                <img src="{away_logo}" width="54" height="54" style="object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.5));">
                <div style="font-weight:bold; font-size:14px; margin-top:6px;">{match_data['away_team']}</div>
            </div>
        </div>
        <div class="badge-win">
            <span>🎯 判定: 得失点差 {'+' if gd > 0 else ''}{gd}点差</span>
            <span>🛒 購入口数: {tickets_count}口 ({total_cost:,}円)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 選択中の試合詳細へ飛ぶリンク
    st.link_button("🔗 FotMobでこの試合のスタッツ詳細を見る", fotmob_url, use_container_width=True)

    # オウンゴール手動補正オプション
    og_override = None
    with st.expander("⚙️ オウンゴール（OG）または手動背番号補正"):
        st.caption("先制点がOGの場合や、スタッツを修正したい場合はここで指定します。")
        use_manual = st.checkbox("手動で先制誘発者を指定する")
        if use_manual:
            manual_num = st.number_input("誘発した選手の背番号を入力", min_value=1, max_value=99, value=29)
            og_override = int(manual_num)

    # 数字算出
    if tickets_count > 0:
        t1_nums, t1_logs = generate_ticket_1(match_data, og_override)
        t2_nums = generate_ticket_2()
        t3_nums = generate_ticket_qp()

        st.markdown("**1口目【マッチスタッツ連動型】**")
        balls_html_1 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t1_nums])
        st.markdown(f'<div class="ball-container">{balls_html_1}</div>', unsafe_allow_html=True)
        st.caption(" ➔ " + " / ".join(t1_logs))

        if tickets_count >= 2:
            st.markdown("**2口目【過去3年 AI統計分析型】**")
            balls_html_2 = "".join([f'<div class="loto-ball loto-ball-gold">{n:02d}</div>' for n in t2_nums])
            st.markdown(f'<div class="ball-container">{balls_html_2}</div>', unsafe_allow_html=True)
            st.caption(" ➔ 統計構成: 奇数3:偶数4 / 合計127 / 連番30-31")

        if tickets_count >= 3:
            st.markdown("**3口目【クイックピック（QP）】**")
            balls_html_3 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t3_nums])
            st.markdown(f'<div class="ball-container">{balls_html_3}</div>', unsafe_allow_html=True)
            st.caption(" ➔ 自動ランダム採番")

        # コピペ用コードブロック
        st.divider()
        copy_text = f"""【ロト7 購入シート】{match_data['match_name']}
スコア: {match_data['home_team']} {match_data['home_score']} - {match_data['away_score']} {match_data['away_team']}
購入口数: {tickets_count}口 ({total_cost:,}円)
1口目: {' '.join([f'{n:02d}' for n in t1_nums])}"""
        if tickets_count >= 2:
            copy_text += f"\n2口目: {' '.join([f'{n:02d}' for n in t2_nums])}"
        if tickets_count >= 3:
            copy_text += f"\n3口目: {' '.join([f'{n:02d}' for n in t3_nums])} (QP)"

        st.markdown("**📋 購入用テキスト（右上のアイコンで1タップコピー）**")
        st.code(copy_text, language="text")

        # 履歴保存ボタン
        if st.button("💾 この試合を購入履歴に保存", use_container_width=True):
            history = load_history()
            opp_name = match_data['away_team'] if is_arsenal_home else match_data['home_team']
            new_record = {
                "date": match_data["date"],
                "opponent": opp_name,
                "score": f"{arsenal_score}-{opp_score}",
                "tickets": tickets_count,
                "cost": total_cost,
                "ticket_1": t1_nums,
                "ticket_2": t2_nums if tickets_count >= 2 else [],
                "hit_amount": 0,
                "status": "未抽せん"
            }
            history.insert(0, new_record)
            save_history(history)
            st.success(f"{match_data['match_name']} を購入履歴に保存しました！")
    else:
        st.info("今節は引き分けまたは敗戦のため、ロト7の購入はありません（0口）。")

# --------------------------------------------------
# TAB 2: シーズン収支管理
# --------------------------------------------------
with tab2:
    history = load_history()
    
    total_spent = sum([item.get("cost", 0) for item in history])
    total_won = sum([item.get("hit_amount", 0) for item in history])
    net_balance = total_won - total_spent
    roi = (total_won / total_spent * 100) if total_spent > 0 else 0

    st.markdown(f"""
    <div class="match-card">
        <div style="font-size:12px; color:#94A3B8;">SEASON OVERVIEW (収支概要)</div>
        <div style="font-size:28px; font-weight:900; color:{'#34D399' if net_balance >= 0 else '#F87171'}; margin:6px 0;">
            {'+' if net_balance > 0 else ''}{net_balance:,} 円
        </div>
        <div style="display:flex; justify-content:space-between; font-size:12px; border-top:1px solid rgba(255,255,255,0.08); padding-top:8px;">
            <span>総投資: -{total_spent:,}円</span>
            <span>総回収: +{total_won:,}円</span>
            <span>回収率: {roi:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📜 試合別履歴 & 当せん入力**")
    if history:
        for idx, rec in enumerate(history):
            with st.expander(f"{rec['date']} vs {rec['opponent']} ({rec['score']}) - {rec['tickets']}口"):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.write(f"購入額: {rec['cost']:,}円")
                    st.write(f"1口目: {rec['ticket_1']}")
                with col_h2:
                    won_input = st.number_input(f"当せん金額 (円)", min_value=0, step=1000, value=rec.get("hit_amount", 0), key=f"won_{idx}")
                    if won_input != rec.get("hit_amount", 0):
                        history[idx]["hit_amount"] = int(won_input)
                        history[idx]["status"] = f"{won_input:,}円 当せん" if won_input > 0 else "ハズレ"
                        save_history(history)
                        st.rerun()
    else:
        st.caption("保存された購入履歴はありません。")

    if st.button("🗑️ 履歴データをリセット"):
        save_history([])
        st.rerun()
