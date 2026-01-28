import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ---------------------------------------------------------
# 1. アプリ設定 & デザイン (ポップで優しい雰囲気)
# ---------------------------------------------------------
st.set_page_config(
    page_title="🌱 身体のクセ診断 | SEEK STUDIO", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 全体のフォントや雰囲気を柔らかく */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fb 100%);
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    /* ヘッダー部分の装飾 */
    .header-container {
        text-align: center;
        padding: 2rem 1rem;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1rem;
        color: #718096;
        line-height: 1.6;
    }
    
    /* ラジオボタンを横並び＆ボタン風に */
    .stRadio > div {
        flex-direction: row;
        gap: 8px;
    } 
    
    .stRadio label {
        font-weight: 500;
        background: #ffffff;
        border-radius: 10px;
        padding: 12px 20px;
        margin-right: 0;
        border: 2px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stRadio label:hover {
        background: #f7fafc;
        border-color: #cbd5e0;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* 結果表示ボックスのデザイン */
    .result-box {
        padding: 30px; 
        border-radius: 20px; 
        margin-bottom: 25px; 
        color: #fff;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        animation: fadeInUp 0.5s ease;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .type-a {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%); 
        color: #2d3748;
    }
    
    .type-b {
        background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); 
        color: #2d3748;
    }
    
    .type-c {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); 
        color: #2d3748;
    }
    
    /* レッドフラッグ警告 */
    .red-flag {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%);
        border: 3px solid #ff9800;
        padding: 25px; 
        border-radius: 15px; 
        color: #663c00;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(255, 152, 0, 0.2);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 4px 12px rgba(255, 152, 0, 0.2);
        }
        50% {
            box-shadow: 0 8px 20px rgba(255, 152, 0, 0.4);
        }
    }
    
    /* プログレスバー */
    .progress-container {
        margin: 2rem 0;
        text-align: center;
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 10px;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    
    /* タブのスタイリング */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 12px 24px;
        border: 2px solid #e2e8f0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
    
    /* ボタンスタイル */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* カード風のコンテナ */
    .question-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
    
    h1 {color: #2d3748;}
    h2 {color: #2d3748;}
    h3 {margin-top: 0; color: #2d3748;}
    
    /* フッター */
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 2px solid #e2e8f0;
        color: #718096;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. データ保存機能
# ---------------------------------------------------------
HISTORY_FILE = "diagnosis_history.json"

def save_diagnosis_result(result_data):
    """診断結果を履歴として保存"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    history.append(result_data)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------
# 3. タイトル・導入
# ---------------------------------------------------------
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌱 身体のクセ診断</h1>
    <p class="subtitle">
        いくつかの質問に答えるだけで、今のあなたの<strong>「身体のタイプ」</strong>と<br>
        <strong>「優先すべきケア」</strong>がわかります。<br>
        直感でポチポチ選んでみてください！
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. レッドフラッグ（安全チェック）
# ---------------------------------------------------------
st.divider()
st.markdown("### 🛡️ 安全チェック")
st.caption("まずは念のため、今の身体の状態を確認させてください")

rf_col1, rf_col2 = st.columns(2)
with rf_col1:
    rf1 = st.radio(
        "❶ しびれや、力が入りにくい感じはありますか？", 
        ["いいえ", "はい"], 
        index=0, 
        horizontal=True,
        help="手足のしびれや筋力低下がある場合は医療機関への相談をおすすめします"
    )
with rf_col2:
    rf2 = st.radio(
        "❷ じっとしていても痛む、または夜間に痛みで目が覚めますか？", 
        ["いいえ", "はい"], 
        index=0, 
        horizontal=True,
        help="安静時痛や夜間痛は重要な症状のサインです"
    )

if rf1 == "はい" or rf2 == "はい":
    st.markdown("""
    <div class="red-flag">
        <h3>⚠️ ちょっとストップ！</h3>
        <p style="margin-top: 1rem; line-height: 1.8;">
        強い痛み・しびれ・夜間痛がある場合は、<strong>医療機関（整形外科など）での相談をおすすめします。</strong><br><br>
        無理にセルフケアを続けると症状が悪化する可能性があります。<br>
        まずは専門医の診察を受けてから、適切なケアを始めましょう。<br><br>
        お大事になさってください 🙏
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop() 

# ---------------------------------------------------------
# 5. メイン診断（シルエット ＆ 質問）
# ---------------------------------------------------------
st.divider()
st.markdown("### 📝 身体のクセチェック")

# ★ここに「女性のシルエット画像」を表示（実際の画像に差し替え可能）
st.image("https://placehold.co/600x300/e8f5e9/4caf50?text=あなたの身体のクセを見つけよう！", 
         use_column_width=True)

st.info("💡 以下の質問に「直感」で答えてください。深く考えすぎなくて大丈夫です！")

# 質問データ（重み付け：決定打=3, 補助=2）
questions = {
    "A": {
        "name": "呼吸・胸郭タイプ",
        "emoji": "💨",
        "short_name": "肋骨が開きやすい",
        "q": [
            {"text": "仰向けで大きく息を吐いた時、肋骨（みぞおち周り）が下がりにくいですか？", "weight": 3},
            {"text": "「反り腰を直そう」とお腹に力を入れると、呼吸がしづらくなりますか？", "weight": 3},
            {"text": "気づくと、みぞおちが前に突き出るような姿勢になっていますか？", "weight": 2},
            {"text": "お腹よりも、前ももや腰周りに張りや疲れを感じやすいですか？", "weight": 2},
        ]
    },
    "B": {
        "name": "骨盤・股関節タイプ",
        "emoji": "🦴",
        "short_name": "骨盤が安定しにくい",
        "q": [
            {"text": "片脚で立つと、骨盤が左右にグラグラと揺れる感じがしますか？", "weight": 3},
            {"text": "スクワットや階段の上り下りで、お尻よりも太もも（前・外側）が先に疲れますか？", "weight": 3},
            {"text": "立っている時、腰を反ったり丸めたりはできるけど、「真ん中」で安定させるのが難しいですか？", "weight": 2},
            {"text": "歩いている時、脚が外に流れたり内側に入ったり、軌道がブレやすいですか？", "weight": 2},
        ]
    },
    "C": {
        "name": "足部・足首タイプ",
        "emoji": "👣",
        "short_name": "足のアーチが崩れやすい",
        "q": [
            {"text": "立っている時、足の親指の付け根（母趾球）にうまく体重が乗らない感じがしますか？", "weight": 3},
            {"text": "つま先立ちをすると、足の指が浮いたり、外側に逃げたりしますか？", "weight": 3},
            {"text": "靴底の減り方に偏りがあり、特定の場所だけすり減りやすいですか？", "weight": 2},
            {"text": "歩いたり立ったりしていると、ふくらはぎがパンパンに張りやすいですか？", "weight": 2},
        ]
    }
}

# 回答フォーム生成
scores = {"A": 0, "B": 0, "C": 0}
options = ["いいえ", "少し当てはまる", "はい"] 

# タブでスッキリ表示（絵文字とタイトルを追加）
tab_a, tab_b, tab_c = st.tabs([
    f"{questions['A']['emoji']} 胸・呼吸", 
    f"{questions['B']['emoji']} 腰・骨盤", 
    f"{questions['C']['emoji']} 足・脚"
])

def ask_questions(type_key, tab):
    with tab:
        st.markdown(f"### {questions[type_key]['emoji']} {questions[type_key]['name']}")
        st.caption(f"特徴：{questions[type_key]['short_name']}")
        st.markdown("---")
        
        current_score = 0
        total_questions = len(questions[type_key]["q"])
        
        for i, item in enumerate(questions[type_key]["q"], 1):
            key = f"{type_key}_{i}"
            
            # 質問カードのスタイリング
            st.markdown(f"##### 質問 {i} / {total_questions}")
            st.markdown(f"**{item['text']}**")
            
            # インデックス設定: いいえ=0, 少し当てはまる=1, はい=2
            ans_index = st.radio(
                "回答を選択してください",
                range(len(options)), 
                format_func=lambda x: options[x], 
                key=key, 
                horizontal=True,
                label_visibility="collapsed"
            )
            
            # 点数計算
            if ans_index == 2:  # はい
                current_score += item['weight']
            elif ans_index == 1:  # 少し当てはまる
                current_score += 1
            else:
                current_score += 0
            
            if i < total_questions:
                st.markdown("<br>", unsafe_allow_html=True)
        
        return current_score

scores["A"] = ask_questions("A", tab_a)
scores["B"] = ask_questions("B", tab_b)
scores["C"] = ask_questions("C", tab_c)

# ---------------------------------------------------------
# 6. 診断実行 ＆ 結果表示
# ---------------------------------------------------------
st.divider()
st.markdown("### 🎯 診断を実行")
st.markdown("すべての質問に答えたら、下のボタンを押してください")

if st.button("🔍 診断結果を見る", type="primary", use_container_width=True):
    
    st.divider()
    st.markdown("# 📊 あなたの診断結果")
    
    # スコア集計
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    first = sorted_scores[0]
    second = sorted_scores[1]
    
    # 混合タイプ判定（1位と2位が2点差以内 かつ ある程度点数がある）
    is_mixed = (first[1] - second[1]) <= 2 and second[1] >= 3
    
    # 詳細なアドバイス文
    advices = {
        "A": {
            "summary": "呼吸が浅く、肋骨が開いているため、反り腰や前ももの張りが起きています。",
            "priority": "肋骨を締める呼吸エクササイズ",
            "details": [
                "仰向けで膝を立て、息を吐きながら肋骨を床に近づける練習",
                "呼吸に合わせてお腹周りのインナーマッスルを活性化",
                "反り腰改善と前もものリラックス"
            ],
            "benefit": "呼吸が深くなり、姿勢が安定します。前ももの張りも軽減されます。"
        },
        "B": {
            "summary": "骨盤周りのインナーマッスルが機能しておらず、お尻の筋肉がうまく使えていません。",
            "priority": "骨盤をニュートラルに保つ練習",
            "details": [
                "骨盤の前後傾コントロール（骨盤時計）",
                "お尻の筋肉（中殿筋）の活性化エクササイズ",
                "片脚立ちでバランス強化"
            ],
            "benefit": "骨盤が安定し、太ももの疲れが減ります。歩行も楽になります。"
        },
        "C": {
            "summary": "足のアーチが崩れており、着地のたびに足首や膝にねじれが生じています。",
            "priority": "足指を使えるようにするワーク",
            "details": [
                "足指グーパー運動で足のアーチを作る",
                "タオルギャザーで足裏の筋肉を鍛える",
                "母趾球（親指の付け根）でしっかり踏む練習"
            ],
            "benefit": "足元が安定し、ふくらはぎの張りが軽減します。歩行効率も向上します。"
        }
    }

    if first[1] == 0 and second[1] == 0:
        st.warning("⚠️ チェック項目がまだ選ばれていないようです！上のタブから質問に答えてください。")
    
    elif is_mixed:
        type1_key = first[0]
        type2_key = second[0]
        type1_name = questions[type1_key]['name']
        type2_name = questions[type2_key]['name']
        
        st.markdown(f"""
        <div class="result-box type-{type1_key.lower()}">
            <h2 style='margin-top:0;'>🔄 あなたは「混合タイプ」です！</h2>
            <h3>{questions[type1_key]['emoji']} {type1_name} × {questions[type2_key]['emoji']} {type2_name}</h3>
            <p style='font-size:1.1rem; margin-top:1rem;'>
            2つのクセが組み合わさっています。<br>
            優先的に取り組むべきは<strong>「{type1_name}」</strong>のアプローチです。
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 優先アドバイス
        advice = advices[type1_key]
        st.markdown("### 💡 あなたへのアドバイス")
        st.info(f"**現状：** {advice['summary']}")
        
        st.markdown(f"### 🎯 優先して取り組むこと")
        st.success(f"**{advice['priority']}**")
        
        st.markdown("#### 📝 具体的なエクササイズ")
        for i, detail in enumerate(advice['details'], 1):
            st.markdown(f"{i}. {detail}")
        
        st.markdown("#### ✨ 期待できる効果")
        st.markdown(f"**{advice['benefit']}**")
        
        # 第2優先のアドバイス
        with st.expander(f"📌 第2優先：{questions[type2_key]['name']} のケアも大切です", expanded=False):
            advice2 = advices[type2_key]
            st.markdown(f"**現状：** {advice2['summary']}")
            st.markdown(f"**優先アプローチ：** {advice2['priority']}")
            
    else:
        result_key = first[0]
        result_name = questions[result_key]['name']
        result_emoji = questions[result_key]['emoji']
        
        st.markdown(f"""
        <div class="result-box type-{result_key.lower()}">
            <h2 style='margin-top:0;'>{result_emoji} あなたは「{result_name}」です！</h2>
            <p style='font-size:1.1rem; margin-top:1rem;'>
            {questions[result_key]['short_name']}傾向が見られます
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 詳細アドバイス
        advice = advices[result_key]
        st.markdown("### 💡 あなたへのアドバイス")
        st.info(f"**現状：** {advice['summary']}")
        
        st.markdown(f"### 🎯 優先して取り組むこと")
        st.success(f"**{advice['priority']}**")
        
        st.markdown("#### 📝 具体的なエクササイズ")
        for i, detail in enumerate(advice['details'], 1):
            st.markdown(f"{i}. {detail}")
        
        st.markdown("#### ✨ 期待できる効果")
        st.markdown(f"**{advice['benefit']}**")

    # グラフ表示
    st.divider()
    st.markdown("### 📈 あなたのバランス分析")
    chart_data = pd.DataFrame({
        "タイプ": [
            f"{questions['A']['emoji']} {questions['A']['name']}", 
            f"{questions['B']['emoji']} {questions['B']['name']}", 
            f"{questions['C']['emoji']} {questions['C']['name']}"
        ],
        "スコア": [scores["A"], scores["B"], scores["C"]]
    })
    st.bar_chart(chart_data, x="タイプ", y="スコア", height=300)
    
    # スコア詳細
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{questions['A']['emoji']} 呼吸・胸郭", f"{scores['A']}点", 
                 help=questions['A']['name'])
    with col2:
        st.metric(f"{questions['B']['emoji']} 骨盤・股関節", f"{scores['B']}点",
                 help=questions['B']['name'])
    with col3:
        st.metric(f"{questions['C']['emoji']} 足部・足首", f"{scores['C']}点",
                 help=questions['C']['name'])
    
    # 診断結果を保存
    result_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scores": scores,
        "primary_type": first[0],
        "is_mixed": is_mixed
    }
    save_diagnosis_result(result_data)
    
    # CTA（公式LINEなどへ）
    st.divider()
    st.markdown("### 🎁 もっと詳しく知りたい方へ")
    st.success("今のあなたにぴったりの **セルフケア動画** と **個別アドバイス** をプレゼントしています！")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.link_button("📱 公式LINEで改善動画を受け取る", "https://lin.ee/your-line-link", use_container_width=True)
    with col_btn2:
        if st.button("📥 結果をダウンロード（開発中）", use_container_width=True, disabled=True):
            pass

# ---------------------------------------------------------
# 7. フッター
# ---------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <strong>SEEK STUDIO</strong><br>
    科学的根拠に基づいた身体ケア<br>
    <small style="color: #a0aec0; margin-top: 0.5rem; display: inline-block;">
    ⚠️ この診断は医療行為ではありません。深刻な症状がある場合は医療機関にご相談ください。
    </small>
</div>
""", unsafe_allow_html=True)
