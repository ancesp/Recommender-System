import pandas as pd
import numpy as np
from apyori import apriori
import pickle
from operator import itemgetter
import flask
import json

# load payslip data and product_list
product_data = pd.read_csv("payslips_ids_old.csv")
product_list = pd.read_csv("products_old.csv")


# get parameters for algorithm
df_shape = product_data.shape
n_of_transactions = df_shape[0]
n_of_products = df_shape[1]

records = []
for i in range(0, n_of_transactions):
    records.append([])
    for j in range(0, n_of_products):
        if (str(product_data.values[i, j]) != 'nan'):
            records[i].append(str(product_data.values[i, j]))

# print(records)

association_rules = apriori(
    records, min_support=0.001, min_confidence=0.0, min_lift=0, max_length=2)
association_results = list(association_rules)


# create lookup table for results
lookup_table = {}

for index, item in product_list.iterrows():
    lookup_table[item[0]] = []

for item in association_results:
    pair = item[0]
    items = [x for x in pair]

    if(len(items) == 1):
        to_print = "Rule: " + items[0]
    else:
        to_print = "Rule: " + \
            items[0] + " -> " + items[1]

    if(len(items) > 1):

        lookup_pair_1 = [items[1], item[2][0][2]]
        lookup_pair_2 = [items[0], item[2][0][2]]
        lookup_table[items[0]].append(lookup_pair_1)
        lookup_table[items[1]].append(lookup_pair_2)

    print(to_print)
    print("Support: " + str(item[1]))
    print("Confidence: " + str(item[2][0][2]))
    print("Lift: " + str(item[2][0][3]))
    print("=======================================")


# sort recommendations by confidence (higher to lower)
for key, item in lookup_table.items():
    item = sorted(item, key=itemgetter(1), reverse=True)
    lookup_table[key] = item


def getRecommendationsForProduct(product_id):
    recommended_products = []
    product_information = product_list.loc[product_list['product_id'] == int(
        product_id)]
    product_category = product_information['product_category']

    for item in lookup_table[int(product_id)]:

        item_information = product_list.loc[product_list['product_id'] == item[0]]
        item_category = item_information['product_category']

        if(item_category.to_string(
           index=False) == product_category.to_string(
                index=False)):
            recommended_products.append(item[0])

    recommendations = json.dumps(recommended_products)
    return recommendations


print(getRecommendationsForProduct(26))

# call from backend
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/recommendation', methods=['GET'])
def getRecommendations():
    product_id = flask.request.args.get('productId')
    recommendations_list = getRecommendationsForProduct(product_id)
    return recommendations_list


#app.run(host="0.0.0.0", port=1234)
