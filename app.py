import streamlit as st
import requests
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
# 永続データ管理（収支用）
# ==========================================
HISTORY_FILE = "match_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# 2026-27シーズン 全38節公式日程マスター（確定データ削除済・未確定状態）
# ==========================================
SCHEDULE_2026_27 = [
    {"round": 1, "opp": "コヴェントリー・シティ", "en_opp": "coventry", "ha": "H", "status": "UPCOMING", "day": 22},
    {"round": 2, "opp": "アストン・ヴィラ", "en_opp": "villa", "ha": "A", "status": "UPCOMING", "day": 1},
    {"round": 3, "opp": "チェルシー", "en_opp": "chelsea", "ha": "H", "status": "UPCOMING", "day": 7},
    {"round": 4, "opp": "サンダーランド", "en_opp": "sunderland", "ha": "A", "status": "UPCOMING", "day": 13},
    {"round": 5, "opp": "ブライトン", "en_opp": "brighton", "ha": "A", "status": "UPCOMING", "day": 19},
    {"round": 6, "opp": "リーズ・ユナイテッド", "en_opp": "leeds", "ha": "H", "status": "UPCOMING", "day": 10},
    {"round": 7, "opp": "ノッティンガム・フォレスト", "en_opp": "forest", "ha": "A", "status": "UPCOMING", "day": 19},
    {"round": 8, "opp": "エヴァートン", "en_opp": "everton", "ha": "H", "status": "UPCOMING", "day": 24},
    {"round": 9, "opp": "リヴァプール", "en_opp": "liverpool", "ha": "A", "status": "UPCOMING", "day": 2},
    {"round": 10, "opp": "ハル・シティ", "en_opp": "hull", "ha": "H", "status": "UPCOMING", "day": 8},
    {"round": 11, "opp": "ニューカッスル・ユナイテッド", "en_opp": "newcastle", "ha": "A", "status": "UPCOMING", "day": 22},
    {"round": 12, "opp": "マンチェスター・シティ", "en_opp": "man city", "ha": "H", "status": "UPCOMING", "day": 29},
    {"round": 13, "opp": "ブレントフォード", "en_opp": "brentford", "ha": "A", "status": "UPCOMING", "day": 5},
    {"round": 14, "opp": "トッテナム・ホットスパー", "en_opp": "tottenham", "ha": "A", "status": "UPCOMING", "day": 12},
    {"round": 15, "opp": "ボーンマス", "en_opp": "bournemouth", "ha": "H", "status": "UPCOMING", "day": 19},
    {"round": 16, "opp": "マンチェスター・ユナイテッド", "en_opp": "manchester united", "ha": "H", "status": "UPCOMING", "day": 26},
    {"round": 17, "opp": "クリスタル・パレス", "en_opp": "crystal palace", "ha": "A", "status": "UPCOMING", "day": 29},
    {"round": 18, "opp": "フラム", "en_opp": "fulham", "ha": "A", "status": "UPCOMING", "day": 2},
    {"round": 19, "opp": "イプスウィッチ・タウン", "en_opp": "ipswich", "ha": "H", "status": "UPCOMING", "day": 16},
    {"round": 20, "opp": "ブレントフォード", "en_opp": "brentford", "ha": "H", "status": "UPCOMING", "day": 23},
    {"round": 21, "opp": "ハル・シティ", "en_opp": "hull", "ha": "A", "status": "UPCOMING", "day": 30},
    {"round": 22, "opp": "ニューカッスル・ユナイテッド", "en_opp": "newcastle", "ha": "H", "status": "UPCOMING", "day": 6},
    {"round": 23, "opp": "マンチェスター・シティ", "en_opp": "man city", "ha": "A", "status": "UPCOMING", "day": 13},
    {"round": 24, "opp": "リヴァプール", "en_opp": "liverpool", "ha": "H", "status": "UPCOMING", "day": 20},
    {"round": 25, "opp": "イプスウィッチ・タウン", "en_opp": "ipswich", "ha": "A", "status": "UPCOMING", "day": 27},
    {"round": 26, "opp": "フラム", "en_opp": "fulham", "ha": "H", "status": "UPCOMING", "day": 6},
    {"round": 27, "opp": "マンチェスター・ユナイテッド", "en_opp": "manchester united", "ha": "A", "status": "UPCOMING", "day": 13},
    {"round": 28, "opp": "クリスタル・パレス", "en_opp": "crystal palace", "ha": "H", "status": "UPCOMING", "day": 3},
    {"round": 29, "opp": "チェルシー", "en_opp": "chelsea", "ha": "A", "status": "UPCOMING", "day": 10},
    {"round": 30, "opp": "サンダーランド", "en_opp": "sunderland", "ha": "H", "status": "UPCOMING", "day": 17},
    {"round": 31, "opp": "コヴェントリー・シティ", "en_opp": "coventry", "ha": "A", "status": "UPCOMING", "day": 24},
    {"round": 32, "opp": "アストン・ヴィラ", "en_opp": "villa", "ha": "H", "status": "UPCOMING", "day": 1},
    {"round": 33, "opp": "ボーンマス", "en_opp": "bournemouth", "ha": "A", "status": "UPCOMING", "day": 8},
    {"round": 34, "opp": "トッテナム・ホットスパー", "en_opp": "tottenham", "ha": "H", "status": "UPCOMING", "day": 15},
    {"round": 35, "opp": "リーズ・ユナイテッド", "en_opp": "leeds", "ha": "A", "status": "UPCOMING", "day": 19},
    {"round": 36, "opp": "ノッティンガム・フォレスト", "en_opp": "forest", "ha": "H", "status": "UPCOMING", "day": 23},
    {"round": 37, "opp": "エヴァートン", "en_opp": "everton", "ha": "A", "status": "UPCOMING", "day": 26},
    {"round": 38, "opp": "ブライトン", "en_opp": "brighton", "ha": "H", "status": "UPCOMING", "day": 30}
]

ARSENAL_SQUAD_NUMBERS = {
    "saka": 7, "odegaard": 8, "havertz": 29, "martinelli": 11,
    "gabriel": 6, "saliba": 2, "rice": 41, "calafiori": 33,
    "timber": 12, "trossard": 19, "jesus": 9, "white": 4,
    "sterling": 30, "merino": 23, "nwaneri": 53, "lewis-skelly": 49,
    "partey": 5, "zinchenko": 17, "jorginho": 20, "raya": 22
}

# ==========================================
# バックグラウンド自動スタッツ同期（FotMob）
# ==========================================
@st.cache_data(ttl=180)
def sync_fotmob_match_silently(en_opp, is_home):
    """裏側でFotMobから該当試合を検索してスタッツを取得"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.fotmob.com/"
    }
    try:
        res = requests.get("https://www.fotmob.com/api/team?id=9825", headers=headers, timeout=5)
        if res.status_code != 200:
            return None

        data = res.json()
        raw_fixtures = []
        if "fixtures" in data:
            f_sec = data["fixtures"]
            if isinstance(f_sec, dict):
                raw_fixtures = f_sec.get("allFixtures", {}).get("fixtures", []) or f_sec.get("fixtures", [])
            elif isinstance(f_sec, list):
                raw_fixtures = f_sec
        if not raw_fixtures and "overview" in data:
            raw_fixtures = data["overview"].get("fixtures", [])

        matched_id = None
        for item in raw_fixtures:
            h_n = item.get("home", {}).get("name", "").lower()
            a_n = item.get("away", {}).get("name", "").lower()
            target_side = a_n if is_home else h_n
            if en_opp in target_side:
                matched_id = str(item.get("id", ""))
                break

        if not matched_id:
            return None

        m_res = requests.get(f"https://www.fotmob.com/api/matchDetails?matchId={matched_id}", headers=headers, timeout=5)
        if m_res.status_code != 200:
            return None

        m_data = m_res.json()
        header = m_data.get("header", {})
        teams = header.get("teams", [])
        if len(teams) < 2:
            return None

        h_sc = teams[0].get("score")
        a_sc = teams[1].get("score")
        is_finished = header.get("status", {}).get("finished", False)

        player_number_map = {}
        lineup = m_data.get("content", {}).get("lineup", {})
        for side in ["homeTeam", "awayTeam"]:
            team_lineup = lineup.get(side, {})
            for p in team_lineup.get("starters", []) + team_lineup.get("subs", []):
                pid = str(p.get("id", ""))
                shirt = p.get("shirt") or p.get("shirtNumber")
                if pid and shirt:
                    player_number_map[pid] = int(shirt)

        events = m_data.get("content", {}).get("matchFacts", {}).get("events", {}).get("events", [])
        scorers = []
        first_assist = None
        first_time = None

        for ev in events:
            if ev.get("type") in ["Goal", "goal"]:
                ev_is_home = ev.get("isHome", True)
                if (is_home and ev_is_home) or (not is_home and not ev_is_home):
                    pid = str(ev.get("playerId") or ev.get("player", {}).get("id", ""))
                    pname = ev.get("player", {}).get("name", "").lower()
                    num = player_number_map.get(pid)
                    if not num:
                        for k, v in ARSENAL_SQUAD_NUMBERS.items():
                            if k in pname:
                                num = v
                                break
                    if not num:
                        num = 7
                    scorers.append(num)

                    if first_time is None:
                        first_time = int(ev.get("time", 20))
                        aid = str(ev.get("assistPlayerId") or ev.get("assist", {}).get("id", ""))
                        aname = ev.get("assist", {}).get("name", "").lower()
                        if aid and aid in player_number_map:
                            first_assist = player_number_map[aid]
                        else:
                            for k, v in ARSENAL_SQUAD_NUMBERS.items():
                                if k in aname:
                                    first_assist = v
                                    break

        shots = 15
        possession = 55
        stats_periods = m_data.get("content", {}).get("stats", {}).get("Periods", {}).get("All", {}).get("stats", [])
        ars_idx = 0 if is_home else 1

        for sec in stats_periods:
            for item in sec.get("stats", []):
                title = item.get("title", "").lower()
                vals = item.get("stats", [])
                if len(vals) >= 2:
                    if "possession" in title:
                        p_str = str(vals[ars_idx]).replace("%", "").strip()
                        if p_str.isdigit():
                            possession = int(p_str)
                    elif "shots" in title and "total" in title:
                        s_str = str(vals[ars_idx]).strip()
                        if s_str.isdigit():
                            shots = int(s_str)

        return {
            "match_id": matched_id,
            "h_score": int(h_sc) if h_sc is not None else 0,
            "a_score": int(a_sc) if a_sc is not None else 0,
            "is_finished": is_finished,
            "scorers": scorers if scorers else [7],
            "assist": first_assist or 8,
            "goal_time": first_time or 20,
            "shots": shots,
            "possession": possession
        }
    except Exception:
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

    if len(selected) < 7 and stats.get("poss"):
        num = convert_to_loto_number(stats["poss"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"支配率: {num:02d}")

    if len(selected) < 7 and stats.get("day"):
        num = convert_to_loto_number(stats["day"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"開催日: {num:02d}日")

    fallback_pool = [2, 14, 13, 18, 1, 19]
    fb_idx = 0
    while len(selected) < 7 and fb_idx < len(fallback_pool):
        cand = convert_to_loto_number(fallback_pool[fb_idx])
        if cand not in selected:
            selected.append(cand)
            log_details.append(f"予備枠: {cand:02d}")
        fb_idx += 1

    return sorted(selected), log_details

def generate_ticket_2():
    while True:
        nums = sorted(random.sample(range(1, 38), 7))
        odds = sum(1 for n in nums if n % 2 != 0)
        total = sum(nums)
        zones = set((n - 1) // 10 for n in nums)
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
    labels = []
    for item in SCHEDULE_2026_27:
        r = item["round"]
        opp = item["opp"]
        ha = item["ha"]
        txt = f"アーセナル vs {opp}" if ha == "H" else f"{opp} vs アーセナル"
        labels.append(f"第{r}節: {txt} ({ha})")

    selected_idx = st.selectbox(
        "📅 試合を選択してください（第1節〜第38節）",
        range(len(labels)),
        format_func=lambda i: labels[i]
    )

    m = SCHEDULE_2026_27[selected_idx]
    round_num = m["round"]
    opp_name = m["opp"]
    en_opp = m.get("en_opp", "")
    ha = m["ha"]
    is_home = (ha == "H")

    state_key = f"match_data_{round_num}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "match_id": "",
            "h_score": 0,
            "a_score": 0,
            "is_finished": False,
            "scorers": [7],
            "assist": 8,
            "goal_time": 20,
            "passer": 6,
            "shots": 15,
            "poss": 55,
            "day": m.get("day", 1),
            "auto_synced": False
        }

    cur = st.session_state[state_key]

    # 裏側で自動同期（未同期かつ未確定の場合にFotMob検索）
    if not cur["auto_synced"] and not cur["is_finished"] and en_opp:
        fetched = sync_fotmob_match_silently(en_opp, is_home)
        if fetched and fetched.get("is_finished"):
            cur["match_id"] = fetched["match_id"]
            cur["h_score"] = fetched["h_score"]
            cur["a_score"] = fetched["a_score"]
            cur["is_finished"] = True
            cur["scorers"] = fetched["scorers"]
            cur["assist"] = fetched["assist"]
            cur["goal_time"] = fetched["goal_time"]
            cur["shots"] = fetched["shots"]
            cur["poss"] = fetched["possession"]
            cur["auto_synced"] = True

    h_team = "アーセナルFC" if is_home else opp_name
    a_team = opp_name if is_home else "アーセナルFC"

    # 手動補正・OG対応アコーディオン
    with st.expander("📝 スコア & スタッツ詳細（手動調整・OG補正）", expanded=False):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            cur["h_score"] = st.number_input(f"{h_team} 得点", min_value=0, value=int(cur["h_score"]), key=f"hs_{round_num}")
        with col_m2:
            cur["a_score"] = st.number_input(f"{a_team} 得点", min_value=0, value=int(cur["a_score"]), key=f"as_{round_num}")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sc_str = ", ".join([str(n) for n in cur["scorers"]])
            scorers_input = st.text_input("得点者 背番号（カンマ区切り）", value=sc_str, key=f"sc_{round_num}")
            cur["scorers"] = [int(s.strip()) for s in scorers_input.split(",") if s.strip().isdigit()]
            cur["assist"] = st.number_input("先制アシスト 背番号", min_value=0, max_value=99, value=int(cur["assist"]), key=f"asst_{round_num}")
            cur["goal_time"] = st.number_input("先制ゴール時間（分）", min_value=1, max_value=120, value=int(cur["goal_time"]), key=f"gt_{round_num}")
        with col_s2:
            cur["passer"] = st.number_input("パス1位 背番号", min_value=1, max_value=99, value=int(cur["passer"]), key=f"pass_{round_num}")
            cur["shots"] = st.number_input("チーム総シュート数", min_value=0, value=int(cur["shots"]), key=f"sh_{round_num}")
            cur["poss"] = st.number_input("ボール支配率 (%)", min_value=0, max_value=100, value=int(cur["poss"]), key=f"poss_{round_num}")
            cur["day"] = st.number_input("試合開催日（日）", min_value=1, max_value=31, value=int(cur["day"]), key=f"day_{round_num}")

    ars_score = cur["h_score"] if is_home else cur["a_score"]
    opp_score = cur["a_score"] if is_home else cur["h_score"]
    gd = ars_score - opp_score

    has_result = cur["is_finished"] or (cur["h_score"] > 0 or cur["a_score"] > 0)
    tickets = max(0, min(5, gd)) if (has_result and gd > 0) else 0
    cost = tickets * 300

    # スコアカード
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>第{round_num}節 / 38節</span>
            <span style="color:{'#34D399' if cur['is_finished'] else '#F59E0B'}; font-weight:bold;">
                {'FT (試合終了)' if cur['is_finished'] else 'キックオフ前'}
            </span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; width:120px; font-weight:bold; font-size:15px;">{h_team}</div>
            <div style="text-align:center;">
                <div style="font-size:36px; font-weight:900; letter-spacing:3px;">
                    {f"{cur['h_score']} - {cur['a_score']}" if has_result else "VS"}
                </div>
                <div style="font-size:11px; color:#94A3B8;">{'HOME' if is_home else 'AWAY'}</div>
            </div>
            <div style="text-align:center; width:120px; font-weight:bold; font-size:15px;">{a_team}</div>
        </div>
        <div class="badge-win">
            <span>🎯 得失点差: {'+' if gd > 0 else ''}{gd}点差</span>
            <span>🛒 購入口数: {tickets}口 ({cost:,}円)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if cur.get("match_id"):
        st.link_button("🔗 FotMobでこの試合の詳細ページを開く", f"https://www.fotmob.com/matches/{cur['match_id']}", use_container_width=True)

    t2_key = f"t2_{round_num}"
    if t2_key not in st.session_state:
        st.session_state[t2_key] = generate_ticket_2()
    t2_nums, t2_odd, t2_even, t2_total = st.session_state[t2_key]

    t3_key = f"t3_{round_num}"
    if t3_key not in st.session_state:
        st.session_state[t3_key] = generate_ticket_qp()
    t3_nums = st.session_state[t3_key]

    if tickets > 0:
        t1, logs = generate_ticket_1(cur)

        st.markdown("**1口目【マッチスタッツ連動型】**")
        b1 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t1])
        st.markdown(f'<div class="ball-container">{b1}</div>', unsafe_allow_html=True)
        st.caption(" ➔ " + " / ".join(logs))

        if tickets >= 2:
            st.markdown("**2口目【AI統計分析型（動的生成）】**")
            b2 = "".join([f'<div class="loto-ball loto-ball-gold">{n:02d}</div>' for n in t2_nums])
            st.markdown(f'<div class="ball-container">{b2}</div>', unsafe_allow_html=True)
            st.caption(f" ➔ 統計分析: 奇数{t2_odd}:偶数{t2_even} / 合計値{t2_total}")

        if tickets >= 3:
            st.markdown("**3口目【クイックピック（QP）】**")
            b3 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t3_nums])
            st.markdown(f'<div class="ball-container">{b3}</div>', unsafe_allow_html=True)

        st.divider()
        copy_text = f"""【ロト7 購入シート】第{round_num}節 vs {opp_name} ({ha})
購入口数: {tickets}口 ({cost:,}円)
1口目: {' '.join([f'{n:02d}' for n in t1])}"""
        if tickets >= 2:
            copy_text += f"\n2口目: {' '.join([f'{n:02d}' for n in t2_nums])}"
        if tickets >= 3:
            copy_text += f"\n3口目: {' '.join([f'{n:02d}' for n in t3_nums])} (QP)"

        st.markdown("**📋 購入用テキスト（右上のアイコンで1タップコピー）**")
        st.code(copy_text, language="text")

        if st.button("💾 この試合を購入履歴に保存", use_container_width=True):
            history = load_history()
            new_record = {
                "round": round_num,
                "opponent": f"{opp_name} ({ha})",
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
            st.success(f"第{round_num}節（vs {opp_name}）の購入データを保存しました！")
    else:
        if has_result:
            st.info("引き分けまたは敗戦のため、ロト7の購入はありません（0口）。")
        else:
            st.info("キックオフ前です。試合終了後に自動同期されるか、上のアコーディオンから手動入力できます。")

# ==========================================
# TAB 2: シーズン収支管理
# ==========================================
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
            with st.expander(f"第{rec.get('round', '')}節 vs {rec['opponent']} ({rec['score']}) - {rec['tickets']}口"):
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
                        key=f"won_{idx}_{rec.get('round', idx)}"
                    )
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
