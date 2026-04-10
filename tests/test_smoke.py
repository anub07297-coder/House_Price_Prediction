import pandas as pd

from house_price_prediction.data import split_features_target


def test_split_features_target():
    df = pd.DataFrame(
        {
            "LotArea": [8450, 9600],
            "OverallQual": [7, 6],
            "SalePrice": [208500, 181500],
        }
    )

    x, y = split_features_target(df, "SalePrice")

    assert "SalePrice" not in x.columns
    assert y.name == "SalePrice"
    assert len(x) == len(y) == 2
