from data_gathering import create_dataframe, get_games_today, get_nba_season_results, get_team_stats
import statsmodels.api as sm

DAYS_TO_INCLUDE = 150
TEAM_STATS = get_team_stats()


def main():
    res = ordinary_least_squares_model()
    print(f'Adjusted R-Squared Value: {round(res.rsquared_adj, 2)}\n')
    predict_game_scores(res)


def round_off_rating(number):
    return round(number * 2) / 2


def ordinary_least_squares_model():
    data = create_dataframe(get_nba_season_results(DAYS_TO_INCLUDE), True, TEAM_STATS)
    y = data['pts']
    x = data.loc[:, data.columns != 'pts']
    x = sm.add_constant(x)
    results = sm.OLS(y.astype(float), x.astype(float)).fit()
    return results


def predict_game_scores(model):
    games = get_games_today()
    for game in games:
        data = create_dataframe(game, False, TEAM_STATS)
        X = data
        X = sm.add_constant(X)
        X = X.to_numpy()
        ypred = model.predict(X.astype(float))
        print(f'{game["visitor"]}: {round(ypred[0], 2)}, {game["home"]} {round(ypred[1], 2)}')
        spread = ypred[0] - ypred[1]
        print(f'Spread: {game["home"]} {"+" if spread > 0 else ""}{round_off_rating(spread)}')
        print(f'Total Score: {round_off_rating(sum(ypred))}')
        print()

    print(f'Check Live Betting Lines: {"https://www.actionnetwork.com/nba/odds"}')
    print(f'Check NBA Injury Logs: {"https://www.espn.com/nba/injuries"}')


if __name__ == '__main__':
    main()
