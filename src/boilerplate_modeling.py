class CustomKFold:
    def __init__(self, n_splits=5):
        self.n_splits = n_splits

    def split(self, df, y, groups=None):
        from sklearn.model_selection import StratifiedKFold

        sk = StratifiedKFold(random_state=666, n_splits=self.n_splits, shuffle=True)

        train_all = df[df['year'] < 2019]

        for train_idx, valid_idx in sk.split(np.zeros(train_all.shape[0]), train_all['year']):
            print(train_idx[0], valid_idx[0])
            yield (train_idx, valid_idx)

    def get_n_splits(self, X, y, groups=None):
        return self.n_splits

