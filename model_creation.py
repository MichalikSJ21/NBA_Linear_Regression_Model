from data_gathering import create_test_dataframe
import statsmodels.api as sm


def main():
    res = ordinary_least_squares_model()
    print(res.summary())


def ordinary_least_squares_model():
    data = create_test_dataframe()
    y = data['pts']
    x = data.loc[:, data.columns != 'pts']
    x = sm.add_constant(x)
    results = sm.OLS(y.astype(float), x.astype(float)).fit()
    return results


if __name__ == '__main__':
    main()
