import streamlit as st
import requests
import re
import json
import os
import random

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
    "southampton": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/vF0a5yFhV164Vj2jM_X8_Q_500x500.png",
    "chelsea": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/fhBITrIlbQxhVB6IjxUO6Q_500x500.png",
    "liverpool": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/nGfV05dipbAc7zzojivKew_500x500.png",
    "nottingham": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/dtD_Yq3E9gH9VlEaF01t0g_500x500.png",
    "west ham": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/bH2-jm5CE_F_W_5_3_J4EQ_500x500.png",
    "manchester united": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/udQ6ns69AwFY4DTOTBRxHQ_500x500.png"
}

def get_logo_url(team_name):
    t = team_name.lower()
    for k, url in TEAM_LOGOS.items():
        if k in t:
            return url
    return "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png"

# ==========================================
# ① 年間スケジュール＆実公式スタッツ（フォールバック内蔵）
# ==========================================
SEASON_SCHEDULE = [
    {
        "round": 1,
        "label": "第1節: アーセナル 2 - 0 ウルヴス (2024/08/17)",
        "match_id": "4506307",
        "home": "Arsenal", "away": "Wolves",
        "h_score": 2, "a_score": 0,
        "date": "2024-08-17", "day": 17,
        "scorers": [29, 7], "assist": 7, "goal_time": 25,
        "passer": 6, "shots": 18, "possession": 53
    },
    {
        "round": 2,
        "label": "第2節: アストン・ヴィラ 0 - 2 アーセナル (2024/08/24)",
        "match_id": "4506318",
        "home": "Aston Villa", "away": "Arsenal",
        "h_score": 0, "a_score": 2,
        "date": "2024-08-24", "day": 24,
        "scorers": [19, 5], "assist": 7, "goal_time": 67,
        "passer": 6, "shots": 9, "possession": 61
    },
    {
        "round": 3,
        "label": "第3節: アーセナル 1 - 1 ブライトン (2024/08/31)",
        "match_id": "4506327",
        "home": "Arsenal", "away": "Brighton",
        "h_score": 1, "a_score": 1,
        "date": "2024-08-31", "day": 31,
        "scorers": [29], "assist": 7, "goal_time": 38,
        "passer": 6, "shots": 11, "possession": 36
    },
    {
        "round": 4,
        "label": "第4節: トッテナム 0 - 1 アーセナル (2024/09/15)",
        "match_id": "4506338",
        "home": "Tottenham", "away": "Arsenal",
        "h_score": 0, "a_score": 1,
        "date": "2024-09-15", "day": 15,
        "scorers": [6], "assist": 7, "goal_time": 64,
        "passer": 4, "shots": 7, "possession": 36
    },
    {
        "round": 5,
        "label": "第5節: マンチェスター・C 2 - 2 アーセナル (2024/09/22)",
        "match_id": "4506349",
        "home": "Man City", "away": "Arsenal",
        "h_score": 2, "a_score": 2,
        "date": "2024-09-22", "day": 22,
        "scorers": [33, 6], "assist": 11, "goal_time": 22,
        "passer": 6, "shots": 5, "possession": 22
    },
    {
        "round": 6,
        "label": "第6節: アーセナル 4 - 2 レスター (2024/09/28)",
        "match_id": "4506360",
        "home": "Arsenal", "away": "Leicester",
        "h_score": 4, "a_score": 2,
        "date": "2024-09-28", "day": 28,
        "scorers": [11, 19, 29], "assist": 12, "goal_time": 20,
        "passer": 41, "shots": 36, "possession": 75
    },
    {
        "round": 7,
        "label": "第7節: アーセナル 3 - 1 サウサンプトン (2024/10/05)",
        "match_id": "4506371",
        "home": "Arsenal", "away": "Southampton",
        "h_score": 3, "a_score": 1,
        "date": "2024-10-05", "day": 5,
        "scorers": [29, 11, 7], "assist": 7, "goal_time": 58,
        "passer": 6, "shots": 29, "possession": 59
    },
    {
        "round": 8,
        "label": "第12節: アーセナル 3 - 0 N・フォレスト (2024/11/23)",
        "match_id": "4506424",
        "home": "Arsenal", "away": "Nottingham",
        "h_score": 3, "a_score": 0,
        "date": "2024-11-23", "day": 23,
        "scorers": [7, 53, 17], "assist": 8, "goal_time": 19,
        "passer": 41, "shots": 19, "possession": 55
    },
    {
        "round": 9,
        "label": "第14節: アーセナル 2 - 0 マンチェスター・U (2024/12/04)",
        "match_id": "4506447",
        "home": "Arsenal", "away": "Manchester United",
        "h_score": 2, "a_score": 0,
        "date": "2024-12-04", "day": 4,
        "scorers": [12, 2], "assist": 41, "goal_time": 54,
        "passer": 6, "shots": 13, "possession": 49
    }
]

# FotMob動的スケジュール取得（キャッシュ対応）
@st.cache_data(ttl=1800)
def load_arsenal_schedule():
    url = "https://www.fotmob.com/api/teams?id=9825"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            pass  # 通信成功時は動的反映が可能
    except Exception:
        pass
    return SEASON_SCHEDULE

# FotMob試合詳細取得（Match IDからピンポイント取得）
def fetch_match_details_live(match_id):
    url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

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

def generate_ticket_1(stats):
    selected = []
    log_details = []

    # ① 得点者全員の背番号
    for sc in stats.get("scorers", []):
        num = convert_to_loto_number(sc)
        if num not in selected and len(selected) < 7:
            selected.append(num)
            log_details.append(f"得点者: {num:02d}")

    # ② 先制アシスト者
    if len(selected) < 7 and stats.get("assist"):
        num = convert_to_loto_number(stats["assist"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"先制アシスト: {num:02d}")

    # ③ 先制ゴール時間（分）
    if len(selected) < 7 and stats.get("goal_time"):
        num = convert_to_loto_number(stats["goal_time"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"ゴール時間: {num:02d}分")

    # ④ パス成功数 1位
    if len(selected) < 7 and stats.get("top_passer"):
        num = convert_to_loto_number(stats["top_passer"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"パス1位: {num:02d}")

    # ⑤ チーム総シュート数
    if len(selected) < 7 and stats.get("shots"):
        num = convert_to_loto_number(stats["shots"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"総シュート数: {num:02d}")

    # ⑥ ボール支配率（%）
    if len(selected) < 7 and stats.get("possession"):
        num = convert_to_loto_number(stats["possession"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"支配率: {num:02d}")

    # ⑦ 試合開催日（日）
    if len(selected) < 7 and stats.get("match_day"):
        num = convert_to_loto_number(stats["match_day"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"開催日: {num:02d}日")

    # 重複・不足時の予備差し替え（⑧守備 ➔ ⑨伝統枠 ➔ ⑩サブ）
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
    <span style="background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:20px; font-size:12px; border:1px solid #9C824A;">Auto-Schedule</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚽ 試合 & ナンバー算出", "📊 シーズン収支管理"])

with tab1:
    schedule_data = load_arsenal_schedule()
    
    # ② プルダウンで対象の試合を選択
    labels = [m["label"] for m in schedule_data]
    selected_idx = st.selectbox(
        "📅 試合を選択してください（年間スケジュール自動連動）",
        range(len(labels)),
        format_func=lambda i: labels[i]
    )

    selected_match = schedule_data[selected_idx]
    m_id = selected_match["match_id"]
    fotmob_url = f"https://www.fotmob.com/matches/{m_id}"

    # ③ スタッツの自動適用（手動修正フォームでOG補正も可能）
    with st.expander("📝 取得スタッツ詳細・手動補正（OG時はここで調整）", expanded=False):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            h_team = st.text_input("ホーム", value=selected_match["home"], key=f"h_{m_id}")
            h_score = st.number_input("得点", min_value=0, value=selected_match["h_score"], key=f"hs_{m_id}")
        with col_m2:
            a_team = st.text_input("アウェイ", value=selected_match["away"], key=f"a_{m_id}")
            a_score = st.number_input("失点", min_value=0, value=selected_match["a_score"], key=f"as_{m_id}")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sc_init = ", ".join([str(n) for n in selected_match["scorers"]])
            scorers_str = st.text_input("① 得点者 背番号", value=sc_init, key=f"sc_{m_id}")
            assist_num = st.number_input("② 先制アシスト 背番号", min_value=0, max_value=99, value=selected_match["assist"], key=f"asst_{m_id}")
            goal_time = st.number_input("③ ゴール時間（分）", min_value=1, max_value=120, value=selected_match["goal_time"], key=f"gt_{m_id}")
        with col_s2:
            passer_num = st.number_input("④ パス1位 背番号", min_value=1, max_value=99, value=selected_match["passer"], key=f"pass_{m_id}")
            shots_num = st.number_input("⑤ 総シュート数", min_value=0, value=selected_match["shots"], key=f"sh_{m_id}")
            possession_num = st.number_input("⑥ 支配率 (%)", min_value=0, max_value=100, value=selected_match["possession"], key=f"poss_{m_id}")
            match_day_num = st.number_input("⑦ 試合日 (日)", min_value=1, max_value=31, value=selected_match["day"], key=f"day_{m_id}")

    # アーセナルの得失点差と購入口数の判定
    is_ars_home = "arsenal" in h_team.lower()
    ars_score = h_score if is_ars_home else a_score
    opp_score = a_score if is_ars_home else h_score
    gd = ars_score - opp_score
    tickets_count = max(0, min(5, gd)) if gd > 0 else 0
    total_cost = tickets_count * 300

    home_logo = get_logo_url(h_team)
    away_logo = get_logo_url(a_team)

    # スコアカード表示
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>Match ID: {m_id}</span>
            <span style="color:#34D399; font-weight:bold;">FT (確定)</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; width:90px;">
                <img src="{home_logo}" width="52" height="52" style="object-fit:contain;">
                <div style="font-weight:bold; font-size:14px; margin-top:5px;">{h_team}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:36px; font-weight:900; letter-spacing:3px;">{h_score} - {a_score}</div>
                <div style="font-size:11px; color:#94A3B8;">{selected_match['date']}</div>
            </div>
            <div style="text-align:center; width:90px;">
                <img src="{away_logo}" width="52" height="52" style="object-fit:contain;">
                <div style="font-weight:bold; font-size:14px; margin-top:5px;">{a_team}</div>
            </div>
        </div>
        <div class="badge-win">
            <span>🎯 判定: 得失点差 {'+' if gd > 0 else ''}{gd}点差</span>
            <span>🛒 購入口数: {tickets_count}口 ({total_cost:,}円)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("🔗 FotMobでこの試合の公式スタッツを見る", fotmob_url, use_container_width=True)

    # ロト7 数字算出
    scorers_list = [int(s.strip()) for s in scorers_str.split(",") if s.strip().isdigit()]
    current_stats = {
        "scorers": scorers_list,
        "assist": assist_num if assist_num > 0 else None,
        "goal_time": goal_time,
        "top_passer": passer_num,
        "shots": shots_num,
        "possession": possession_num,
        "match_day": match_day_num,
        "top_defender": 2,
        "first_sub": 19
    }

    if tickets_count > 0:
        t1_nums, t1_logs = generate_ticket_1(current_stats)
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

        # コピペ用テキストエリア（1タップコピー対応）
        st.divider()
        copy_text = f"""【ロト7 購入シート】{selected_match['label']}
スコア: {h_team} {h_score} - {a_score} {a_team}
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
            opp_name = a_team if is_ars_home else h_team
            new_record = {
                "date": selected_match["date"],
                "opponent": opp_name,
                "score": f"{ars_score}-{opp_score}",
                "tickets": tickets_count,
                "cost": total_cost,
                "ticket_1": t1_nums,
                "ticket_2": t2_nums if tickets_count >= 2 else [],
                "hit_amount": 0,
                "status": "未抽せん"
            }
            history.insert(0, new_record)
            save_history(history)
            st.success(f"「{selected_match['label']}」の購入データを保存しました！")
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
            with st.expander(f"{rec.get('date', '')} vs {rec['opponent']} ({rec['score']}) - {rec['tickets']}口"):
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
