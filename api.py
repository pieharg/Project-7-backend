import flask
import numpy as np
import pandas as pd
import joblib


app = flask.Flask(__name__)

##########################
# Chargement des données #
##########################

# Charger le modèle joblib
with open('pipeline_p7.joblib', 'rb') as pipe :
    pipeline = joblib.load(pipe)

# Charger les données
df = pd.read_csv("data_clients.csv", index_col=0)

###################################################
# Calcul et échange des données avec le front-end #
###################################################

# cette route ne sert qu'à vérifier que l'api fonctionne une fois celle-ci déployée
@app.route('/')
def home():
    return "Hello, World!"

# route permettant de vérifier la présence d'une demande de crédit déjà formulée
@app.route('/client_info', methods=['GET'])
def retrieve_client_info():
    client_ID = int(flask.request.args.get('client_ID'))
    if df['SK_ID_CURR'].isin([client_ID]).any():
        return flask.jsonify(True)
    else :
        return flask.jsonify(False)

# envoie d'une réponse pour une demande déjà formulée
@app.route('/predict/ID', methods=['GET'])
def make_prediction_ID():
    client_ID = int(flask.request.args.get('client_ID'))
    # proba (d'être mauvais payeur(classe 1))
    proba = df.loc[df['SK_ID_CURR']==client_ID,'PRED_1'].item() # probabilité d'être mauvais payeur (préalablement calculée pour alléger le csv)
    # transformation de la proba en score /100
    score = round(((proba-1)*-1)*100,1) # ex: très mauvais payeur proba=0.90 --> score=10/100
    return flask.jsonify(score)

# envoie d'une réponse pour une demande "en direct"
@app.route('/predict/noID', methods=['GET'])
def make_prediction_noID():
    # récupération des infos du front
    gender = flask.request.args.get('gender')
    if gender == "Monsieur":
        gender = 0
    elif gender == "Madame":
        gender = 1
    else:
        gender=np.nan
    age = int(flask.request.args.get('age'))
    if age == 0:
        age = np.nan
    cnt_children = int(flask.request.args.get('cnt_children'))
    time_employment = int(flask.request.args.get('time_employment'))
    income = int(flask.request.args.get('income'))
    own_car = flask.request.args.get('own_car')
    if own_car == "Oui":
        own_car = 1
    elif own_car == "Non":
        own_car = 0
    else:
        own_car = np.nan
    own_realty = flask.request.args.get('own_realty')
    if own_realty == "Oui":
        own_realty = 1
    elif own_realty == "Non":
        own_realty = 0
    else:
        own_realty = np.nan
    amt_goods_price = int(flask.request.args.get('amt_goods_price'))
    amt_credit = int(flask.request.args.get('amt_credit'))
    amt_annuity = float(flask.request.args.get('amt_annuity'))
    # construction array
    array = np.empty(795)
    array[:] = np.nan
    # attribution des valeurs
    array[0] = gender
    array[9] = age * (-365.245)
    array[3] = cnt_children
    array[10] = time_employment * (-365.245)
    array[4] = income
    array[1] = own_car
    array[2] = own_realty
    array[7] = amt_goods_price
    array[5] = amt_credit
    array[6] = amt_annuity
    # calcul proba (d'être mauvais payeur(classe 1))
    proba = pipeline.predict_proba(array.reshape(1,-1))[0,1]
    score = round(((proba-1)*-1)*100,1) # même principe que dans la fonction précédente
    return flask.jsonify(score)

# toutes les prochaines routes servent à construire des éléments de comparaison (graphs, metriques...)
@app.route('/comparison/ID/graph_income', methods=['GET'])
def data_income():
    client_ID = int(flask.request.args.get('client_ID'))
    income = float(df.loc[df['SK_ID_CURR']==client_ID]['AMT_INCOME_TOTAL'])
    data = df.loc[df['TARGET']==0]['AMT_INCOME_TOTAL'].tolist()
    return flask.jsonify({"income":income, "data":data})

@app.route('/comparison/ID/graph_credit', methods=['GET'])
def data_credit():
    client_ID = int(flask.request.args.get('client_ID'))
    credit = float(df.loc[df['SK_ID_CURR']==client_ID]['AMT_CREDIT'])
    data = df.loc[df['TARGET']==0]['AMT_CREDIT'].tolist()
    return flask.jsonify({"credit":credit, "data":data})

@app.route('/comparison/ID/graph_annuity', methods=['GET'])
def data_annuity():
    client_ID = int(flask.request.args.get('client_ID'))
    annuity = float(df.loc[df['SK_ID_CURR']==client_ID]['AMT_ANNUITY'])
    data = df.loc[df['TARGET']==0]['AMT_ANNUITY'].tolist()
    return flask.jsonify({"annuity":annuity, "data":data})

@app.route('/comparison/ID/metrics', methods=['GET'])
def metrics():
    client_ID = int(flask.request.args.get('client_ID'))
    income = float(df.loc[df['SK_ID_CURR']==client_ID]['AMT_INCOME_TOTAL'])
    m1 = df.loc[df['AMT_INCOME_TOTAL']<income].shape[0]/df.shape[0]*100
    m2 = df.loc[df['TARGET']==0].loc[df['AMT_INCOME_TOTAL']>0.95*income].loc[df['AMT_INCOME_TOTAL']<1.05*income]['AMT_CREDIT'].mean()
    m3 = df.loc[df['TARGET']==0].loc[df['AMT_INCOME_TOTAL']>0.95*income].loc[df['AMT_INCOME_TOTAL']<1.05*income]['AMT_ANNUITY'].mean()
    return flask.jsonify({"metrics":[m1,m2,m3]})

@app.route('/comparison/noID/graph_income', methods=['GET'])
def data_income_noID():
    data = df.loc[df['TARGET']==0]['AMT_INCOME_TOTAL'].tolist()
    return flask.jsonify({"data":data})

@app.route('/comparison/noID/graph_credit', methods=['GET'])
def data_credit_noID():
    data = df.loc[df['TARGET']==0]['AMT_CREDIT'].tolist()
    return flask.jsonify({"data":data})

@app.route('/comparison/noID/graph_annuity', methods=['GET'])
def data_annuity_noID():
    data = df.loc[df['TARGET']==0]['AMT_ANNUITY'].tolist()
    return flask.jsonify({"data":data})

@app.route('/comparison/noID/metrics', methods=['GET'])
def metrics_noID():
    income = float(flask.request.args.get('income'))
    m1 = df.loc[df['AMT_INCOME_TOTAL']<income].shape[0]/df.shape[0]*100
    m2 = df.loc[df['TARGET']==0].loc[df['AMT_INCOME_TOTAL']>0.95*income].loc[df['AMT_INCOME_TOTAL']<1.05*income]['AMT_CREDIT'].mean()
    m3 = df.loc[df['TARGET']==0].loc[df['AMT_INCOME_TOTAL']>0.95*income].loc[df['AMT_INCOME_TOTAL']<1.05*income]['AMT_ANNUITY'].mean()
    return flask.jsonify({"metrics":[m1,m2,m3]})

if __name__ == '__main__':
    app.run(port=5000)