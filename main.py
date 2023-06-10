from flask import Flask, jsonify, request
import numpy as np
import pandas as pd
import tensorflow as tf
import json
from dotenv import load_dotenv
import psycopg2
import geopy.distance

load_dotenv()

app=Flask(__name__)

#Database connection 
# conn = psycopg2.connect(database=os.getenv("DB_DATABASE"), 
#                         user=os.getenv("DB_USERNAME"),
#                         password=os.getenv("DB_PASSWORD"), 
#                         host=os.getenv("DB_HOST"), 
#                         port="5432")

# conn = psycopg2.connect(database="agroconnect_db_prod", user="postgres", password="agroconnect", host="34.128.87.179", port="5432")

# query for database
# cur.execute()

# commit the changes
# conn.commit()

# close the cursor and connection
# cur.close()
# conn.close()
def nearestCluster(centroids, coor_supp):
    N, M = centroids.shape
    lst_coor = np.zeros(N)
    for i, data in enumerate(centroids):
      lst_coor[i] = geopy.distance.geodesic(data, coor_supp).km
    sorted_indices = np.argsort(lst_coor)  # Sort the indices based on distances
    # top_clusters = sorted_indices[:k]  # Get the top k closest clusters
    return (np.argmin(lst_coor), min(lst_coor),list(sorted_indices))    

    pass
def predict_location(clusters_n, iteration_n, array_location):
    points = tf.constant(array_location)
    centroids = tf.constant(tf.slice(tf.compat.v1.random_shuffle(points), [0, 0], [clusters_n, -1]))
    points_expanded = tf.expand_dims(points, 0)

    def update_centroids(points_expanded, centroids):
        centroids_expanded = tf.expand_dims(centroids, 1)
        distances = tf.reduce_sum(tf.square(tf.subtract(points_expanded, centroids_expanded)), 2)
        assignments = tf.argmin(distances, 0)
        means = []
        for c in range(clusters_n):
            ruc = tf.reshape(tf.where(tf.equal(assignments, c)), [1,-1])
            ruc = tf.gather(points, ruc)
            ruc = tf.reduce_mean(ruc, axis=[1])
            means.append(ruc)
        new_centroids = tf.concat(means, 0)
        return new_centroids, assignments

    for _ in range(iteration_n):
        centroids, assignments = update_centroids(points_expanded, centroids)

    def predict(point, centroids):
        point_expanded = tf.expand_dims(point, 0)
        centroids_expanded = tf.expand_dims(centroids, 1)
    
        distances = tf.reduce_sum(tf.square(tf.subtract(point_expanded, centroids_expanded)), 2)
        assignment = tf.argmin(distances, 0)
    
        return assignment
    
    lst_centroid = []
    for i, point in enumerate(array_location):
        lst_centroid.append(predict(point, centroids).numpy()[0])
    return centroids, lst_centroid

def get_commodity_score(farmer_data, supplier_data):
    farmer_size,_ = farmer_data.shape
    supplier_size,_ = supplier_data.shape
    max_value_farm = max(farmer_data.max(numeric_only=True))
    max_value_sup = np.max(supplier_data)

    if max_value_farm > max_value_sup:
        norm_scale = max_value_farm
    else:
        norm_scale = max_value_sup

    commodity_score = np.zeros((farmer_size,supplier_size, 6))
    for farmer_index, farmer_row in farmer_data.iterrows():
        for supplier_index, supplier_row in enumerate(supplier_data):
            for commodity_col in range(1, 7): 
                supplier_amount = supplier_row[commodity_col-1]
                farmer_amount = farmer_row[f'Commodity_{commodity_col}'] 
                if (farmer_amount >= supplier_amount) and (farmer_amount != 0) and (supplier_amount != 0):
                    score = 1 - (farmer_amount - supplier_amount)/norm_scale
                    commodity_score[farmer_index][supplier_index][commodity_col - 1] = abs(score)        
                elif (farmer_amount < supplier_amount) and (farmer_amount != 0) and (supplier_amount != 0):
                    score = (supplier_amount - farmer_amount)/norm_scale
                    commodity_score[farmer_index][supplier_index][commodity_col - 1] = abs(score)            
                else:
                    commodity_score[farmer_index][supplier_index][commodity_col - 1] = 0
    return np.mean(commodity_score,axis=-1), farmer_size


@app.route("/")
def index():
    return "Welcome to AgroConnect ML API"

@app.route("/products")
def get_all_products():
    try:
        #connection to db
        conn = psycopg2.connect(database="agroconnect_db_prod", 
                                user="postgres", 
                                password="agroconnect", 
                                host="34.128.87.179", 
                                port="5432")

        #create a cursor 
        cur = conn.cursor()

        # Qeury Selcet all from table public.products 
        cur.execute('''SELECT id, "name", amount, "location", crop_date, estimate_exp, category_id, user_id, "createdAt", "updatedAt"
                        FROM public."Products"''')

        # Fetch all data 
        data = cur.fetchall()

        # close sursor and connection 
        cur.close()
        conn.close()

        return data

    except psycopg2.Error as e:
        print("Connection failed to database: ", e)
        return

@app.route("/farmer")
def get_data_farmer():
    try:
        conn = psycopg2.connect(database="agroconnect_db_prod", 
                                user="postgres", 
                                password="agroconnect", 
                                host="34.128.87.179", 
                                port="5432")

        #create a cursor 
        cur = conn.cursor()

        #  Query SQL to Join Data from table Users, Category, and Products
        query = """
        SELECT u.username AS "Name",
            SPLIT_PART(p.location, ',', 1) AS "Lat",
            SPLIT_PART(p.location, ',', 2) AS "Long",
            SUM(CASE WHEN c.id = 7 THEN p.amount ELSE 0 END) AS "Commodity_1",
            SUM(CASE WHEN c.id = 8 THEN p.amount ELSE 0 END) AS "Commodity_2",
            SUM(CASE WHEN c.id = 9 THEN p.amount ELSE 0 END) AS "Commodity_3",
            SUM(CASE WHEN c.id = 10 THEN p.amount ELSE 0 END) AS "Commodity_4",
            SUM(CASE WHEN c.id = 5 THEN p.amount ELSE 0 END) AS "Commodity_5",
            SUM(CASE WHEN c.id = 6 THEN p.amount ELSE 0 END) AS "Commodity_6"
        FROM public."Products" p
        JOIN public."Users" u ON u.id = p.user_id
        JOIN public."Categories" c ON c.id = p.category_id
        GROUP BY u.username, p.location
        """

        # Execute Qeury Selcet all from table public.products 
        cur.execute(query)

        # Fetch all data 
        rows = cur.fetchall()

        # Coloumn names 
        column_names = ["Name", "Lat", "Long", "Commodity_1", "Commodity_2", "Commodity_3", "Commodity_4", "Commodity_5", "Commodity_6", "Date_Posted"]

        # Respon Table 

        # # Create a string to hold the table data
        # table_str = ""

        # # Append column names to the table string
        # table_str += "\t".join(column_names) + "\n"

        # # Append each data row to the table string
        # for row in rows:
        #     formatted_row = "\t".join(str(value) for value in row)
        #     table_str += formatted_row + "\n"

        # Respons JSON 

        data = []

        # Iterate over the rows and create dictionaries for each row
        for row in rows:
            data_row = {column_names[i]: str(value) for i, value in enumerate(row)}
            data.append(data_row)

        # Convert the data to JSON
        json_data = json.dumps(data)

        # Close the cursor and connection
        cur.close()
        conn.close()

        # return table_str
        return json_data

    except Exception as e: 
        print("Connection failed to database:", e)
        return str(e)

@app.route("/getScore", methods=['GET'])
def get_score():
    try:
        args = request.args.getlist('supplier_data')
        supplier_location = np.array(args[1:3]).reshape(1,2).astype(float)
        supplier_data = np.array(args[3:]).reshape(1,6).astype(int)
        farmer_data = pd.read_json(get_data_farmer())
        final_commodity_score,farmer_size = get_commodity_score(farmer_data, supplier_data)
        # print(farmer_data)
        # print(final_commodity_score)
        #define the variable needed for the location prediction
        array_location = farmer_data[['Lat','Long']].values.tolist()

        clusters_n = int(np.sqrt(farmer_size/2))
        iteration_n = 100
        centroids, lst_centroid = predict_location(clusters_n, iteration_n, array_location)

        #add the cluster and score to the dataframe
        labeled_farmer_data = farmer_data.copy()
        labeled_farmer_data['Cluster'] = lst_centroid
        labeled_farmer_data['Score'] = final_commodity_score
        # print(labeled_farmer_data.to_json(orient='records'))
        nearest_cluster, nearest_distance, top_cluster = nearestCluster(np.array(centroids),supplier_location)
        print(nearest_cluster, nearest_distance, top_cluster)


        labeled_farmer_data['Location_rank'] = labeled_farmer_data['Cluster'].apply(lambda cluster: top_cluster.index(cluster) + 1)
        labeled_farmer_data.sort_values(by=['Score','Location_rank'], ascending=[False,True], inplace=True)
        # print(labeled_farmer_data.head(5))
        
        return labeled_farmer_data.drop(['Cluster'],axis=1).head(5).to_json(orient='records')
    except Exception as e:
        print("Failed to get score:", e)
        return str(e)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)