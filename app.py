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
</style>
""", unsafe_allow_html=True)

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
    "man city": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/z44l-a0W1v5FmgPnemV6Xw_500x500.png"
}

def get_logo(name):
    t = name.lower()
    for k, url in TEAM_LOGOS.items():
        if k in t:
            return url
    return "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png"

# ==========================================
# ① 2026-27シーズン アーセナル公式日程マスター
# ==========================================
SEASON_2026_27_FIXTURES = [
    {
        "round": 1,
        "label": "第1節: アーセナル 3 - 0 コヴェントリー (2026/08/22 確定)",
        "status": "FT",
        "home": "アーセナルFC", "away": "コヴェントリー・シティFC",
        "h_score": 3, "a_score": 0,
        "date": "2026-08-22", "match_day": 22,
        "scorers": [29, 7, 8],     # Havertz(29), Saka(07), Odegaard(08)
        "assist": 33,              # Calafiori(33)
        "goal_time": 15,           # 15分
        "passer": 49,              # Lewis-Skelly(49 -> 12)
        "shots": 20, "possession": 64, "top_defender": 2, "first_sub": 19
    },
    {
        "round": 2,
        "label": "第2節: アストン・ヴィラ 0 - 1 アーセナル (2026/09/01 確定)",
        "status": "FT",
        "home": "アストン・ヴィラFC", "away": "アーセナルFC",
        "h_score": 0, "a_score": 1,
        "date": "2026-09-01", "match_day": 1,
        "scorers": [7],            # Saka(07) 59分
        "assist": 8,               # Odegaard(08)
        "goal_time": 59,           # 59分 (59-37 = 22)
        "passer": 6,               # Gabriel(06)
        "shots": 14, "possession": 56, "top_defender": 2, "first_sub": 10 # Eze
    },
    {
        "round": 3,
        "label": "第3節: アーセナル vs チェルシー (2026/09/07 00:30)",
        "status": "UPCOMING",
        "home": "アーセナルFC", "away": "チェルシーFC",
        "h_score": None, "a_score": None,
        "date": "2026-09-07", "match_day": 7
    },
    {
        "round": 4,
        "label": "第4節: サンダーランド vs アーセナル (2026/09/13 04:00)",
        "status": "UPCOMING",
        "home": "サンダーランドAFC", "away": "アーセナルFC",
        "h_score": None, "a_score": None,
        "date": "2026-09-13", "match_day": 13
    },
    {
        "round": 5,
        "label": "第5節: ブライトン vs アーセナル (2026/09/19 23:00)",
        "status": "UPCOMING",
        "home": "ブライトン・アンド・ホーヴ・アルビオンFC", "away": "アーセナルFC",
        "h_score": None, "a_score": None,
        "date": "2026-09-19", "match_day": 19
    },
    {
        "round": 6,
        "label": "第6節: アーセナル vs リーズ (2026/10/10 20:30)",
        "status": "UPCOMING",
        "home": "アーセナルFC", "away": "リーズ・ユナイテッドFC",
        "h_score": None, "a_score": None,
        "date": "2026-10-10", "match_day": 10
    },
    {
        "round": 7,
        "label": "第7節: N・フォレスト vs アーセナル (2026/10/19 00:30)",
        "status": "UPCOMING",
        "home": "ノッティンガム・フォレストFC", "away": "アーセナルFC",
        "h_score": None, "a_score": None,
        "date": "2026-10-19", "match_day": 19
    },
    {
        "round": 8,
        "label": "第8節: アーセナル vs エヴァートン (2026/10/24 23:00)",
        "status": "UPCOMING",
        "home": "アーセナルFC", "away": "エヴァートンFC",
        "h_score": None, "a_score": None,
        "date": "2026-10-24", "match_day": 24
    },
    {
        "round": 9,
        "label": "第9節: リヴァプール vs アーセナル (2026/11/02 01:30)",
        "status": "UPCOMING",
        "home": "リヴァプールFC", "away": "アーセナルFC",
        "h_score": None, "a_score": None,
        "date": "2026-11-02", "match_day": 2
    },
    {
        "round": 10,
        "label": "第10節: アーセナル vs ハル・シティ (2026/11/08 00:00)",
        "status": "UPCOMING",
        "home": "アーセナルFC", "away": "ハル・シティAFC",
        "h_score": None, "a_score": None,
        "date": "2026-11-08", "match_day": 8
    },
    {
        "round": 11,
        "label": "第11節: ニューカッスル vs アーセナル (2026/11/22 00:00)",
        "status": "UPCOMING",
        "home": "ニューカッスル・ユナイテッドFC", "away": "アーセナルFC",
        "h_score": None, "a_score": None,
        "date": "2026-11-22", "match_day": 22
    },
    {
        "round": 12,
        "label": "第12節: アーセナル vs マンチェスター・C (2026/11/29 00:00)",
        "status": "UPCOMING",
        "home": "アーセナルFC", "away": "マンチェスター・シティFC",
        "h_score": None, "a_score": None,
        "date": "2026-11-29", "match_day": 29
    }
]

# ==========================================
# ロト7 採番ロジック（38以上は n-37）
# ==========================================
def convert_to_loto_number(val):
    try:
        n = int(val)
        while n > 37:
            n -= 37
        return n if n > 0 else 1
    except (ValueError, TypeError):
        return 1

def generate_ticket_1(stats):
    selected = []
    log_details = []

    for sc in stats.get("scorers", []):
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

# ② プルダウン選択
fixture_labels = [m["label"] for m in SEASON_2026_27_FIXTURES]
selected_idx = st.selectbox(
    "📅 試合を選択（2026-27シーズン公式日程）",
    range(len(fixture_labels)),
    format_func=lambda i: fixture_labels[i]
)

m = SEASON_2026_27_FIXTURES[selected_idx]
home_logo = get_logo(m["home"])
away_logo = get_logo(m["away"])

# 試合カード表示
if m["status"] == "FT":
    is_ars_home = "アーセナル" in m["home"]
    ars_score = m["h_score"] if is_ars_home else m["a_score"]
    opp_score = m["a_score"] if is_ars_home else m["h_score"]
    gd = ars_score - opp_score
    tickets = max(0, min(5, gd)) if gd > 0 else 0
    cost = tickets * 300

    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>第{m['round']}節</span>
            <span style="color:#34D399; font-weight:bold;">FT (試合終了)</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; width:95px;">
                <img src="{home_logo}" width="54" height="54" style="object-fit:contain;">
                <div style="font-weight:bold; font-size:13px; margin-top:6px;">{m['home']}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:36px; font-weight:900; letter-spacing:3px;">{m['h_score']} - {m['a_score']}</div>
                <div style="font-size:11px; color:#94A3B8;">{m['date']}</div>
            </div>
            <div style="text-align:center; width:95px;">
                <img src="{away_logo}" width="54" height="54" style="object-fit:contain;">
                <div style="font-weight:bold; font-size:13px; margin-top:6px;">{m['away']}</div>
            </div>
        </div>
        <div class="badge-win">
            <span>🎯 判定: 得失点差 +{gd}点差</span>
            <span>🛒 購入口数: {tickets}口 ({cost:,}円)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ロト7 採番
    if tickets > 0:
        t1, logs = generate_ticket_1(m)
        t2 = generate_ticket_2()
        t3 = generate_ticket_qp()

        st.markdown("**1口目【マッチスタッツ連動型】**")
        b1 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t1])
        st.markdown(f'<div class="ball-container">{b1}</div>', unsafe_allow_html=True)
        st.caption(" ➔ " + " / ".join(logs))

        if tickets >= 2:
            st.markdown("**2口目【過去3年 AI統計分析型】**")
            b2 = "".join([f'<div class="loto-ball loto-ball-gold">{n:02d}</div>' for n in t2])
            st.markdown(f'<div class="ball-container">{b2}</div>', unsafe_allow_html=True)

        if tickets >= 3:
            st.markdown("**3口目【クイックピック（QP）】**")
            b3 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t3])
            st.markdown(f'<div class="ball-container">{b3}</div>', unsafe_allow_html=True)

        # コピペ用テキスト
        st.divider()
        copy_text = f"""【ロト7 購入シート】{m['label']}
購入口数: {tickets}口 ({cost:,}円)
1口目: {' '.join([f'{n:02d}' for n in t1])}"""
        if tickets >= 2:
            copy_text += f"\n2口目: {' '.join([f'{n:02d}' for n in t2])}"
        if tickets >= 3:
            copy_text += f"\n3口目: {' '.join([f'{n:02d}' for n in t3])} (QP)"

        st.markdown("**📋 購入用テキスト（右上のアイコンで1タップコピー）**")
        st.code(copy_text, language="text")
else:
    # 未開催試合の表示
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>第{m['round']}節</span>
            <span style="color:#F59E0B; font-weight:bold;">キックオフ前 (Upcoming)</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; width:95px;">
                <img src="{home_logo}" width="54" height="54" style="object-fit:contain;">
                <div style="font-weight:bold; font-size:13px; margin-top:6px;">{m['home']}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:24px; font-weight:800; color:#94A3B8;">VS</div>
                <div style="font-size:11px; color:#94A3B8;">{m['date']}</div>
            </div>
            <div style="text-align:center; width:95px;">
                <img src="{away_logo}" width="54" height="54" style="object-fit:contain;">
                <div style="font-weight:bold; font-size:13px; margin-top:6px;">{m['away']}</div>
            </div>
        </div>
        <div style="text-align:center; font-size:13px; color:#94A3B8; padding-top:8px;">
            ※ 試合終了後にスコアと詳細スタッツが確定し、ロト7番号が自動算出されます。
        </div>
    </div>
    """, unsafe_allow_html=True)
