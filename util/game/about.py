import streamlit as st

def show_about():
    st.sidebar.title("About")

    st.sidebar.header("小游戏")
    st.sidebar.markdown("""
    这款互动多人游戏是使用 Python 和 Streamlit 来展示实时交互能力的一个示例。而且以这种方式构建一个简单的游戏很有趣。
    """, unsafe_allow_html=True)

