import requests


class TvmazeService(object):

    def __init__(self):
        self.base_url = 'http://api.tvmaze.com/'
        self.url_search = self.base_url + 'singlesearch/shows'
        self.url_serie = self.base_url + 'shows/'

    def _search(self, q):
        json = None
        url = self.url_search + '?q=' + q
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
        return json

    def schedule(self):
        COUNTRIES = ['US', 'EN', 'ES']
        url = self.base_url + 'schedule?country={country}'
        series = []
        for country in COUNTRIES:
            response = requests.get(url.format(country=country))
            series.append(response.json)
        return series

    def _next_episode(self, id):
        url = self.url_serie + str(id) + '?embed[]=nextepisode&embed[]=previousepisode'
        nextepisode = None
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            nextepisode = json
            embedded = json.get('_embedded', None)
            if embedded.get('nextepisode'):
                nextepisode.update({'next': embedded['nextepisode']})
            else:
                nextepisode.update({'error': 'We do not have episode information right now.'})
            nextepisode.update({'previous': embedded['previousepisode']})
        return nextepisode

    def next_episode(self, q):
        next_episode = self._search(q)
        if next_episode:
            next_episode = self._next_episode(next_episode['id'])
        return next_episode
