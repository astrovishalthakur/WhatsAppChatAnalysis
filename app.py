import streamlit as st
import helper
import preprocessor
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize session state

if "load_state" not in st.session_state:
    st.session_state.load_state = False

st.sidebar.title("Whatsapp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None or st.session_state.load_state:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # the file we uploaded on streamlit is byte data, we need to convert it to string.

    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users.

    user_list = df["users"].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show Analysis wrt", user_list)

    if st.sidebar.button("Show Analysis") or st.session_state.load_state:
        st.session_state.load_state = True
        # stats area
        num_messages, words, num_media, num_links = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total Words")
            st.title(words)

        with col3:
            st.header("Media Shared")
            st.title(num_media)

        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline["time"], timeline["message"], color="green")
        plt.xticks(rotation="vertical")
        plt.ylabel("Messages")
        st.pyplot(fig)

        # Daily Timeline

        try:

            st.title("Daily Timeline")
            a = timeline.time.unique()
            options = st.multiselect("Choose Months", a, a[-2])

            fig, ax = plt.subplots()
            for i in options:
                timeL = helper.daily_df(selected_user, df, i)
                ax.plot(timeL.day, timeL.message, label=f"{i}")
            plt.legend(loc="best")
            plt.xlim((1, 31))
            plt.xlabel("Date")
            plt.ylabel("Messages")
            st.pyplot(fig, clear_figure=True)

        except IndexError:
            pass

        # finding the busiest users in the group(Group level)
        if selected_user == "Overall":
            st.title("Most Busy Users")
            x, new_df = helper.fetch_most_busy_users(df)

            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color="#F76E11")
                plt.xticks(rotation="vertical")

                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color="orange")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        # activity heatmap
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(20, 10))
        ax = sns.heatmap(user_heatmap)
        plt.xlabel("Time(24 Hrs)")
        plt.ylabel("Days")
        st.pyplot(fig)

        # WordCloud
        try:
            st.title("WordCloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)
        except Exception as e:
            pass

        # most common words
        try:
            st.title("Most Common Words")
            most_common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0][::-1], most_common_df[1][::-1])
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        except Exception as e:
            pass
        # emoji analysis

        try:

            st.title("Most Common Emojis")
            emoji_df = helper.emoji_helper(selected_user, df)

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df["Number"].head(), labels=emoji_df["emoji"].head(), autopct="%0.2f")
                st.pyplot(fig)

        except KeyError:
            pass


footer = """<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: black;
color: white;
text-align: center;
}

#love {
color: red;
}
</style>
<div class="footer">
<p>Developed with <span id="love">❤</span> by <a style='display: block; text-align: center;' href="https://github.com/astrovishalthakur" target="_blank">Vishal Thakur</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)


