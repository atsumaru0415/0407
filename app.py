import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="広告分析ダッシュボード", layout="wide")
st.title("📊 スポンサープロダクト広告分析ツール")

# ファイルアップロード（CSV）
uploaded_file = st.sidebar.file_uploader("広告データ（CSV）をアップロードしてください", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # 列名を標準化（日本語→英語変換）
    df.rename(columns={
        'カスタマーの検索キーワード': 'Keyword',
        '日付': 'Date',
        'インプレッション': 'Impressions',
        'クリック': 'Clicks',
        '費用': 'Cost',
        '広告がクリックされてから7日間の総売上高': 'Sales',
        '広告費売上高比率（ACOS）合計': 'ACOS',
        '広告費用対効果（ROAS）合計': 'ROAS'
    }, inplace=True)

    # サイドバーでメニュー選択
    menu = st.sidebar.radio("表示する分析を選択", (
        "キーワード別の成果一覧",
        "キャンペーン全体の概要",
        "日別推移の可視化",
        "レコメンド機能"
    ))

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    if menu == "キーワード別の成果一覧":
        st.header("🔍 キーワード別 成果一覧")
        if 'Keyword' in df.columns:
            keyword_summary = df.groupby("Keyword").agg({
                'Impressions': 'sum',
                'Clicks': 'sum',
                'Cost': 'sum',
                'Sales': 'sum',
                'ACOS': 'mean',
                'ROAS': 'mean'
            }).reset_index()

            keyword_summary = keyword_summary.sort_values("Sales", ascending=False)
            st.dataframe(keyword_summary, use_container_width=True)

            st.subheader("🔖 ASINと画像")
            for index, row in keyword_summary.iterrows():
                keyword = row["Keyword"]
                if isinstance(keyword, str) and len(keyword) == 10 and keyword.isalnum():
                    image_url = f"https://images-na.ssl-images-amazon.com/images/P/{keyword}.01._SCLZZZZZZZ_.jpg"
                    st.markdown(f"**{keyword}**")
                    st.image(image_url, width=150)
        else:
            st.warning("Keyword列が見つかりませんでした。")

    elif menu == "キャンペーン全体の概要":
        st.header("📈 キャンペーン全体の概要")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("インプレッション", f"{int(df['Impressions'].sum()):,}")
        col2.metric("クリック数", f"{int(df['Clicks'].sum()):,}")
        col3.metric("広告費", f"¥{df['Cost'].sum():,.0f}")
        col4.metric("売上", f"¥{df['Sales'].sum():,.0f}")

        chart = alt.Chart(df).mark_bar().encode(
            x='Keyword:N',
            y='Sales:Q',
            tooltip=['Keyword', 'Sales']
        ).properties(width=800, height=400).interactive()

        st.altair_chart(chart)

    elif menu == "日別推移の可視化":
        st.header("📆 日別推移")
        if 'Date' in df.columns:
            daily = df.groupby("Date").agg({
                'Impressions': 'sum',
                'Clicks': 'sum',
                'Cost': 'sum',
                'Sales': 'sum',
            }).reset_index()

            st.line_chart(daily.set_index("Date"))
        else:
            st.warning("Date列が見つかりませんでした。")

    elif menu == "レコメンド機能":
        st.header("💡 改善アクション提案")

        if all(col in df.columns for col in ['Keyword', 'Cost', 'ROAS', 'Clicks', 'Sales']):
            bad_roas = df[(df['Cost'] > 0) & (df['ROAS'] < 1)]
            no_sales = df[(df['Clicks'] > 5) & (df['Sales'] == 0)]

            st.subheader("ROAS が低いキーワード")
            if not bad_roas.empty:
                st.dataframe(bad_roas[['Keyword', 'Cost', 'Sales', 'ROAS']], use_container_width=True)
                st.info("ROAS が 1 未満のキーワードは費用に対して効果が出ていません。停止や調整を検討しましょう。")
            else:
                st.success("ROAS が 低いキーワードはありません。")

            st.subheader("クリック多いが売れていないキーワード")
            if not no_sales.empty:
                st.dataframe(no_sales[['Keyword', 'Clicks', 'Sales']], use_container_width=True)
                st.info("クリックは多いが売れていないキーワードがあります。訴求内容の見直しやキーワード除外を検討してください。")
            else:
                st.success("クリックはある程度あり、売上も発生しています。")
        else:
            st.warning("必要な列（Keyword、Cost、ROAS、Clicks、Sales）が足りません。")
else:
    st.info("左のサイドバーからCSVファイルをアップロードしてください。")
