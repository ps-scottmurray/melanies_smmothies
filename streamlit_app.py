# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()

helpful_links = [
    "https://docs.streamlit.io",
    "https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit",
    "https://github.com/Snowflake-Labs/snowflake-demo-streamlit",
    "https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake"
]

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie")

name_on_order = st.text_input('Name on Smoothie: ')

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_string = ''
ingredients_list = []

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list and name_on_order:
    ingredients_string = ' '.join(ingredients_list) + ' '

    for fruit_chosen in ingredients_list:
        search_on = my_dataframe.filter(col('FRUIT_NAME') == fruit_chosen).select(col('SEARCH_ON')).collect()[0][0]
        st.write(f'You chose: {fruit_chosen} with search term: {search_on}')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                values('{ingredients_string}', '{name_on_order}')"""

        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon = "✅")
