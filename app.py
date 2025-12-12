import streamlit as st
import plotly.express as px
from load_data import get_coordinates, get_forecast, get_gear_recommendations

st.set_page_config(page_title="SmartPack", page_icon="⛺", layout="centered")

st.title("⛺ SmartPack: Camping Forecast")
st.markdown("Enter a park name to see the forecast and generated gear checklist.")


# Location name input
park_name = st.text_input("Where are you camping?", value="Pinnacles National Park, CA")

if park_name:
    # Geocode park name
    lat, lon = get_coordinates(park_name)
    
    if lat and lon:
        st.caption(f"Found location: {lat:.2f}, {lon:.2f}")
        
        #Get Weather Data
        df = get_forecast(lat, lon)
        
        if df is not None:
           # Weathere metrics dashboard
            col1, col2, col3 = st.columns(3)
            with col1:
                min_temp = df['Temp (F)'].min()
                st.metric("Lowest Temp", f"{min_temp:.1f} °F")
            # with col2:
            #     max_wind = df['Wind (mph)'].max()
            #     st.metric("Max Wind", f"{int(max_wind):.1f} mph")
            with col2:
                max_wind = 6
                st.metric("Max Wind", f"{max_wind:.1f} mph")
            with col3:
                total_rain = df['Rain (3h)'].sum()
                st.metric("Total Rain", f"{total_rain:.1f} mm")

            
            # Gear recommendations dashboard 
            st.divider()
            gear, warnings = get_gear_recommendations(df)
            
            st.subheader("🎒 Smart Gear Checklist")
            
            # Display any warnings
            if warnings:
                for warn in warnings:
                    st.error(f"⚠️ {warn}")
            
            # Display gear list using  columns
            g_col1, g_col2 = st.columns(2)
            gear_list = list(gear)
            half = len(gear_list) // 2
            
            with g_col1:
                for item in gear_list[:half]:
                    st.success(item)
            with g_col2:
                for item in gear_list[half:]:
                    st.success(item)

           # Weather Graph dashboard
            st.divider()
            st.subheader("📅 Temperature & Wind Outlook")
            
            # Dual Axis Chart , plan to change once I find a better visual
            # ploty shows both wind and temp but I dont think it clear
            fig = px.line(df, x="Time of Day", y="Temp (F)", title="Temperature Trend")
            fig.add_bar(x=df["Time of Day"], y=df["Wind (mph)"], name="Wind (mph)")
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("Error fetching weather data.")
    else:
        st.error("Could not find that location. Try adding 'State' or 'National Park' to the name.")