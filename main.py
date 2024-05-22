import streamlit as st
from openai import OpenAI

# 必要なモジュールのインポート
from openai_client import OpenAIClient
from serializer import serialize
from database_handler import DatabaseHandler
from streamlit_interface import initialize_session_state, display_chat, add_user_message, add_assistant_message

# Streamlitアプリのタイトルを設定する
st.title("江戸時代の卵料理がわかる君")

# セッション状態の初期化
initialize_session_state()

# これまでのメッセージを表示
display_chat()

# ユーザーが新しいメッセージを入力できるテキストボックス
if prompt := st.chat_input("質問やメッセージを入力してください"):
    # ユーザーメッセージを追加
    add_user_message(prompt)
    
    # OpenAI クライアントの初期化と埋め込み生成
    openai_client = OpenAIClient(model="text-embedding-3-large")
    query_embedding = openai_client.generate_embedding(prompt)
    serialized_embedding = serialize(query_embedding)

    # データベースの操作
    db_handler = DatabaseHandler("example_vec.db")
    db_handler.connect()
    results = db_handler.search_recipes(serialized_embedding)
    db_handler.close()

    # レシピ検索結果をセッションに追加
    message = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    message.insert(
        0,
        {
            "role": "system",
            "content": f"# レシピ検索結果\n {results} \nこれはレシピ検索結果です。これに基づいて質問に答えます。レシピ検索結果がない場合は、「データにありません」を出力します。",
        },
    )

    # OpenAI APIを使用してアシスタントの応答を取得
    client = OpenAI()
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=message,
        stream=True,
    )
    response = st.write_stream(stream)

    # アシスタントメッセージを追加
    add_assistant_message(response)
