import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import calendar
import pandas as pd


MONTHS = ['october', 'november', 'december', 'january', 'february', 'march', 'april']
TODAY = date.today()
ABBREVIATIONS_FILE = 'nba_teams.text'


def get_nba_season_results(days: int) -> list[dict]:
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
                    if TODAY > game_date > TODAY - timedelta(days=days):
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


def get_team_stats():
    teams = {}

    for team in get_basic_stats():
        teams[team['team']] = {'fg_pct': team['fg_pct'], 'fg3a': team['fg3a'], 'trb': team['trb'], 'ast': team['ast'],
                               'pts': team['pts'], 'stl': team['stl'], 'blk': team['blk']}

    for team in get_advanced_stats():
        stats = {'ortg': team['off_rtg'], 'drtg': team['def_rtg'], 'pace': team['pace'], 'ts_pct': team['ts_pct'],
                 'efg_pct': team['efg_pct'], 'tov_pct': team['tov_pct'],
                 'orb_pct': team['orb_pct'], 'ft_rate': team['ft_rate']}
        teams[team['team']].update(stats)

    return teams


def create_dataframe(games, train: bool, team_stats):
    team_results = []

    if train:
        for game in games:
            visitor_stats = {'pts': game['visitor_points'], 'home': 0, 'OT': game['OT'],
                             'ortg': team_stats[game['visitor']]['ortg'],
                             'opp_drtg': team_stats[game['home']]['drtg'], 'pace': team_stats[game['visitor']]['pace'],
                             'opp_pace': team_stats[game['home']]['pace'],
                             'avg_pts': team_stats[game['visitor']]['pts'],
                             }
            home_stats = {'pts': game['home_points'], 'home': 1, 'OT': game['OT'],
                          'ortg': team_stats[game['home']]['ortg'],
                          'opp_drtg': team_stats[game['visitor']]['drtg'], 'pace': team_stats[game['home']]['pace'],
                          'opp_pace': team_stats[game['visitor']]['pace'], 'avg_pts': team_stats[game['home']]['pts'],
                          }
            team_results.append(visitor_stats)
            team_results.append(home_stats)
    else:
        visitor_stats = {'home': 0, 'OT': 0, 'ortg': team_stats[games['visitor']]['ortg'],
                         'opp_drtg': team_stats[games['home']]['drtg'], 'pace': team_stats[games['visitor']]['pace'],
                         'opp_pace': team_stats[games['home']]['pace'],'avg_pts': team_stats[games['visitor']]['pts'],
                         }
        home_stats = {'home': 1, 'OT': 0, 'ortg': team_stats[games['home']]['ortg'],
                      'opp_drtg': team_stats[games['visitor']]['drtg'], 'pace': team_stats[games['home']]['pace'],
                      'opp_pace': team_stats[games['visitor']]['pace'], 'avg_pts': team_stats[games['home']]['pts'],
                      }
        team_results.append(visitor_stats)
        team_results.append(home_stats)

    return pd.DataFrame.from_dict(team_results)
