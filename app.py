from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/form',methods=['POST','GET'])
def form():
    if request.method == 'GET':
        return render_template('form.html')
    if request.method == 'POST':
        Ticker = request.form['Ticker']
        option = request.form['options']
        # Ticker = form_data['Ticker']
        return redirect(url_for('stock',**request.form))
@app.route('/stock',methods=['GET','POST'])
def stock():
    import requests
    import os
    # symb = input("TICKER:")
    import json
    from dotenv import load_dotenv
    from bokeh.embed import file_html
    from bokeh.resources import CDN
    import numpy as np
    from bokeh.layouts import gridplot
    from bokeh.plotting import figure, show
    from bokeh.models import ColumnDataSource
    import pandas as pd
    from bokeh.io import curdoc
    from bokeh.models import Select
    from bokeh.themes import Theme, built_in_themes

    if request.method == 'GET':
        load_dotenv()
        API = os.getenv('API')
        Ticker = request.args.get('Ticker')
        option = request.args.get('options')
        # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='+Ticker+'&interval=5min&apikey='+API
        r = requests.get(url)
        data = r.json()
        tick_data_py = json.loads(str(data).replace('\'','\"'))
        json_data = tick_data_py["Time Series (5min)"]
        dates = json_data.keys()
        ticker_dates = np.array(list(dates), dtype='M')
        ticker_values = []
        for date in dates:
            if option == "price":
                ticker_values.append(float(json_data[date]['1. open']))
            elif option == 'volume':
                ticker_values.append(int(json_data[date]['5. volume']))

        ticker_data = dict(date = ticker_dates, values=ticker_values)
        ticker_data = pd.DataFrame(ticker_data)
        source = ColumnDataSource(data=ticker_data)

        p2 = figure(x_axis_type="datetime", title="Recent " +Ticker+" Open Prices")
        p2.sizing_mode = 'scale_width'
        p2.grid.grid_line_alpha = 0
        p2.xaxis.axis_label = 'Date'
        p2.yaxis.axis_label = option.capitalize()

        p2.line(x="date", y="values", legend_label='open',
                   color='white', alpha=0.2,source=source)
        curdoc().theme = 'contrast'
        html = file_html(p2, CDN,Ticker+" stock", theme=built_in_themes['contrast'])

        return html
    else:
        return redirect(url_for('form'))


if __name__ == '__main__':
  app.run(port=33508)
