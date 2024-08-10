import streamlit as st
from openai import OpenAI
import numpy as np

# クライアントの初期化
client = OpenAI()

# 必要なモジュールのインポート
from duckduckgo_search import DDGS

def search_duckduckgo(query, num_results=5):
    """
    DuckDuckGoで検索を実行し、結果を表示する関数
    
    :param query: 検索クエリ
    :param num_results: 取得する検索結果の数（デフォルト: 5）
    """
    results = []
    # DDGSオブジェクトのコンテキストマネージャを使用
    with DDGS() as ddgs:
        # テキスト検索を実行し、結果をリストに変換
        results = list(ddgs.text(query, max_results=num_results))
    return results

# Streamlitアプリのタイトルを設定する
st.title("テスト")


# メッセージの初期化
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "こんにちは！お名前を教えてください。"}]
    st.session_state.user_question_count = 0  # 質問回数の初期化
    st.session_state.query_generated = False  # 検索クエリ生成フラグの初期化


# これまでのメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ユーザーが新しいメッセージを入力できるテキストボックス
if prompt := st.chat_input("質問やメッセージを入力してください"):
    # ユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.user_question_count += 1  # 質問回数のカウントを増やす
    with st.chat_message("user"):
        st.markdown(prompt)

    # 質問回数が4回以上の場合
    if st.session_state.user_question_count > 4:
        # メッセージをapiの形式に変換
        if not st.session_state.query_generated:
            message = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            message.append({"role": "system", "content": "以上の会話履歴から検索クエリを生成して。検索クエリのみ出力して"})
            
            with st.chat_message("assistant"):
                # OpenAI APIを使用して検索クエリを生成
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=message,
                )
                query = response.choices[0].message.content
                st.session_state.query_generated = True
                st.session_state.search_query = query.strip()

        # DuckDuckGoで検索
        results = search_duckduckgo(st.session_state.search_query)
        
        # 検索結果を表示
        with st.chat_message("assistant"):
            for result in results:
                st.markdown(f"**Title**: {result['title']}")
                st.markdown(f"**URL**: {result['href']}")
                st.markdown(f"**Description**: {result['body']}")
                st.markdown("---")
    else:
        # 質問のリスト
        questions = ["読みたい本のジャンルは何ですか(例:ミステリー、ファンタジー、SF、恋愛など)", 
                     "どの年代の本が読みたいですか(例:古典、現代、2020年に話題になった本など)", 
                     "最近読んだ本で面白かった本はありますか", 
                     "好きな作家や興味のあるテーマはありますか"]

        # アシスタントメッセージを追加
        st.session_state.messages.append({"role": "assistant", "content": f"{questions[st.session_state.user_question_count - 1]}"})
        with st.chat_message("assistant"):
            st.markdown(questions[st.session_state.user_question_count - 1])
