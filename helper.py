from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()


def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df.users == selected_user]

    # 1. number of messages
    num_messages = df.shape[0]

    # 2. number of words
    words = []
    for message in df.message:
        words.extend(message.split())

    # 3. fetch number of media messages
    num_media = df[df.message == "<Media omitted>\n"].shape[0]

    # 4. fetch number of links shared
    links = []
    for message in df.message:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media, len(links)


def fetch_most_busy_users(df):
    new_df = round((df.users.value_counts() / df.shape[0]) * 100, 2) \
        .reset_index().rename(columns={"index": "name", "users": "percentage"})
    count = df.users.value_counts().head()
    return count, new_df


def remove_stop_words(df):
    f = open("HinglishStop.txt", 'r')
    stop_words = f.read()

    temp = df[df.users != "group_notification"]

    temp = temp[temp["message"] != "<Media omitted>\n"]

    words = []
    for message in temp.message:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    em_less_words = []
    for i in words:
        em = False
        for j in i[0]:
            if j in emoji.UNICODE_EMOJI['en']:
                em = True
                break
        if not em:
            em_less_words.append(i)

    return em_less_words


def create_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df.users == selected_user]

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color="white")

    wc_lis = remove_stop_words(df)
    wc_str = " ".join(wc_lis)
    df_wc = wc.generate(wc_str)
    return df_wc


def most_common_words(selected_user, df):

    if selected_user != "Overall":
        df = df[df.users == selected_user]

    em_less_words = remove_stop_words(df)

    most_common_df = pd.DataFrame(Counter(em_less_words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    # Most Common Emoji

    if selected_user != "Overall":
        df = df[df.users == selected_user]

    emojis = []
    for message in df.message:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df.rename(columns={0: "emoji", 1: "Number"})


def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df.users == selected_user]
    timeline = df.groupby(["year", "month_num", "month"]).count()["message"].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline["month"][i] + "-" + str(timeline["year"][i]))
    timeline["time"] = time
    return timeline


def daily_df(selected_user, df, k):
    if selected_user != "Overall":
        df = df[df.users == selected_user]
    mo = k.split("-")[0]
    ye = k.split("-")[1]
    month_df = df[(df.month == mo) & (df.year == int(ye))]
    daily_time = month_df.groupby(["day"]).count()["message"].reset_index()
    return daily_time


def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df.users == selected_user]
    return df.day_name.value_counts()


def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df.users == selected_user]
    return df["month"].value_counts()


def activity_heatmap(selected_user,df):
    if selected_user != "Overall":
        df = df[df.users == selected_user]

    heatmap = df.pivot_table(index="day_name", columns="period", values="message", aggfunc="count").fillna(0)

    return heatmap
