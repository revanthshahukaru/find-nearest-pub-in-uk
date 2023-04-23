import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import math

df = pd.read_csv("data/clean_open_pubs.csv").reset_index()

# Create the sidebar with links to the different pages
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Pub Locations", "Find the nearest Pub"])

##############################################################
########################### PAGE 1 ###########################
##############################################################
if page == "Home":
    st.title("Open Pubs Dataset")

    st.write("This is a dataset of open pubs in the United Kingdom.")
    st.write(f"Number of rows: {df.shape[0]}")
    st.write(f"Number of columns: {df.shape[1]}")
    st.write("Top 10 local authorities with the most pubs:")
    local_authority_counts = df["local_authority"].value_counts()
    local_authority_counts_dict = dict(local_authority_counts)
    new_loc_authority_dict = dict(itertools.islice(local_authority_counts_dict.items(), 0,10))
    loc_authority_series = pd.Series(new_loc_authority_dict).plot.bar()
    st.pyplot(plt)
    st.write("Top 30 postal codes with the most pubs:")
    postcode_counts = df["postcode"].value_counts()
    postcode_counts_dict = dict(postcode_counts)
    new_postcode_dict = dict(itertools.islice(postcode_counts_dict.items(), 0,30))
    postcode_series = pd.Series(new_postcode_dict).plot.bar()
    st.pyplot(plt)

##############################################################
########################### PAGE 2 ###########################
##############################################################
elif page == "Pub Locations":

    st.title("Find Pubs in Your Area")
    st.write("Enter a postcode or local authority name to find all the pubs in the area.")

    def display_pubs_on_map(area_type, area_name):

        # Filter the dataframe based on the area_type and area_name
        if area_type == "Postcode":
            pubs_in_area = df[df["postcode"] == area_name].reset_index()
        elif area_type == "Local Authority":
            pubs_in_area = df[df["local_authority"] == area_name].reset_index()
        else:
            st.error("Invalid area type!")
            return "Invalid address."

        # Display the map
        st.map(pubs_in_area)
        st.header(f"{len(pubs_in_area)} open pubs found in the {area_type} - :red[{area_name}]")
        st.table(pubs_in_area)


    # Get the user"s choice of area type and area name
    area_type = st.radio(
        "Select an area type:",
        ["Postcode", "Local Authority"],
    )
    area_name = st.text_input(f"Enter the {area_type}:", "").strip()
    # Display the pubs on a map
    if area_name:
        display_pubs_on_map(area_type, area_name)

##############################################################
########################### PAGE 3 ###########################
##############################################################
else:
    st.title("Find the nearest Pub")
    st.write("Enter your Latitude and Longitude to find the nearest pubs.")

    R = 6371 # Approximate radius of the Earth in kilometers
    def euclidean_distance(lat1, lon1, lat2, lon2):
        """
        Calculates the Euclidean distance between two points on the Earth"s surface
        given their latitudes and longitudes using the formula:
        distance = R * sqrt((lat2-lat1)^2 + (cos((lat1+lat2)/2) * (lon2-lon1))^2)
        where R is the radius of the Earth (approx. 6371 km).
        """
        
        # Trigonometric functions like sine and cosine in Python"s math library expect their arguments
        # to be in radians, not degrees.
        # Therefore, we need to convert the degree values to radians before we can use these
        # trigonometric functions in our formula.
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        lat_diff = lat2 - lat1
        lon_diff = lon2 - lon1
        
        # atan2 allows us to specify both the numerator and denominator of 
        # the fraction whose arctangent we want to calculate
        a = math.sin(lat_diff / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(lon_diff / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance # units are kilometers.
    
    def find_nearest_pubs(lat, lon, n=5):
        df["distance"] = df.apply(lambda datapoint: euclidean_distance(lat, lon, datapoint["latitude"], datapoint["longitude"]), axis=1)
        nearest_pubs = df.sort_values(by="distance").head(n)
        return nearest_pubs
    
    # Get the user"s location
    lat = st.number_input(f"Enter the latitude:")
    lon = st.number_input(f"Enter the longitude:")

    nearest_pubs = find_nearest_pubs(lat,lon).reset_index()

    if lat and lon:
        st.header(f":blue[{len(nearest_pubs)}] open pubs found near {lat, lon}")
        st.table(nearest_pubs)

