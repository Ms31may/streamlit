import streamlit as st
import pandas as pd
import numpy as np
from authentication import session_handler
import plotly.express as px
import plotly.graph_objects as go
import time 

import streamlit as st
from PIL import Image
# st.set_page_config(layout="wide", page_title="Charging Behaviour", page_icon="🔋")
from firesql.firebase import FirebaseClient

client = FirebaseClient()
client.connect(credentials_json=r"secret.key.json")
from firesql.sql import FireSQL
from firesql.sql.sql_fire_client import FireSQLClient





###################################################################################################################


######################################################3##############################################


def df_to_plotly(df):
    return {'z': df.values.tolist(),
            'x': df.columns.tolist(),
            'y': df.index.tolist()}

@session_handler
def main():
        
        st.title("Customers Insight Regarding the charging")
        st.write(
                """
                Here We will find out User start charging from what per to what percent
                """
        )
        



        fireSQL = FireSQL()
        sqlClient = FireSQLClient(client)

        sql1 = """
        SELECT *
        FROM
        events/Charging/events
        """

        selectDocs = fireSQL.execute(sqlClient, sql1)
        df = pd.DataFrame(selectDocs)

        # df.loc[(df["Customer City"].isnull() == True), "Customer City"] = "Pune"
        # df["start1"] = pd.to_datetime(df["start"]).dt.date


        st.title("Customers Behaviour Dashboard")
        # # city_filter = st.selectbox("Select the City", pd.unique(df["Customer City"]))
        # option = st.radio("Cities", ["all", "Select"])
        # if option == "Select":
        #         options = st.multiselect(
        #                 "Select the City", pd.unique(df["Customer City"]), ["Pune"])
        # else:
        #         options = pd.unique(df["Customer City"])



        col1, col2 = st.columns(2)

        # In the first column, add the Start Date input
        with col1:
                start_date = st.date_input(
                "Start Date", value=pd.to_datetime("2021-01-01", format="%Y-%m-%d")
                )

        # In the second column, add the End Date input
        with col2:
                end_date = st.date_input(
                "End Date", value=pd.to_datetime("today", format="%Y-%m-%d")
                )

        # st.write('You selected:', options)
        begin = start_date.strftime("%Y-%m-%d")
        begin = begin + "T00:00:00"
        end = end_date.strftime("%Y-%m-%d")
        end = end + "T23:59:59"
        # st.write(begin)

        # df = df[df["Customer City"].isin(options)]
        st.write(type(start_date))
        df["start1"] = pd.to_datetime(df["start"]).dt.date
        labels=['0-10', '10-20', '20-30', '30-40', '40-50','50-60','60-70','70-80','80-90','90-100']
        df = df[(df["start1"] >= start_date) & (df["start1"] <= end_date)]
        if len(df)> 0:
                df['SOC_IN'] = pd.cut(df['soc'], bins=[0, 10, 20, 30, 40, 50,60,70,80,90,100], labels=['0-10', '10-20', '20-30', '30-40', '40-50','50-60','60-70','70-80','80-90','90-100'])
                df['SOC_OUT'] = pd.Categorical(pd.cut(df['nsoc'], bins=[0, 10, 20, 30, 40, 50,60,70,80,90,100], labels=['0-10', '10-20', '20-30', '30-40', '40-50','50-60','60-70','70-80','80-90','90-100']), categories=labels[::-1], ordered=True)

                # Create pivot table
                df['s'] = 1
                charging = df[df['eventType'] == "Charging"]
                pivot = pd.pivot_table(
                                charging,
                                values="s",
                                index=["SOC_OUT"],
                                columns=["SOC_IN"],
                                aggfunc=np.sum,
                                margins=True,
                                )
                pivot = ((pivot / pivot.iloc[-1, -1]) * 100).round(2)
                pivot[pivot.isnull() == True] = 0
                pivot.index.names = ["SOC_OUT"]
                pivot.columns.names = ["SOC_IN"]
                # pivot = pivot.iloc[:-1, :-1] # Remove total row and column
                pivot = pivot.reindex(index=["All"] + list(pivot.index[:-1]))

                # Create heatmap using Plotly
                # fig1.update_traces(texttemplate='%{text:}%')
                fig1 = px.imshow(pivot, color_continuous_scale="Blues",text_auto=True)
                # fig1.update_traces(texttemplate='%{text:}%')

                fig1.update_layout(
                title="SOC_IN vs. SOC_OUT",
                xaxis_title="SOC_IN",
                yaxis_title="SOC_OUT",
                width=1200,
                height=900
                )


                df["start"] = pd.to_datetime(df["start"]) + pd.Timedelta(hours=5, minutes=30)

                df["Hour"] = df["start"].astype("str").str[11:13].astype("int")
                bins = [0, 6, 12, 18, 23]
                label = ["0-6", "6-12", "12-18", "18-24"]
                df["ChargingTime"] = pd.cut(df["Hour"], bins, labels=label)
                # sns.countplot(df['ChargingTime'])

                gr = px.histogram(
                df,
                x="ChargingTime",
                barmode="group",
                category_orders=dict(ChargingTime=["0-6", "6-12", "12-18", "18-24"]),
                text_auto=True,
                )
                gr.update_layout(
                title="Charging Time",
                xaxis_title="Charging Time",
                yaxis_title="Count",
                font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
                )
##################################################################3


# Create ChargeIn and ChargeOut categories
                
###################################################################33


                
                

                






                fig = go.Figure()

                days = sorted(df['Hour'].unique())

                fig.add_trace(go.Violin(x = df["eventType"][df["eventType"] == "Charging"],
                                        y=df['onboard_bms_temperature'],
                                        
                                        name="all",
                                        box_visible=True,
                                        meanline_visible=True))

                for day in days:
                        fig.add_trace(go.Violin(x=df['Hour'][df['Hour'] == day],
                                                y=df['onboard_bms_temperature'][df['Hour'] == day],
                                                name=day.astype('str'),
                                                box_visible=True,
                                                meanline_visible=True))
        # calculate average temperature value

                fig.update_layout(xaxis_title='Hours')
                fig.update_layout(yaxis_title='Temperature')
                fig.update_layout(title='Temperature Distribution by Hours')
                fig.update_layout(autosize=False,
                                width=1000,
                                height=500,
                                margin=dict(l=50, r=50, b=100, t=100, pad=4),
                                paper_bgcolor="LightSteelBlue",)
                

                # fig1 = go.Figure(data=go.Heatmap(df_to_plotly(x)))

                ######################################################################################
                st.markdown("### Cutomers Start Charging Time")
                
                st.plotly_chart(gr, use_container_width=True)


                st.markdown("### Cutomers Start Charging Time Table")


                st.plotly_chart(fig1, use_container_width=True)
                st.plotly_chart(fig, use_container_width=True)
                # st.plotly_chart(fig2, use_container_width=True)
                


                
        else:
                st.markdown("# No Data")

####################################################################################3

# Create heatmap trace
                