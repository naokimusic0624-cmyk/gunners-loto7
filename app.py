import streamlit as st
import json
import os
import random

# ==========================================
# ページ基本設定 & カスタムCSS
# ==========================================
st.set_page_config(
    page_title="Gunners Loto 7 (2026-27)",
    page_icon="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
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
    .match-card {
        background-color: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
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
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #475569 !important;
        color: #F8FAFC !important;
    }
    div[data-baseweb="select"] * {
        color: #F8FAFC !important;
    }
    div[data-baseweb="input"] input {
        color: #F8FAFC !important;
        background-color: #1E293B !important;
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
# チームロゴ対応マップ
# ==========================================
TEAM_LOGOS = {
    "arsenal": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png",
    "coventry": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/KHpmY4tIwqiutl8Cfl0MAw_500x500.png",
    "aston villa": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/uyNNelfnFvCEnsLrUL-j2Q_500x500.png",
    "chelsea": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/fhBITrIlbQxhVB6IjxUO6Q_500x500.png",
    "sunderland": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/CQFeTfHrtxqgr3VKWtTwfA_500x500.png",
    "brighton": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/EKIe0e-ZIphOcfQAwsuEEQ_500x500.png",
    "leeds": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/5dqfOKpjjW6EwTAx_FysKQ_500x500.png",
    "nottingham": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/Zr6FbE-8pDH7UBpWCO8U9A_500x500.png",
    "everton": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/C3J47ea36cMBc4XPbp9aaA_500x500.png",
    "liverpool": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/nGfV05dipbAc7zzojivKew_500x500.png",
    "hull": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/riiyZbb1JHuFQgZ3831jUQ_500x500.png",
    "newcastle": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/96CcNNQ0AYDAbssP0V9LuQ_500x500.png",
    "man city": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/z44l-a0W1v5FmgPnemV6Xw_500x500.png",
    "bournemouth": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/IcW6E1iJbW8k3NdfLz89Xw_500x500.png",
    "fulham": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/b0L6C0J8fD8pXm9qE7m1aQ_500x500.png",
    "crystal palace": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/8bP7_32n1wJ3qK8zE8_xXw_500x500.png",
    "wolves": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/b92Xo_yS75bX6d8f8XqHfw_500x500.png",
    "manchester united": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/udQ6ns69AwFY4DTOTBRxHQ_500x500.png",
    "brentford": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/Q9qP5040b0ky5Fm1_8wRvg_500x500.png",
    "tottenham": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/k3Q_mKE98Dnohrcea0JFgQ_500x500.png"
}

def get_logo(name):
    t = name.lower()
    for k, url in TEAM_LOGOS.items():
        if k in t:
            return url
    return "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png"

# ==========================================
# 2026-27シーズン アーセナル公式日程マスター（全38節）
# ==========================================
SEASON_2026_27_FIXTURES = [
    {"round": 1, "label": "第1節: アーセナル 3 - 0 コヴェントリー (2026/08/22 確定)", "status": "FT", "home": "アーセナルFC", "away": "コヴェントリー・シティFC", "h_score": 3, "a_score": 0, "date": "2026-08-22", "match_day": 22, "scorers": [29, 7, 8], "assist": 33, "goal_time": 15, "passer": 49, "shots": 20, "possession": 64, "top_defender": 2, "first_sub": 19},
    {"round": 2, "label": "第2節: アストン・ヴィラ 0 - 1 アーセナル (2026/09/01 確定)", "status": "FT", "home": "アストン・ヴィラFC", "away": "アーセナルFC", "h_score": 0, "a_score": 1, "date": "2026-09-01", "match_day": 1, "scorers": [7], "assist": 8, "goal_time": 59, "passer": 6, "shots": 14, "possession": 56, "top_defender": 2, "first_sub": 10},
    {"round": 3, "label": "第3節: アーセナル vs チェルシー (2026/09/07)", "status": "UPCOMING", "home": "アーセナルFC", "away": "チェルシーFC", "h_score": None, "a_score": None, "date": "2026-09-07", "match_day": 7},
    {"round": 4, "label": "第4節: サンダーランド vs アーセナル (2026/09/13)", "status": "UPCOMING", "home": "サンダーランドAFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2026-09-13", "match_day": 13},
    {"round": 5, "label": "第5節: ブライトン vs アーセナル (2026/09/19)", "status": "UPCOMING", "home": "ブライトンFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2026-09-19", "match_day": 19},
    {"round": 6, "label": "第6節: アーセナル vs リーズ (2026/10/10)", "status": "UPCOMING", "home": "アーセナルFC", "away": "リーズ・ユナイテッドFC", "h_score": None, "a_score": None, "date": "2026-10-10", "match_day": 10},
    {"round": 7, "label": "第7節: N・フォレスト vs アーセナル (2026/10/19)", "status": "UPCOMING", "home": "ノッティンガム・フォレストFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2026-10-19", "match_day": 19},
    {"round": 8, "label": "第8節: アーセナル vs エヴァートン (2026/10/24)", "status": "UPCOMING", "home": "アーセナルFC", "away": "エヴァートンFC", "h_score": None, "a_score": None, "date": "2026-10-24", "match_day": 24},
    {"round": 9, "label": "第9節: リヴァプール vs アーセナル (2026/11/02)", "status": "UPCOMING", "home": "リヴァプールFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2026-11-02", "match_day": 2},
    {"round": 10, "label": "第10節: アーセナル vs ハル・シティ (2026/11/08)", "status": "UPCOMING", "home": "アーセナルFC", "away": "ハル・シティAFC", "h_score": None, "a_score": None, "date": "2026-11-08", "match_day": 8},
    {"round": 11, "label": "第11節: ニューカッスル vs アーセナル (2026/11/22)", "status": "UPCOMING", "home": "ニューカッスル・ユナイテッドFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2026-11-22", "match_day": 22},
    {"round": 12, "label": "第12節: アーセナル vs マンチェスター・C (2026/11/29)", "status": "UPCOMING", "home": "アーセナルFC", "away": "マンチェスター・シティFC", "h_score": None, "a_score": None, "date": "2026-11-29", "match_day": 29},
    {"round": 13, "label": "第13節: ボーンマス vs アーセナル (2026/12/05)", "status": "UPCOMING", "home": "AFCボーンマス", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2026-12-05", "match_day": 5},
    {"round": 14, "label": "第14節: アーセナル vs フラム (2026/12/12)", "status": "UPCOMING", "home": "アーセナルFC", "away": "フラムFC", "h_score": None, "a_score": None, "date": "2026-12-12", "match_day": 12},
    {"round": 15, "label": "第15節: クリスタル・パレス vs アーセナル (2026/12/19)", "status": "UPCOMING", "home": "クリスタル・パレスFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2026-12-19", "match_day": 19},
    {"round": 16, "label": "第16節: アーセナル vs ウルヴス (2026/12/26)", "status": "UPCOMING", "home": "アーセナルFC", "away": "ウルヴァーハンプトンFC", "h_score": None, "a_score": None, "date": "2026-12-26", "match_day": 26},
    {"round": 17, "label": "第17節: マンチェスター・U vs アーセナル (2026/12/29)", "status": "UPCOMING", "home": "マンチェスター・ユナイテッドFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2026-12-29", "match_day": 29},
    {"round": 18, "label": "第18節: アーセナル vs ブレントフォード (2027/01/02)", "status": "UPCOMING", "home": "アーセナルFC", "away": "ブレントフォードFC", "h_score": None, "a_score": None, "date": "2027-01-02", "match_day": 2},
    {"round": 19, "label": "第19節: トッテナム vs アーセナル (2027/01/16)", "status": "UPCOMING", "home": "トッテナムFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-01-16", "match_day": 16},
    {"round": 20, "label": "第20節: アーセナル vs アストン・ヴィラ (2027/01/23)", "status": "UPCOMING", "home": "アーセナルFC", "away": "アストン・ヴィラFC", "h_score": None, "a_score": None, "date": "2027-01-23", "match_day": 23},
    {"round": 21, "label": "第21節: コヴェントリー vs アーセナル (2027/01/30)", "status": "UPCOMING", "home": "コヴェントリー・シティFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-01-30", "match_day": 30},
    {"round": 22, "label": "第22節: アーセナル vs サンダーランド (2027/02/06)", "status": "UPCOMING", "home": "アーセナルFC", "away": "サンダーランドAFC", "h_score": None, "a_score": None, "date": "2027-02-06", "match_day": 6},
    {"round": 23, "label": "第23節: チェルシー vs アーセナル (2027/02/13)", "status": "UPCOMING", "home": "チェルシーFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-02-13", "match_day": 13},
    {"round": 24, "label": "第24節: アーセナル vs ブライトン (2027/02/20)", "status": "UPCOMING", "home": "アーセナルFC", "away": "ブライトンFC", "h_score": None, "a_score": None, "date": "2027-02-20", "match_day": 20},
    {"round": 25, "label": "第25節: リーズ vs アーセナル (2027/02/27)", "status": "UPCOMING", "home": "リーズ・ユナイテッドFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-02-27", "match_day": 27},
    {"round": 26, "label": "第26節: アーセナル vs N・フォレスト (2027/03/06)", "status": "UPCOMING", "home": "アーセナルFC", "away": "ノッティンガム・フォレストFC", "h_score": None, "a_score": None, "date": "2027-03-06", "match_day": 6},
    {"round": 27, "label": "第27節: エヴァートン vs アーセナル (2027/03/13)", "status": "UPCOMING", "home": "エヴァートンFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-03-13", "match_day": 13},
    {"round": 28, "label": "第28節: アーセナル vs リヴァプール (2027/04/03)", "status": "UPCOMING", "home": "アーセナルFC", "away": "リヴァプールFC", "h_score": None, "a_score": None, "date": "2027-04-03", "match_day": 3},
    {"round": 29, "label": "第29節: ハル・シティ vs アーセナル (2027/04/10)", "status": "UPCOMING", "home": "ハル・シティAFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-04-10", "match_day": 10},
    {"round": 30, "label": "第30節: アーセナル vs ニューカッスル (2027/04/17)", "status": "UPCOMING", "home": "アーセナルFC", "away": "ニューカッスル・ユナイテッドFC", "h_score": None, "a_score": None, "date": "2027-04-17", "match_day": 17},
    {"round": 31, "label": "第31節: マンチェスター・C vs アーセナル (2027/04/24)", "status": "UPCOMING", "home": "マンチェスター・シティFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-04-24", "match_day": 24},
    {"round": 32, "label": "第32節: アーセナル vs ボーンマス (2027/05/01)", "status": "UPCOMING", "home": "アーセナルFC", "away": "AFCボーンマス", "h_score": None, "a_score": None, "date": "2027-05-01", "match_day": 1},
    {"round": 33, "label": "第33節: フラム vs アーセナル (2027/05/08)", "status": "UPCOMING", "home": "フラムFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-05-08", "match_day": 8},
    {"round": 34, "label": "第34節: アーセナル vs クリスタル・パレス (2027/05/12)", "status": "UPCOMING", "home": "アーセナルFC", "away": "クリスタル・パレスFC", "h_score": None, "a_score": None, "date": "2027-05-12", "match_day": 12},
    {"round": 35, "label": "第35節: ウルヴス vs アーセナル (2027/05/15)", "status": "UPCOMING", "home": "ウルヴァーハンプトンFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-05-15", "match_day": 15},
    {"round": 36, "label": "第36節: アーセナル vs マンチェスター・U (2027/05/19)", "status": "UPCOMING", "home": "アーセナルFC", "away": "マンチェスター・ユナイテッドFC", "h_score": None, "a_score": None, "date": "2027-05-19", "match_day": 19},
    {"round": 37, "label": "第37節: ブレントフォード vs アーセナル (2027/05/23)", "status": "UPCOMING", "home": "ブレントフォードFC", "away": "アーセナルFC", "h_score": None, "a_score": None, "date": "2027-05-23", "match_day": 23},
    {"round": 38, "label": "第38節: アーセナル vs トッテナム (2027/05/30 最終節)", "status": "UPCOMING", "home": "アーセナルFC", "away": "トッテナムFC", "h_score": None, "a_score": None, "date": "2027-05-30", "match_day": 30}
]

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

def generate_ticket_1(stats, og_override=None):
    selected = []
    log_details = []

    scorers = stats.get("scorers", [])
    if og_override is not None:
        scorers = [og_override] + [s for s in scorers if s != og_override]

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

    if len(selected) < 7 and stats.get("passer"):
        num = convert_to_loto_number(stats["passer"])
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

    fallback_pool = [stats.get("top_defender", 2), 14, 13, 18, 1, stats.get("first_sub", 19)]
    fb_idx = 0
    while len(selected) < 7 and fb_idx < len(fallback_pool):
        cand = convert_to_loto_number(fallback_pool[fb_idx])
        if cand not in selected:
            selected.append(cand)
            log_details.append(f"予備枠: {cand:02d}")
        fb_idx += 1

    return sorted(selected), log_details

def generate_ticket_2():
    """統計的黄金バランス（奇偶比・合計値レンジ・ゾーン分散）を満たすまで動的生成"""
    while True:
        nums = sorted(random.sample(range(1, 38), 7))
        odds = sum(1 for n in nums if n % 2 != 0)
        total = sum(nums)
        
        # ゾーン分散判定（1〜9, 10〜19, 20〜29, 30〜37）
        zones = set()
        for n in nums:
            if n <= 9: zones.add(1)
            elif n <= 19: zones.add(2)
            elif n <= 29: zones.add(3)
            else: zones.add(4)
            
        # 奇偶比が3:4または4:3、合計値115〜145、3ゾーン以上に分散
        if odds in [3, 4] and 115 <= total <= 145 and len(zones) >= 3:
            return nums, odds, 7 - odds, total

def generate_ticket_qp():
    return sorted(random.sample(range(1, 38), 7))

# ==========================================
# メイン画面 UI
# ==========================================
st.markdown("""
<div class="arsenal-header">
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png" width="30" height="30" style="object-fit:contain;">
        <span style="font-size:18px; letter-spacing:0.5px;">GUNNERS LOTO 7</span>
    </div>
    <span style="background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:20px; font-size:12px; border:1px solid #9C824A;">Premier League 2026-27</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚽ 試合 & ナンバー算出", "📊 シーズン収支管理"])

with tab1:
    fixture_labels = [m["label"] for m in SEASON_2026_27_FIXTURES]
    selected_idx = st.selectbox(
        "📅 試合を選択（第1節〜最終第38節）",
        range(len(fixture_labels)),
        format_func=lambda i: fixture_labels[i]
    )

    m = SEASON_2026_27_FIXTURES[selected_idx]
    round_num = m["round"]
    home_logo = get_logo(m["home"])
    away_logo = get_logo(m["away"])
    is_finished = m["status"] == "FT"

    with st.expander("📝 試合結果・スタッツの確認＆手動入力（次節以降もここで入力可能）", expanded=not is_finished):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            h_score_in = st.number_input("ホーム得点", min_value=0, value=m["h_score"] if is_finished else 0, key=f"hs_{round_num}")
        with col_m2:
            a_score_in = st.number_input("アウェイ得点", min_value=0, value=m["a_score"] if is_finished else 0, key=f"as_{round_num}")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            default_sc = ", ".join([str(n) for n in m.get("scorers", [7])]) if is_finished else "7"
            scorers_str = st.text_input("得点者 背番号（カンマ区切り）", value=default_sc, key=f"sc_{round_num}")
            assist_in = st.number_input("先制アシスト者 背番号", min_value=0, max_value=99, value=m.get("assist", 8) if is_finished else 8, key=f"asst_{round_num}")
            goal_time_in = st.number_input("先制ゴール時間（分）", min_value=1, max_value=120, value=m.get("goal_time", 20) if is_finished else 20, key=f"gt_{round_num}")
        with col_s2:
            passer_in = st.number_input("パス1位 背番号", min_value=1, max_value=99, value=m.get("passer", 6) if is_finished else 6, key=f"pass_{round_num}")
            shots_in = st.number_input("総シュート数", min_value=0, value=m.get("shots", 15) if is_finished else 15, key=f"sh_{round_num}")
            poss_in = st.number_input("ボール支配率 (%)", min_value=0, max_value=100, value=m.get("possession", 55) if is_finished else 55, key=f"poss_{round_num}")

    is_ars_home = "アーセナル" in m["home"]
    ars_score = h_score_in if is_ars_home else a_score_in
    opp_score = a_score_in if is_ars_home else h_score_in
    gd = ars_score - opp_score

    has_score = is_finished or (h_score_in > 0 or a_score_in > 0)
    tickets = max(0, min(5, gd)) if (has_score and gd > 0) else 0
    cost = tickets * 300

    # スコアカード
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>第{round_num}節 / 38節</span>
            <span style="color:{'#34D399' if is_finished else '#F59E0B'}; font-weight:bold;">
                {'FT (試合終了)' if is_finished else 'キックオフ前 (Upcoming)'}
            </span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; width:95px;">
                <img src="{home_logo}" width="54" height="54" style="object-fit:contain;">
                <div style="font-weight:bold; font-size:13px; margin-top:6px;">{m['home']}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:36px; font-weight:900; letter-spacing:3px;">
                    {f"{h_score_in} - {a_score_in}" if has_score else "VS"}
                </div>
                <div style="font-size:11px; color:#94A3B8;">{m['date']}</div>
            </div>
            <div style="text-align:center; width:95px;">
                <img src="{away_logo}" width="54" height="54" style="object-fit:contain;">
                <div style="font-weight:bold; font-size:13px; margin-top:6px;">{m['away']}</div>
            </div>
        </div>
        <div class="badge-win">
            <span>🎯 判定: 得失点差 {'+' if gd > 0 else ''}{gd}点差</span>
            <span>🛒 購入口数: {tickets}口 ({cost:,}円)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    current_match_stats = {
        "scorers": [int(s.strip()) for s in scorers_str.split(",") if s.strip().isdigit()],
        "assist": assist_in if assist_in > 0 else None,
        "goal_time": goal_time_in,
        "passer": passer_in,
        "shots": shots_in,
        "possession": poss_in,
        "match_day": m["match_day"],
        "top_defender": 2,
        "first_sub": 19
    }

    # セッションステートで2口目・3口目を保持（画面操作による不意な変動を防止）
    t2_key = f"t2_data_{round_num}"
    if t2_key not in st.session_state:
        st.session_state[t2_key] = generate_ticket_2()

    t3_key = f"t3_data_{round_num}"
    if t3_key not in st.session_state:
        st.session_state[t3_key] = generate_ticket_qp()

    t2_nums, t2_odd, t2_even, t2_total = st.session_state[t2_key]
    t3_nums = st.session_state[t3_key]

    if tickets > 0:
        t1, logs = generate_ticket_1(current_match_stats)

        st.markdown("**1口目【マッチスタッツ連動型】**")
        b1 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t1])
        st.markdown(f'<div class="ball-container">{b1}</div>', unsafe_allow_html=True)
        st.caption(" ➔ " + " / ".join(logs))

        if tickets >= 2:
            st.markdown("**2口目【AI統計分析型（リアルタイム動的生成）】**")
            b2 = "".join([f'<div class="loto-ball loto-ball-gold">{n:02d}</div>' for n in t2_nums])
            st.markdown(f'<div class="ball-container">{b2}</div>', unsafe_allow_html=True)
            st.caption(f" ➔ 統計分析: 奇数{t2_odd}:偶数{t2_even} / 合計値{t2_total} (黄金適正レンジ・広域分散)")

        if tickets >= 3:
            st.markdown("**3口目【クイックピック（QP）】**")
            b3 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t3_nums])
            st.markdown(f'<div class="ball-container">{b3}</div>', unsafe_allow_html=True)
            st.caption(" ➔ 自動ランダム採番")

        # コピペ用テキスト
        st.divider()
        copy_text = f"""【ロト7 購入シート】{m['label']}
購入口数: {tickets}口 ({cost:,}円)
1口目: {' '.join([f'{n:02d}' for n in t1])}"""
        if tickets >= 2:
            copy_text += f"\n2口目: {' '.join([f'{n:02d}' for n in t2_nums])}"
        if tickets >= 3:
            copy_text += f"\n3口目: {' '.join([f'{n:02d}' for n in t3_nums])} (QP)"

        st.markdown("**📋 購入用テキスト（右上のアイコンで1タップコピー）**")
        st.code(copy_text, language="text")

        # 履歴保存ボタン
        if st.button("💾 この試合を購入履歴に保存", use_container_width=True):
            history = load_history()
            opp_name = m['away'] if is_ars_home else m['home']
            new_record = {
                "round": round_num,
                "date": m["date"],
                "opponent": opp_name,
                "score": f"{ars_score}-{opp_score}",
                "tickets": tickets,
                "cost": cost,
                "ticket_1": t1,
                "ticket_2": t2_nums if tickets >= 2 else [],
                "hit_amount": 0,
                "status": "未抽せん"
            }
            history.insert(0, new_record)
            save_history(history)
            st.success(f"「第{round_num}節 {opp_name}戦」の購入データを保存しました！")
    else:
        if has_score:
            st.info("引き分けまたは敗戦のため、ロト7の購入はありません（0口）。")
        else:
            st.info("キックオフ前です。試合終了後にスコアを入力するか、FotMobから最新スタッツを取り込んで採番してください。")

with tab2:
    history = load_history()
    total_spent = sum([item.get("cost", 0) for item in history])
    total_won = sum([item.get("hit_amount", 0) for item in history])
    net_balance = total_won - total_spent
    roi = (total_won / total_spent * 100) if total_spent > 0 else 0

    st.markdown(f"""
    <div class="match-card">
        <div style="font-size:12px; color:#94A3B8;">2026-27 SEASON OVERVIEW (収支概要)</div>
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

    if history:
        for idx, rec in enumerate(history):
            with st.expander(f"{rec.get('date', '')} vs {rec['opponent']} ({rec['score']}) - {rec['tickets']}口"):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.write(f"購入額: {rec['cost']:,}円")
                    st.write(f"1口目: {rec['ticket_1']}")
                    if rec.get("ticket_2"):
                        st.write(f"2口目: {rec['ticket_2']}")
                with col_h2:
                    won_input = st.number_input(
                        f"当せん金額 (円)",
                        min_value=0,
                        step=1000,
                        value=rec.get("hit_amount", 0),
                        key=f"won_{idx}_{rec['round']}"
                    )
                    if won_input != rec.get("hit_amount", 0):
                        history[idx]["hit_amount"] = int(won_input)
                        history[idx]["status"] = f"{won_input:,}円 当せん" if won_input > 0 else "ハズレ"
                        save_history(history)
                        st.rerun()
    else:
        st.caption("保存された購入履歴はありません。「試合 & ナンバー算出」タブから保存してください。")

    if st.button("🗑️ 履歴データをリセット"):
        save_history([])
        st.rerun()
