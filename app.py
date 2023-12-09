import streamlit_authenticator as stauth
import streamlit as st
import mysql.connector
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time

try:
    def connect_to_database():
        db_config = {
        'host' : st.secrets['db_con']['host_name'],
        'user' : st.secrets['db_con']['username'],
        'password' : st.secrets['db_con']['password'], 
        'database' : st.secrets['db_con']['db_name']
        }
        return mysql.connector.connect(**db_config)
except Exception as e:
    print(e)

try:
    def fetch_data_for_plot():
        db_connection = connect_to_database()
        cursor = db_connection.cursor()
        cursor.execute("""
                SELECT `Batch_IST`, `Channel_Name`, SUM(`Live_Views`) 
                FROM demo2 
                WHERE `Feed_date` = "5/11/2023" 
                GROUP BY `Batch_IST`, `Channel_Name`
                """)
        data = cursor.fetchall()

        # Structuring the data for DataFrame
        struc_data = [dict(zip(['Batch_IST', 'Channel_Name', 'Live_Views'], row)) for row in data]

        return struc_data
except Exception as e:
    print(e)


try:
    def fetch_data_for_creds():
        db_connection = connect_to_database()
        cursor = db_connection.cursor()
        cursor.execute('Select * from creds')
        data = cursor.fetchall()
        credentials = {"usernames": {x[1]: {'name': x[0], 'password': x[2], "channel_name": x[3]} for x in data}}
        return credentials
except Exception as e:
    print(e)



def mat_plot(pivot_sorted_data):
    colormap = plt.cm.tab10 if len(pivot_sorted_data.columns) <= 10 else plt.cm.tab20
    colors = [colormap(i) for i in range(len(pivot_sorted_data.columns))]

    # Plotting with the sorted data and unique colors for each channel
    plt.figure(figsize=(15, 8))  # Set the figure size to match the aspect of the provided screenshot

    # Plot each channel with a unique color
    for i, channel in enumerate(pivot_sorted_data.columns):
        plt.plot(pivot_sorted_data.index, pivot_sorted_data[channel], label=channel, color=colors[i])

    plt.title('Hindi Live News Feed')  # Title as per the screenshot
    plt.xlabel('Batch IST')  # X-axis label
    plt.ylabel('Live Views')  # Y-axis label
    plt.legend()  # Show the legend
    plt.grid(True)  # Show grid

    # Show the plot
    return plt

def plot_ly(pivot_sorted_data):
    # pivot_sorted_data = df.pivot(index='Batch_IST', columns='Channel_Name', values='Live_Views').fillna(0)

    # Convert the pivoted data back to a "long-form" DataFrame for use with Plotly
    plotly_data = pivot_sorted_data.reset_index().melt(id_vars='Batch_IST', var_name='Channel_Name', value_name='Live_Views')

    # Create the interactive line chart using Plotly Express
    fig = px.line(plotly_data, x='Batch_IST', y='Live_Views', color='Channel_Name',
                title='Hindi Live News Feed',
                labels={'BATCH_IST': 'Batch_IST', 'Live Views': 'Live_Views'})

    fig.update_layout(
            plot_bgcolor='white',  # Background color of the plot area
            paper_bgcolor='white',  # Background color of the paper or canvas
            xaxis=dict(showgrid=True, gridcolor='lightgray'),  # Show x-axis gridlines
            yaxis=dict(showgrid=True, gridcolor='lightgray'),  # Show y-axis gridlines
            margin=dict(l=10, r=10, t=40, b=10),  # Adjust margins to add an outline
            )
    for trace in fig.data:
        trace.update(textfont_color='black')
    fig.update_xaxes(tickfont=dict(color='black'))
    fig.update_yaxes(tickfont=dict(color='black'))
    fig.update_layout(legend_title=dict(font=dict(color='black')))  

    # Update legend text color
    fig.update_layout(legend=dict(font=dict(color='black'))) 
    
    # Show the figure
    return fig
    
# def plot_ly2(pivot_sorted_data):
#         colormap = plt.cm.tab10 if len(pivot_sorted_data.columns) <= 10 else plt.cm.tab20
#         colors = [colormap(i) for i in range(len(pivot_sorted_data.columns))]

#         # Plotting with the sorted data and unique colors for each channel
#         plt.figure(figsize=(7, 5))  # Set the figure size to match the aspect of the provided screenshot

#         # Plot each channel with a unique color
#         for i, channel in enumerate(pivot_sorted_data.columns):
#             plt.plot(pivot_sorted_data.index, pivot_sorted_data[channel], label=channel, color=colors[i])

#         plt.legend()  # Show the legend
#         plt.grid(True)  # Show grid
#         plotly_fig = mpl_to_plotly(plt.gcf(), resize=True)  # resize=True to fit Plotly's default layout

#         # Update the layout for a white background and visible text
#         plotly_fig.update_layout({
#             'plot_bgcolor': 'white',    # Set plot background to white
#             'paper_bgcolor': 'white',   # Set the "paper" background to white
#             'font': {
#                 'color': 'black'        # Ensure text is black for visibility
#             },
#             "title":'Hindi Live News Feed',
#             "xaxis_title":'Batch IST',
#             "yaxis_title":'Live Views',
#             "plot_bgcolor":'white',
#             'legend': {
#                 'bordercolor':'black',
#                 'borderwidth': 1
#             }
#         })

#         # Update axes properties if necessary
#         plotly_fig['layout']['xaxis'].update({
#             'showgrid': True,           # To show gridlines
#             'gridcolor': 'grey',        # Gridline color
#             'linecolor': 'black',       # Axis line color
#             'title': {
#                 'text': 'Batch IST',
#                 'font': {
#                     'color': 'black'    # X-axis title color
#                 }
#             }
#         })

#         plotly_fig['layout']['yaxis'].update({
#             'showgrid': True,           # To show gridlines
#             'gridcolor': 'grey',        # Gridline color
#             'linecolor': 'black',       # Axis line color
#             'title': {
#                 'text': 'Live Views',
#                 'font': {
#                     'color': 'black'    # Y-axis title color
#                 }
#             }
#         })
#         plotly_fig.update_xaxes(tickfont=dict(color='black'))
#         plotly_fig.update_yaxes(tickfont=dict(color='black'))

#         # Update legend text color
#         plotly_fig.update_layout(legend=dict(font=dict(color='black')))    
#         # Show the plot
#         return plotly_fig   

def plot_ly3(pivot_sorted_data, channel_name):
    fig = go.Figure()

    for channel in pivot_sorted_data.columns:
        if channel == channel_name:
            fig.add_trace(go.Scatter(x=pivot_sorted_data.index, y=pivot_sorted_data[channel], mode='lines', name=channel,
                                    line=dict(color='red', width=4, dash='dash')))
        else:
            fig.add_trace(go.Scatter(x=pivot_sorted_data.index, y=pivot_sorted_data[channel], mode='lines', name=channel))
    fig.update_layout(title='Hindi Live News Feed', xaxis_title='Batch IST', yaxis_title='Live Views')
    fig.update_layout(
            plot_bgcolor = 'white',    # Set plot background to white
            paper_bgcolor = 'white',   # Set the "paper" background to white
    xaxis=dict(
        titlefont=dict(
            color="black"  # Change to your preferred color
        ),
        tickfont=dict(
            color="black"  # Change to your preferred color
        )
    ),
    yaxis=dict(
        titlefont=dict(
            color="black"  # Change to your preferred color
        ),
        tickfont=dict(
            color="black"  # Change to your preferred color
        )
    )
)
    
    return fig


def plot_all(channel_name):
    st.title('Different Line Charts of Data from MySQL Database')

    # Fetch and display data
    if 'data_fetch_time' not in st.session_state or (time.time() - st.session_state.data_fetch_time) > 20:
        st.session_state.data = fetch_data_for_plot()
        st.session_state.data_fetch_time = time.time()

    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        pivot_sorted_data = df.pivot(index='Batch_IST', columns='Channel_Name', values='Live_Views').fillna(0)
        st.pyplot(mat_plot(pivot_sorted_data))
        st.plotly_chart(plot_ly(pivot_sorted_data))
        st.plotly_chart(plot_ly3(pivot_sorted_data, channel_name), use_container_width=True)
    else:
        st.write('Waiting for data...')
        
    


st.set_page_config(page_title="Demo Login Form", page_icon = ":computer:", layout='wide')

creds = fetch_data_for_creds()

authenticator = stauth.Authenticate(creds,"Demo_Login_Form", 'abcdef', 30)


name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status == False:
    st.error("USername/Password is incorrect!")

if authentication_status == None:
    st.warning("Please Enter Your Username and Password")

if authentication_status:
    st.sidebar.header(f"Welcome {name}")
    authenticator.logout("Logout", "sidebar")
    plot_all(creds['usernames'][username]['channel_name'])
    time.sleep(20)
    print("hello")
    st.rerun()
