"""
Script that draws 4 graphs:
    1. Graph of average f1 score for each machine learning method (if name of the method ends with 'normalized',
        it means that data was normalized before learning).
    2. Graph of average f1 score for each window size for each machine learning method.
    3. Graph of average f1 score for each component for each machine learning method (component 'B200_subset' has just
        sensors: ['7', '9', '11', '12', '31', '34', '39', '52', '56', '58', '66', '67', '73', '74', '75']).
    4. Graph of average f1 score for each number of clusters for each machine learning method.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

input_location = '../../results/'
input_data = ['results_stream.csv', 'results_stream_normalized.csv', 'results_batch.csv', 'results_batch_normalized.csv']


# function that creates column combining columns 'model' and 'normalized'
def combine(row):
    if row['normalized'] == 1:
        return row.model + '_normalized'
    else:
        return row.model


# plot of average f1 for each value of parameter x_name for each machine learning method
def create_figure(x_name):
    grouped = data.groupby(['model_normalized', x_name]).mean()
    grouped = grouped.reset_index()

    graphs = []
    for model in grouped.model_normalized.unique():
        a = grouped[grouped.model_normalized == model]
        graphs.append(go.Bar(name=model, x=a[x_name], y=a['f1']))

    fig = go.Figure(data=graphs)
    fig.update_layout(barmode='group')
    fig.write_html("../../results/model_{}_avg_f1.html".format(x_name))

# read data from csv
data = pd.read_csv(input_location + input_data[0], index_col=0)
for file in input_data[1:]:
    tmp = pd.read_csv(input_location + file, index_col=0)
    data = data.append(tmp, ignore_index=True)

data['model_normalized'] = data.apply(combine, axis='columns')

# plot of average f1 for each machine learning method
fig = px.bar(data.groupby(by=['model_normalized']).mean(), y='f1')
fig.write_html("../../results/model_avg_f1.html")


# plot of average f1 for each window for each machine learning method
grouped = data.groupby(['model_normalized', 'window']).mean()
grouped = grouped.reset_index()

graphs = []
for model in grouped.model_normalized.unique():
    a = grouped[grouped.model_normalized == model]
    graphs.append(go.Bar(name=model, x=['window=5', 'window=10', 'window=20', 'window=50', 'window=100'], y=a['f1']))

fig = go.Figure(data=graphs)
fig.update_layout(barmode='group')
fig.write_html("../../results/model_window_avg_f1.html")


create_figure('name')
create_figure('clusters')
