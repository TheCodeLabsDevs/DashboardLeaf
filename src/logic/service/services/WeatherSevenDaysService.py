import locale
from datetime import datetime
from typing import Dict

import requests
import plotly.graph_objects as go
from TheCodeLabs_BaseUtils import CachedService


class WeatherSevenDaysService(CachedService):
    URL = 'https://api.openweathermap.org/data/2.5/onecall'

    def __init__(self, settings):
        super().__init__(settings['fetchIntervalInSeconds'])
        self._settings = settings

    def _fetch_data(self) -> Dict:
        response = requests.get(self.URL, params={
            'lat': self._settings['lat'],
            'lon': self._settings['lon'],
            'appid': self._settings['apiKey'],
            'lang': 'de',
            'units': 'metric'
        })

        if response.status_code != 200:
            raise Exception(f'Invalid status code: {response.status_code}')

        # TODO less invasive modification
        locale.setlocale(locale.LC_ALL, 'de_DE')

        forecast = response.json()['daily']

        forecastData = {}
        for day in forecast:
            date = day['dt']
            date = datetime.fromtimestamp(date)
            date = datetime.strftime(date, '%a')
            forecastData[date] = (int(day['temp']['min']), int(day['temp']['max']))

        formattedDates = [f'<b>{value}</b>' for value in forecastData.keys()]
        minValues = [x[0] for x in forecastData.values()]
        maxValues = [x[1] for x in forecastData.values()]

        layout = go.Layout(
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis={
                'tickfont': {
                    'family': ' sans-serif',
                    'size': 18
                },
                'showgrid': False,
            },
            yaxis={
                'visible': False,
            })

        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(x=formattedDates,
                                 y=minValues,
                                 text=[f'<b>{value}</b>' for value in minValues],
                                 mode='lines+text',
                                 line=dict(color='#CCCCCC'),
                                 textfont=dict(
                                     family='sans-serif',
                                     size=18,
                                     color='royalblue'
                                 )))
        fig.add_trace(go.Scatter(x=formattedDates,
                                 y=maxValues,
                                 text=[f'<b>{value}</b>' for value in maxValues],
                                 mode='lines+text',
                                 line=dict(color='#CCCCCC'),
                                 textfont=dict(
                                     family='sans-serif',
                                     size=18,
                                     color='crimson'
                                 )))

        fig.show()

        return {}


if __name__ == '__main__':
    ws = WeatherSevenDaysService({
        'fetchIntervalInSeconds': 10,
        'apiKey': '',
        'lat': 51.012825,
        'lon': 13.666365
    })

    data = ws.get_data()
