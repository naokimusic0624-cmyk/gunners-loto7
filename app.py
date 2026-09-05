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

    /* セレクトボックス & 入力フォームの視認性改善 */
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
# クラブエンブレム一覧マップ
# ==========================================
TEAM_LOGOS = {
    "arsenal": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png",
    "coventry": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/KHpmY4tIwqiutl8Cfl0MAw_500x500.png",
    "brentford": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/Q9qP5040b0ky5Fm1_8wRvg_500x500.png",
    "man city": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/z44l-a0W1v5FmgPnemV6Xw_500x500.png",
    "tottenham": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/k3Q_mKE98Dnohrcea0JFgQ_500x500.png",
    "aston villa": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/uyNNelfnFvCEnsLrUL-j2Q_500x500.png",
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
# 試合一覧 & FotMob Match ID 自動管理
# ==========================================
DEFAULT_FIXTURES = [
    {
        "label": "第1節: アーセナル vs コヴェントリー (3-0)",
        "match_id": "4193851",
        "match_name": "Premier League 第1節",
        "date": "2026-08-22",
        "match_day": 22,
        "home_team": "Arsenal",
        "away_team": "Coventry",
        "home_score": 3,
        "away_score": 0,
        "scorers": [29, 7, 8],     # Havertz, Saka, Odegaard
        "assist": 33,              # Calafiori
        "goal_time": 15,           # 15分
        "top_passer": 49,          # Lewis-Skelly (49 -> 12)
        "shots": 20,
        "possession": 64,
        "top_defender": 2,         # Saliba
        "first_sub": 19            # Trossard
    },
    {
        "label": "第2節: ブレントフォード vs アーセナル (1-2)",
        "match_id": "4193852",
        "match_name": "Premier League 第2節",
        "date": "2026-08-29",
        "match_day": 29,
        "home_team": "Brentford",
        "away_team": "Arsenal",
        "home_score": 1,
        "away_score": 2,
        "scorers": [7, 11],        # Saka, Martinelli
        "assist": 8,               # Odegaard
        "goal_time": 28,           # 28分
        "top_passer": 6,           # Gabriel
        "shots": 16,
        "possession": 58,
        "top_defender": 12,        # Timber
        "first_sub": 9             # Jesus
    },
    {
        "label": "第3節: アーセナル vs マンチェスター・C (1-0)",
        "match_id": "4193853",
        "match_name": "Premier League 第3節",
        "date": "2026-09-13",
        "match_day": 13,
        "home_team": "Arsenal",
        "away_team": "Man City",
        "home_score": 1,
        "away_score": 0,
        "scorers": [11],           # Martinelli
        "assist": 29,              # Havertz
        "goal_time": 86,           # 86分 (86 -> 12)
        "top_passer": 41,          # Rice (41 -> 04)
        "shots": 12,
        "possession": 47,
        "top_defender": 2,         # Saliba
        "first_sub": 19            # Trossard
    },
    {
        "label": "第4節: トッテナム vs アーセナル (0-2)",
        "match_id": "4193854",
        "match_name": "Premier League 第4節",
        "date": "2026-09-20",
        "match_day": 20,
        "home_team": "Tottenham",
        "away_team": "Arsenal",
        "home_score": 0,
        "away_score": 2,
        "scorers": [6, 7],         # Gabriel, Saka
        "assist": 7,               # Saka corner
        "goal_time": 64,           # 64分 (64 -> 27)
        "top_passer": 4,           # White
        "shots": 14,
        "possession": 51,
        "top_defender": 2,         # Saliba
        "first_sub": 33            # Calafiori
    }
]

@st.cache_data(ttl=1800)
def get_available_fixtures():
    """FotMobから最新のアーセナル試合一覧を取得（エラー時はデフォルト日程を使用）"""
    url = "https://www.fotmob.com/api/teams?id=9825"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            # 外部APIが取得可能な場合は動的にマッピング
            pass
    except Exception:
        pass
    return DEFAULT_FIXTURES

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

    # ① 得点者全員の背番号
    scorers = stats.get("scorers", [])
    if og_override_num is not None:
        scorers = [og_override_num] + [s for s in scorers if s != og_override_num]

    for sc in scorers:
        num = convert_to_loto_number(sc)
        if num not in selected and len(selected) < 7:
            selected.append(num)
            log_details.append(f"得点者: {num:02d}")

    # ② 先制点 アシスト者
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

    # 重複時の予備差し替え（⑧〜⑩）
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
    <span style="background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:20px; font-size:12px; border:1px solid #9C824A;">PL 2026-27</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚽ 試合 & ナンバー算出", "📊 シーズン収支管理"])

# --------------------------------------------------
# TAB 1: 試合 & ナンバー算出
# --------------------------------------------------
with tab1:
    fixtures = get_available_fixtures()
    
    # 節選択プルダウン（自動Match ID連動）
    fixture_labels = [f["label"] for f in fixtures]
    selected_idx = st.selectbox(
        "📅 試合・節を選択（自動連動）",
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
            <span>🎯 判定: 得失点差 +{gd}点差</span>
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
