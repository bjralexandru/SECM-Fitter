import pandas as pd
import matplotlib.pyplot as plt
import json

# data_to_represent = pd.read_csv('/home/proxyl/Documents/secm_fitter/website/static/files/dummy_data_processed')
# distance_values = data_to_represent['L_data'].tolist()
# experiment_current_values = data_to_represent['iT_experimental'].tolist()


# print(distance_values)
# plt.scatter(distance_values, experiment_current_values)
# plt.show()

# popt = 0.04402121212112
# E_sigma = 0.02321312321321

# Kappa = '{}'.format("{:.5f}".format(popt))
# Chi2 = '{}'.format("{:.5f}".format(E_sigma))
# data = {'Kappa':[Kappa], 'Chi2':[Chi2]}
# temp = pd.DataFrame(data)
# print(temp.head())


# params = pd.read_csv('/home/proxyl/Documents/secm_fitter/website/static/files/dummy_data_params')
# Kappa = params['Kappa'].tolist()[0]
# Chi2 = params['Chi2'].tolist()[0]

# print(Kappa)
# print(Chi2)

# list = {'L_data':[1,2,3,4,5,6,7,8,9]}
# dump = json.dumps(list)
# print(dump)
# print(type(dump))

data = [1, 2, 3, 4]
json_data = json.dumps(data)
print('Before:')
print(data)

dejson_data = json.loads(json_data)
print('After deserialization:')
print(type(dejson_data))

