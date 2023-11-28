import flask
import numpy as np
import pandas as pd
import joblib


app = flask.Flask(__name__)

##########################
# Chargement des données #
##########################

# Charger les modèles joblib
with open('pipeline_backend.joblib', 'rb') as pipe :
    pipeline = joblib.load(pipe)

# Charger les données
df = pd.read_csv("data_clients.csv", index_col=0)

###################################################
# Calcul et échange des données avec le front-end #
###################################################

# cette route ne sert qu'à vérifier que l'api fonctionne une fois celle-ci déployée
@app.route('/')
def home():
    """
    Displays basic text on the index page for a test purpose
    """
    return "Hello, World!"

# route permettant de vérifier la présence d'une demande de crédit déjà formulée
@app.route('/client_info', methods=['GET'])
def retrieve_client_info():
    """
    Retrieves the client ID from the front and returns True if client is in the database
    Else returns False
    """
    client_ID = int(flask.request.args.get('client_ID'))
    if df['SK_ID_CURR'].isin([client_ID]).any():
        return flask.jsonify(True)
    else :
        return flask.jsonify(False)

# envoie d'une score pour une demande déjà formulée
@app.route('/predict/ID', methods=['GET'])
def make_prediction_ID():
    """
    Retrieves the client ID and returns his score based on pre-calculated data
    """
    client_ID = int(flask.request.args.get('client_ID'))
    # probabilité d'être mauvais payeur (préalablement calculée pour alléger le processus)
    proba = df.loc[df['SK_ID_CURR']==client_ID,'PRED_1'].item()
    # je transforme la proba [0,1] en un score /100
    score = round(((proba-1)*-1)*100,1) # ex : une proba 0.80 d'être un mauvais payeur --> score = 20/100
    return flask.jsonify(score)

# j'implémente une condition dynamique pour effectuer une simulation ou une comparaison
# car sinon cela peut mener à des erreurs dans le script quand le salaire est trop bas
# à noter qu'une condition dynamique n'est pas forcément optimale
@app.route('/minimum_income', methods=['GET'])
def minimum_income():
    """
    Retrieves client income and returns True if client income is above minimal
    Else returns False
    """
    min_income = df.loc[df['TARGET']==0]['AMT_INCOME_TOTAL'].min()
    income = int(flask.request.args.get('amt_income'))
    if income >= min_income :
        return flask.jsonify(True)
    else :
        return flask.jsonify(False)

# même chose avec une valeur de salaire maximum
@app.route('/maximum_income', methods=['GET'])
def maximum_income():
    """
    Retrieves client income and returns True if client income is below maximum
    Else returns False
    """
    max_income = df.loc[df['TARGET']==0]['AMT_INCOME_TOTAL'].max()
    income = int(flask.request.args.get('amt_income'))
    if income <= max_income :
        return flask.jsonify(True)
    else :
        return flask.jsonify(False)

# prédiction score partie mandatory
@app.route('/predict/mandatory', methods=['GET'])
def make_prediction_mandatory():
    """
    Retrieves the 4 values for prediction with minimal informations
    Returns score
    """
    amt_income = int(flask.request.args.get('amt_income'))
    amt_goods_price = int(flask.request.args.get('amt_goods_price'))
    amt_credit = int(flask.request.args.get('amt_credit'))
    amt_annuity = float(flask.request.args.get('amt_annuity'))
    array = np.empty(10)
    array[:] = np.nan
    array[0] = amt_income
    array[1] = amt_goods_price
    array[2] = amt_credit
    array[3] = amt_annuity
    proba = pipeline.predict_proba(array.reshape(1,-1))[0,1]
    # transformation proba --> score
    score = round(((proba-1)*-1)*100,1)
    return flask.jsonify(score)

# prédiction score partie optional
@app.route('/predict/optional', methods=['GET'])
def make_prediction_optional():
    """
    Retrieves the 10 values for prediction with (minimal + optional) informations
    Returns score
    """
    amt_income = int(flask.request.args.get('amt_income'))
    amt_goods_price = int(flask.request.args.get('amt_goods_price'))
    amt_credit = int(flask.request.args.get('amt_credit'))
    amt_annuity = float(flask.request.args.get('amt_annuity'))
    gender = flask.request.args.get('gender')
    if gender == "Monsieur":
        gender = 0
    elif gender == "Madame":
        gender = 1
    age = int(flask.request.args.get('age'))
    cnt_children = int(flask.request.args.get('cnt_children'))
    time_employment = int(flask.request.args.get('time_employment'))
    own_car = flask.request.args.get('own_car')
    if own_car == "Oui":
        own_car = 1
    elif own_car == "Non":
        own_car = 0
    own_realty = flask.request.args.get('own_realty')
    if own_realty == "Oui":
        own_realty = 1
    elif own_realty == "Non":
        own_realty = 0
    array = np.array([amt_income, amt_goods_price, amt_credit, amt_annuity, gender, age, cnt_children, time_employment, own_car, own_realty])
    proba = pipeline.predict_proba(array.reshape(1,-1))[0,1]
    # transformation proba --> score
    score = round(((proba-1)*-1)*100,1)
    return flask.jsonify(score)

# récupère le salaire dans la base de données pour l'ID spécifié
@app.route('/compare/ID/client_income', methods=['GET'])
def retrieve_client_income():
    """
    Retrieves the client ID and returns his income from database
    """
    client_ID = int(flask.request.args.get('client_ID'))
    income = float(df.loc[df['SK_ID_CURR']==client_ID]['AMT_INCOME_TOTAL'])
    return flask.jsonify(income)

# même chose avec le montant du crédit
@app.route('/compare/ID/client_credit', methods=['GET'])
def retrieve_client_credit():
    """
    Retrieves the client ID and returns his credit amount from database
    """
    client_ID = int(flask.request.args.get('client_ID'))
    credit = float(df.loc[df['SK_ID_CURR']==client_ID]['AMT_CREDIT'])
    return flask.jsonify(credit)

# même chose avec le montant des annuités
@app.route('/compare/ID/client_annuity', methods=['GET'])
def retrieve_client_annuity():
    """
    Retrieves the client ID and returns his annuity amount from database
    """
    client_ID = int(flask.request.args.get('client_ID'))
    annuity = float(df.loc[df['SK_ID_CURR']==client_ID]['AMT_ANNUITY'])
    return flask.jsonify(annuity)

# les 6 prochaines routes permettent de communiquer les valeurs de la base de 
# données et ainsi de construire les graphiques
@app.route('/compare/distribution_income', methods=['GET'])
def retrieve_database_income():
    """
    Sends the income distribution from database for graphic construction reason
    """
    distribution_income = df.loc[df['TARGET']==0]['AMT_INCOME_TOTAL'].tolist()
    return flask.jsonify(distribution_income)

@app.route('/compare/distribution_credit', methods=['GET'])
def retrieve_database_credit():
    """
    Sends the credit amount distribution from database for graphic construction reason
    """
    distribution_credit = df.loc[df['TARGET']==0]['AMT_CREDIT'].tolist()
    return flask.jsonify(distribution_credit)

@app.route('/compare/distribution_annuity', methods=['GET'])
def retrieve_database_annuity():
    """
    Sends the annuity amount distribution from database for graphic construction reason
    """
    distribution_annuity = df.loc[df['TARGET']==0]['AMT_ANNUITY'].tolist()
    return flask.jsonify(distribution_annuity)

@app.route('/compare/metric_1', methods=['GET'])
def retrieve_metric_1():
    """
    Retrieves the client income from front and returns the m1 metric
    m1 metric defines your position in % in the income distribution from the databse
    """
    income = int(flask.request.args.get('amt_income'))
    m1 = df.loc[df['AMT_INCOME_TOTAL']<income].shape[0]/df.shape[0]*100
    return flask.jsonify(m1)

@app.route('/compare/metric_2', methods=['GET'])
def retrieve_metric_2():
    """
    Retrieves the client income from front and returns the m2 metric
    m2 metric defines the credit amount of people WHO GOT THE LOAN in your income range (+/- 5%)
    """
    income = int(flask.request.args.get('amt_income'))
    m2 = df.loc[df['TARGET']==0].loc[df['AMT_INCOME_TOTAL']>0.95*income].loc[df['AMT_INCOME_TOTAL']<1.05*income]['AMT_CREDIT'].mean()
    return flask.jsonify(m2)

@app.route('/compare/metric_3', methods=['GET'])
def retrieve_metric_3():
    """
    Retrieves the client income from front and returns the m3 metric
    m3 metric defines the annuity amount of people WHO GOT THE LOAN in your income range (+/- 5%)
    """
    income = int(flask.request.args.get('amt_income'))
    m3 = df.loc[df['TARGET']==0].loc[df['AMT_INCOME_TOTAL']>0.95*income].loc[df['AMT_INCOME_TOTAL']<1.05*income]['AMT_ANNUITY'].mean()
    return flask.jsonify(m3)

if __name__ == '__main__':
    app.run()