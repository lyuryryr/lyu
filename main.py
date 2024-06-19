import streamlit as st
from openai import OpenAI

# 必要なモジュールのインポート
from openai_client import OpenAIClient
from serializer import serialize
from database_handler import DatabaseHandler
from streamlit_interface import initialize_session_state, display_chat, add_user_message, add_assistant_message

# Streamlitアプリのタイトルを設定する
st.title("テスト")

# クライアントの初期化
client = OpenAI()

# メッセージの初期化
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "こんにちは！お名前を教えてください。"}]
    st.session_state.user_question_count = 0  # 質問回数の初期化


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
        message = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

        with st.chat_message("assistant"):
            # OpenAI APIを使用してアシスタントの応答を取得
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=message,
                stream=True,
            )
            response = st.write_stream(stream)

        # アシスタントメッセージを履歴に追加
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        # 質問のリスト
        questions = ["好きなジャンルは何ですか？", "出身地は？", "趣味は？", "好きな食べ物は？"]

        # アシスタントメッセージを追加
        st.session_state.messages.append({"role": "assistant", "content": f"{questions[st.session_state.user_question_count - 1]}"})
        with st.chat_message("assistant"):
            st.markdown(questions[st.session_state.user_question_count - 1])
            