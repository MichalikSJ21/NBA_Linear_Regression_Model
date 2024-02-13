import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import calendar


MONTHS = ['october', 'november', 'december', 'january', 'february', 'march', 'april']
TODAY = date.today()
ABBREVIATIONS_FILE = 'nba_teams.text'


def get_nba_season_results() -> list[dict]:
    games = []
    for month in MONTHS:
        url = f'https://www.basketball-reference.com/leagues/NBA_2024_games-{month}.html'
        soup = _extract_soup(url)
        results = soup.find(id="schedule").find("tbody").find_all("tr")
        for row in results:
            game = {'visitor': None, 'visitor_points': None,
                    'home': None, 'home_points': None, 'date': None, 'OT': 0}
            for td in row:
                if td['data-stat'] == 'visitor_team_name': game['visitor'] = td.text
                if td['data-stat'] == 'visitor_pts': game['visitor_points'] = td.text
                if td['data-stat'] == 'home_team_name': game['home'] = td.text
                if td['data-stat'] == 'home_pts': game['home_points'] = td.text
                if td['data-stat'] == 'overtimes' and td.text == 'OT': game['OT'] = 1
                if td['data-stat'] == 'date_game':
                    game_date = datetime.strptime(td.text, '%a, %b %d, %Y').date()
                    if game_date < TODAY:
                        game['date'] = game_date
                        games.append(game)
    return games


def get_nba_abbreviations():
    names = []
    with open(ABBREVIATIONS_FILE, 'r') as team_names:
        for line in team_names:
            team = {}
            words = line.split(',')
            team['abbreviation'] = words[0].strip()
            team['name'] = words[1].strip()
            names.append(team)
    return names


def get_advanced_stats():
    url = 'https://www.basketball-reference.com/leagues/NBA_2024.html'
    soup = _extract_soup(url)
    results = soup.find(id="advanced-team").find("tbody").find_all("tr")
    teams = []
    for row in results:
        team = {}
        for td in row:
            team[td['data-stat']] = td.text
        teams.append(team)
    return teams


def get_basic_stats():
    url = 'https://www.basketball-reference.com/leagues/NBA_2024.html'
    soup = _extract_soup(url)
    results = soup.find(id="per_poss-team").find("tbody").find_all("tr")
    teams = []
    for row in results:
        team = {}
        for td in row:
            team[td['data-stat']] = td.text
        teams.append(team)
    return teams


def get_games_today():
    games = []
    month_name = calendar.month_name[TODAY.month].lower()
    url = f'https://www.basketball-reference.com/leagues/NBA_2024_games-{month_name}.html'

    soup = _extract_soup(url)
    results = soup.find(id="schedule").find("tbody").find_all("tr")
    for row in results:
        game = {'visitor': None, 'home': None}
        for td in row:
            if td['data-stat'] == 'visitor_team_name': game['visitor'] = td.text
            if td['data-stat'] == 'home_team_name': game['home'] = td.text
            if td['data-stat'] == 'date_game':
                game_date = datetime.strptime(td.text, '%a, %b %d, %Y').date()
                if game_date == TODAY: games.append(game)
    return games


def _extract_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


def main():
    all_game_results = get_nba_season_results()
    nba_abbreviations = get_nba_abbreviations()
    for game in get_games_today():
        print(game)


if __name__ == '__main__':
    main()
