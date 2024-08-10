import streamlit as st
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# アップロードされた画像を使用
background_image_path = "kyukurarin.png"  # ここにローカルファイルのパスを指定

# Base64にエンコード
base64_background = get_base64_of_bin_file(background_image_path)

# カスタムCSSで背景画像を設定し、文字に半透明の背景と大きめのフォントサイズを追加
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{base64_background}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

html, body, [class*="st"] {{
    background-color: rgba(0, 0, 0, 0.7) !important;  /* より不透明な背景色 */
    background-image: url("data:image/png;base64,{base64_background}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: white;
    font-size: 15px;  /* フォントサイズを大きく */
}}

[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"] {{
    background-color: rgba(0, 0, 0, 0.7) !important;  /* より不透明な背景色 */
    color: white;
    font-size: 25px;
}}

[data-testid="stMarkdownContainer"] p {{
    font-size: 35px;
    color: white;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# GIF画像のファイルパスを指定
gif_image_path = "SkyBlock_items_enchanted_book.gif"  # ここにGIF画像のローカルファイルパスを指定

# GIF画像をBase64にエンコード
base64_gif = get_base64_of_bin_file(gif_image_path)

# カスタムCSSでGIF画像を中央に配置し、位置を調整
gif_display = f"""
<style>
.centered-gif {{
    position: absolute;
    top: -50px;  /* 位置を上に調整 */
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
}}

</style>

<div class="centered-gif">
    <img src="data:image/gif;base64,{base64_gif}" alt="centered gif">
</div>
"""

st.markdown(gif_display, unsafe_allow_html=True)

# ここからコンテンツを下にずらす
st.markdown("""
    <style>
    .main-content {{
        padding-top: 100px;  /* ここでコンテンツを100px下にずらす */
    }}
    .custom-title {{
        position: relative;
        top: 20px;  /* 追加でタイトルを下に調整 */
        text-align: center;
        font-size: 32px;
        color: black;  /* タイトルの色を黒に設定 */
    }}
    </style>
    """, unsafe_allow_html=True)

# クライアントの初期化
from openai import OpenAI
client = OpenAI()

# 必要なモジュールのインポート
from duckduckgo_search import DDGS

def search_duckduckgo(query, num_results=5):
    results = []
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=num_results))
    return results

# Streamlitアプリのタイトルを設定する
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown('<h1 class="custom-title">レコメンドbook</h1>', unsafe_allow_html=True)

# メッセージの初期化
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "こんにちは！お名前を教えてください。"}]
    st.session_state.user_question_count = 0  # 質問回数の初期化
    st.session_state.query_generated = False  # 検索クエリ生成フラグの初期化

# これまでのメッセージを表示
with st.container():  # ここで全体のコンテナを作成
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

st.markdown('</div>', unsafe_allow_html=True)

# ユーザーが新しいメッセージを入力できるテキストボックス
if prompt := st.chat_input("質問やメッセージを入力してください"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.user_question_count += 1  # 質問回数のカウントを増やす
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.user_question_count > 4:
        if not st.session_state.query_generated:
            message = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            message.append({"role": "system", "content": "以上の会話履歴から検索クエリを生成して。検索クエリのみ出力して"})
            
            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=message,
                )
                query = response.choices[0].message.content
                st.session_state.query_generated = True
                st.session_state.search_query = query.strip()

        results = search_duckduckgo(st.session_state.search_query)
        
        with st.chat_message("assistant"):
            for result in results:
                st.markdown(f"**Title**: {result['title']}")
                st.markdown(f"**URL**: {result['href']}")
                st.markdown(f"**Description**: {result['body']}")
                st.markdown("---")
    else:
        questions = ["読みたい本のジャンルは何ですか(例:ミステリー、ファンタジー、SF、恋愛など)", 
                     "どの年代の本が読みたいですか(例:古典、現代、2020年に話題になった本など)", 
                     "最近読んだ本で面白かった本はありますか", 
                     "好きな作家や興味のあるテーマはありますか"]

        st.session_state.messages.append({"role": "assistant", "content": f"{questions[st.session_state.user_question_count - 1]}"})
        with st.chat_message("assistant"):
            st.markdown(questions[st.session_state.user_question_count - 1])
