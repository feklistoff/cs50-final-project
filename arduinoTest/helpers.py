# for plotting data
import plotly
import plotly.graph_objs

# offline plot
# https://plot.ly/python/bar-charts/
def bar(xdata, ydata, key):
    # return a bar chart as HTML
    if key == "temperature":
        title = "Temperature, *C"
        color = dict(color='rgb(238,110,96)')
    if key == "humidity":
        color = dict(color='rgb(24,158,223)')
        title = "Humidity, %"

    trace = plotly.graph_objs.Bar(
                x=xdata,
                y=ydata,
                marker=color,
            )
    layout = plotly.graph_objs.Layout(
        title="DHT-11 sensor data",
        yaxis=dict(
            title=title,
            ),
        showlegend=False,
        hovermode=True
    )

    barchart = {
        "data": [trace],
        "layout": layout
    }

    return plotly.offline.plot(barchart, output_type="div", show_link=False, link_text=False)
