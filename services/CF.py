# -*- coding: utf-8 -*-
"""collaborativeFilter.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pDwX9xkbDOHjMWLMUWKGURyxME3F49w8

# Ví dụ Collaborative Filtering
"""
from pymongo import MongoClient

# from google.colab import drive
# drive.mount('/content/drive')
#
# pip install pymongo pandas

"""Đây là đoạn code mà tôi implement bằng phương pháp Lọc Cộng Tác (Collaborative Filtering) bằng 2 phương pháp:  

- Lọc Cộng Tác dựa trên Người dùng (User-User Collaborative Filtering)
- Lọc Cộng Tác theo Mục (Item-Item Collaborative Filtering)
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse


class CF(object):
    def __init__(self, Y_data, k, dist_func=cosine_similarity, CF=1):
        self.CF = CF  # 1 for user-user, 0 for item-item
        self.Y_data = Y_data if CF else Y_data[:, [1, 0, 2]]
        self.k = k  # Number of neigh
        self.dist_func = dist_func
        self.Ybar_data = None

        # Mapping user and item IDs to numerical indices
        self.user_id_to_index = {user_id: i for i, user_id in enumerate(np.unique(self.Y_data[:, 0]))}
        self.item_id_to_index = {item_id: i for i, item_id in enumerate(np.unique(self.Y_data[:, 1]))}

        # Create a numerical version of Y_data
        self.Y_data = self.map_data_to_indices()

        # Number of users and items. Remember to add 1 since id starts from 0
        if self.CF == 1:
            self.n_users = int(np.max(self.Y_data[:, 0])) + 1
            self.n_items = int(np.max(self.Y_data[:, 1])) + 1
        else:
            self.n_users = int(np.max(self.Y_data[:, 1])) + 1
            self.n_items = int(np.max(self.Y_data[:, 0])) + 1

    def map_data_to_indices(self):
        indices = np.array(
            [[self.user_id_to_index[user_id], self.item_id_to_index[item_id], rating] for user_id, item_id, rating in
             self.Y_data])
        return indices

    def convert_recommendations(self, recommendations):
        converted_recommendations = {}

        for user_index, item_indices in recommendations.items():
            user_id = next((user_id for user_id, index in self.user_id_to_index.items() if index == user_index), None)

            if user_id is not None:
                converted_item_ids = [
                    next((item_id for item_id, index in self.item_id_to_index.items() if index == item_index), None) for
                    item_index in item_indices]
                converted_recommendations[user_id] = converted_item_ids

        return converted_recommendations

    def test_data(self):
        return self.n_users, self.n_items

    def add(self, new_data):
        self.Y_data = np.concatenate((self.Y_data, new_data), axis=0)

    def normalize_Y(self):
        """
        base variable could be users in the (user-user) or items in (item-item)
        """

        base = self.Y_data[:, 0]  # First col of the Y_data
        self.Ybar_data = self.Y_data.copy()
        # print(self.Ybar_data)
        self.mean = np.zeros((self.n_users,))

        if (self.CF == 0):
            self.mean = np.zeros((self.n_items,))

        for n in range(self.mean.shape[0]):
            # print(np.where(users == n))
            ids = np.where(base == n)[0].astype(np.int32)
            # print(ids)
            item_or_users_ids = self.Y_data[ids, 1]
            ratings = self.Y_data[ids, 2]

            m = np.mean(ratings)
            if np.isnan(m):
                m = 0  # to avoid empty array and nan value
            self.mean[n] = m
            self.Ybar_data[ids, 2] = ratings - self.mean[n]

        ################################################
        # form the rating matrix as a sparse matrix. Sparsity is important
        # for both memory and computing efficiency. For example, if #user = 1M,
        # #item = 100k, then shape of the rating matrix would be (100k, 1M),
        # you may not have enough memory to store this. Then, instead, we store
        # nonzeros only, and, of course, their locations.
        if (self.CF == 1):
            self.Ybar = sparse.coo_matrix((self.Ybar_data[:, 2],
                                           (self.Ybar_data[:, 1], self.Ybar_data[:, 0])), (self.n_items, self.n_users))
        else:
            self.Ybar = sparse.coo_matrix((self.Ybar_data[:, 2],
                                           (self.Ybar_data[:, 1], self.Ybar_data[:, 0])), (self.n_users, self.n_items))

        self.Ybar = self.Ybar.tocsr()

    def similarity(self):
        # eps = 1e-6
        self.S = self.dist_func(self.Ybar.T, self.Ybar.T)

    def refresh(self):
        """
        Normalize data and calculate similarity matrix again
        (after some few ratings change)
        """
        self.normalize_Y()
        self.similarity()

    def fit(self):
        self.refresh()

    def __pred(self, u, i, normalized=1):
        """
        Predict the rating of user u for item i (normalized)
        if you need the un
        """

        # Step 1: Find all users who rated i
        ids = np.where(self.Y_data[:, 1] == i)[0].astype(np.int32)

        # Step 2:
        users_rated_i = (self.Y_data[ids, 0]).astype(np.int32)

        # Step 3: Find similarity between the current user and others
        # who already rated_i
        sim = self.S[u, users_rated_i]
        # print(self.S)
        # Step 4: Find the k most similarity users
        a = np.argsort(sim)[-self.k:]
        nearest_s = sim[a]

        # How did each of 'near' users rated item i
        r = self.Ybar[i, users_rated_i[a]]
        if normalized:
            return (r * nearest_s)[0] / (np.abs(nearest_s).sum() + 1e-8)

        return (r * nearest_s)[0] / (np.abs(nearest_s).sum() + 1e-8) + self.mean[u]

    def pred(self, u, i, normalized=1):
        return self.__pred(u, i, normalized)

    def recommend(self, u):
        ids = np.where(self.Y_data[:, 0] == u)[0]
        items_rated_by_u = self.Y_data[ids, 1].tolist()
        recommended_items = []

        if (self.CF):
            for i in range(self.n_items):
                if i not in items_rated_by_u:
                    rating = self.pred(u, i)
                    if rating > 0:
                        recommended_items.append(i)
        else:
            for i in range(self.n_users):
                if i not in items_rated_by_u:
                    rating = self.pred(u, i)
                    if rating > 0:
                        recommended_items.append(i)

        return recommended_items

    def show_recommendation(self):
        recommendations = {}

        if self.CF:
            for u in range(self.n_users):
                recommended_items = self.recommend(u)
                recommendations[u] = recommended_items
        else:
            for i in range(self.n_items):
                recommended_users = self.recommend(i)
                recommendations[i] = recommended_users

        return recommendations


"""## Import data from mongoDB in ratings collection"""


def get_data():
    # Connect to MongoDB
    client = MongoClient('mongodb+srv://swpts:280301@cluster0.vumst6j.mongodb.net/?retryWrites=true&w=majority')
    db = client['test']
    collection = db['ratings']

    # Fetch data from MongoDB collection
    data = list(collection.find())

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Specify the path where you want to save the CSV file
    csv_path = 'data/ratings.csv'

    # Save DataFrame to CSV
    df.to_csv(csv_path, index=False)

    return f'Data exported to {csv_path}'


def show_data():
    # Specify the path to your CSV file
    csv_path = 'data/ratings.csv'

    # Read CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Display the DataFrame
    return df


"""## Use example data in test/data"""


def rec_with_ratings():
    r_cols = ['user', 'product', 'rating']
    df = pd.read_csv('src/data/fake_data.csv', encoding='latin-1')
    ratings = df[r_cols]
    Y_data = ratings.to_numpy()

    # Lọc Cộng Tác dựa trên Người dùng (User-User Collaborative Filtering)
    rs = CF(Y_data, k=2, CF=1)
    rs.fit()

    result = []
    print(f"Singularity matrix is: \n{rs.S}")
    recommendations = rs.show_recommendation()
    result.append(rs.convert_recommendations(recommendations))

    rs_2 = CF(Y_data, k=2, CF=0)
    rs_2.fit()

    print(f"Singularity matrix is: \n{rs_2.S}")
    result.append(rs_2.show_recommendation())
    return result


def rec_with_test():
    r_cols = ['user_id', 'item_id', 'rating']
    ratings = pd.read_csv('src/data/ex.dat', sep=' ', names=r_cols, encoding='latin-1')
    Y_data = ratings.to_numpy()

    # Lọc Cộng Tác dựa trên Người dùng (User-User Collaborative Filtering)
    rs = CF(Y_data, k=2, CF=1)
    rs.fit()

    result = []
    print(f"Singularity matrix is: \n{rs.S}")
    result.append(rs.show_recommendation())

    rs_2 = CF(Y_data, k=2, CF=0)
    rs_2.fit()

    print(f"Singularity matrix is: \n{rs_2.S}")
    result.append(rs_2.show_recommendation())
    return result


"""## With MovieLens 100k dataset

[Bộ dataset MovieLens 100k](https://grouplens.org/datasets/movielens/100k/) được công bố bởi GroupLens vào tháng 4/1998. MovieLens gồm có 100,000 *ratings* từ 943 *users* cho 1682 bộ phim (có dung lượng là 5MB)
"""


def rec_with_data_movie(type):
    r_cols = ['user_id', 'movie_id', 'rating', 'unix_timestamp']

    ratings_base = pd.read_csv('test_data/ub.base', sep='\t', names=r_cols, encoding='latin-1')
    ratings_test = pd.read_csv('test_data/ub.test', sep='\t', names=r_cols, encoding='latin-1')

    rate_train = ratings_base.to_numpy()
    rate_test = ratings_test.to_numpy()

    # indices start from 0
    rate_train[:, :2] -= 1
    rate_test[:, :2] -= 1

    ratings_base.head()

    len(np.unique(ratings_base['user_id']))

    ratings_test.head()

    np.unique(ratings_base['movie_id'])

    if type == 1:
        """**Sử dụng Lọc Cộng tác theo Người dùng (User-User Collaborative Filtering)**"""
        rs = CF(rate_train, k=30, CF=1)
        rs.fit()

        n_tests = rate_test.shape[0]
        SE = 0  # squared error
        for n in range(n_tests):
            pred = rs.pred(rate_test[n, 0], rate_test[n, 1], normalized=0)
            SE += (pred - rate_test[n, 2]) ** 2

        RMSE = np.sqrt(SE / n_tests)
        print('User-user CF, RMSE =', RMSE)
    else:
        """**Sử dụng Lọc Cộng tác theo Mục (Item-Item Collaborative Filtering)**"""

        rs = CF(rate_train, k=30, CF=0)
        rs.fit()

        n_tests = rate_test.shape[0]
        SE = 0  # squared error
        for n in range(n_tests):
            pred = rs.pred(rate_test[n, 1], rate_test[n, 0], normalized=0)
            SE += (pred - rate_test[n, 2]) ** 2

        RMSE = np.sqrt(SE / n_tests)
        print('Item-item CF, RMSE =', RMSE)
