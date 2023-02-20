import pickle
import pandas as pd
import json
import numpy as np
import streamlit as st
import datetime
import sklearn
from sklearn.ensemble import RandomForestRegressor
from PIL import Image, ImageOps
import base64


with open("columns.json", "r") as jf:
    json_file = json.load(jf)
    all_col = pd.json_normalize(json_file, record_path=['data_columns'])
    all_col.rename(columns={0: 'Columns'}, inplace=True)
    source = pd.json_normalize(json_file, record_path=['source_name'])
    source.rename(columns={0: 'Source'}, inplace = True)
    destination = pd.json_normalize(json_file, record_path=['destination_name'])
    destination.rename(columns={0: 'Destination'}, inplace = True)
    airline = pd.json_normalize(json_file, record_path=['airline_name'])
    airline.rename(columns={0: 'Airline'}, inplace = True)

pickle_in = open("reg_rf.pkl", "rb")
regressor = pickle.load(pickle_in)

def predict_price(stops, mon, dep_hr, dep_min, tot_min, airline, source, destination, dow):
    x = np.zeros(len(all_col['Columns']))
    x[0] = stops
    x[1] = mon
    x[2] = dep_hr
    x[3] = dep_min
    x[4] = tot_min

    if airline == 'Air Asia':
        pass
    else:
        airline_index = all_col[all_col['Columns'] == 'airline_' + airline.lower()].index[0]
        if airline_index >= 0:
            x[airline_index] = 1
    if source == 'Banglore':
        pass
    else:
        source_index = all_col[all_col['Columns'] == 'source_'+ source.lower()].index[0]
        if source_index >= 0:
            x[source_index] = 1
    if destination == 'Banglore':
        pass
    else:
        dest_index = all_col[all_col['Columns'] == 'destination_' + destination.lower()].index[0]
        if dest_index >= 0:
            x[dest_index] = 1
    if dow.lower() == 'friday':
        pass
    else:
        dow_index = all_col[all_col['Columns'] == 'day of the week_' + dow.lower()].index[0]
        if dow_index >=0:
            x[dow_index] = 1
    return str(int(regressor.predict([x])[0])) + " rupees."



# def predict_price(stops, mon, dep_hr, dep_min, tot_min, airline, source, destination, dow):
#     airline_index = all_col[all_col['Columns'] == 'airline_' + airline.lower()].index[0]
#     source_index = all_col[all_col['Columns'] == 'source_'+ source.lower()].index[0]
#     dest_index = all_col[all_col['Columns'] == 'destination_' + destination.lower()].index[0]
#     dow_index = all_col[all_col['Columns'] == 'day of the week_' + dow.lower()].index[0]
#
#
#     x = np.zeros(len(all_col['Columns']))
#     x[0] = stops
#     x[1] = mon
#     x[2] = dep_hr
#     x[3] = dep_min
#     x[4] = tot_min
#     if source_index >= 0:
#         x[source_index] = 1
#     if dest_index >= 0:
#         x[dest_index] = 1
#     if airline_index >=0:
#         x[airline_index] = 1
#     if dow_index >=0:
#         x[dow_index] = 1
#     return str(int(regressor.predict([x])[0])) + " rupees."


@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_jpg_as_page_bg(jpg_file):
    bin_str = get_base64_of_bin_file('img4.jpg')
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/jpeg;base64,%s");
    opacity:0.85;
    background-size: cover;
    }
    </style>
    ''' % bin_str

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return


set_jpg_as_page_bg('img4.jpg')

# image = Image.open("img3.jpeg")
# st.image(image, width = 700)
colh1, colh2, colh3 = st.columns((1,5,1))
colh2.title("FLIGHT PRICE PREDICTOR")

col1, col2 =st.columns((1,1))
dep_date = col1.date_input("Select departure date:")
arr_date = col2.date_input("Select arrival date:")
mon = dep_date.month
dow = dep_date.strftime('%A')
if arr_date < dep_date:
    st.error('ERROR! Arrival date cannot be before departure date. Please input a valid arrival date', icon="🚨")
col3, col4 = st.columns((1, 1))
dep_time = col3.time_input("Select departure time:")
arr_time = col4.time_input("Select arrival time:")
dep_hr = dep_time.hour
dep_min = dep_time.minute
if dep_date == arr_date and arr_time <= dep_time:
    st.error("ERROR! Arrival time cannot be less than or equal to departure time. Please input a valid arrival time", icon="🚨")

departure = datetime.datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M:%S")
arrival = datetime.datetime.strptime(f"{arr_date} {arr_time}", "%Y-%m-%d %H:%M:%S")

tot_min = np.log((arrival - departure).total_seconds() / 60)


col5, col6 =st.columns((1,1))
source = col5.selectbox("Select the Source", [x for x in source['Source'].tolist()])
destination = col6.selectbox("Select the Destination", [x for x in destination['Destination'].tolist()])
if source == destination:
    st.error("ERROR! Source and destination are the same", icon="🚨")

col7, col8 =st.columns((1,1))
stops = col7.selectbox("Select the number of stops", [x for x in range(0,5)])
airline = col8.selectbox("Select the Airline", [x for x in airline['Airline'].tolist()])

col_a, col_b, col_c = st.columns([3,3,1])
col9,col10,col11 = st.columns([1,2,1])
if col_b.button('Get price'):
    result = predict_price(stops, mon, dep_hr, dep_min, tot_min, airline, source, destination, dow)
    col10.success("Approximate cost of the ticket is {}".format(result))