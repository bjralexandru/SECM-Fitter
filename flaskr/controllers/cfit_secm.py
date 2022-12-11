import xlrd
import matplotlib.pyplot as plt
import math
import scipy.optimize
import numpy as np
import pandas as pd
from . import UPLOAD_FOLDER
##################################   DATA  CURATOR   #########################################
def fit_data_Cornut(path, electrode_radius, Rg, iT_inf, K):
    workbook = xlrd.open_workbook(path)
    first_sheet = workbook.sheet_by_index(0)



    current_values = [] # WILL STORE THE VALUES FROM THE 'Imon [1]' COLUMN OF THE EXCEL FILE

    for i in first_sheet.col_values(2,1):
        current_values.append(i)

    current_values = current_values[20:] # Deletes the first points of the curve
                                            # its where the tip touches the surface and its not good for the fit

    distance_values = [] # WILL STORE THE VALUES FROM THE 'Distance [m]' COLUMN OF THE EXCEL FILE



    for v in first_sheet.col_values(1,1):
        distance_values.append(v)

    distance_values = distance_values[20:] # also deletes the first points for the distance values
                                                # in order to have the same number of points in both arrays

    # In the given data-example, by not deleting the first 20-points the algorithm leads to an order of magnitude in error.


    ##################################  PREREQUISITES  #########################################


    global L_data
    global iT_data

    L_data = [] # Stores the values for normalized distance L=d/a - EXPERIMENTAL
    iT_data = [] # Stores the values for normalized current iT=iT/iT_inf - EXPERIMENTAL

    for x in distance_values:
        #value = x-zoffset
        L_data.append(x/float(electrode_radius))

    for y in current_values:
        iT_data.append(y/float(iT_inf))


    ############################  ALFA AND BETA CONSTANTS  #######################################

    alfa = math.log(2) + math.log(2)*(1- 2/math.pi*math.acos(1/Rg)) - math.log(2)*(1-(2/math.pi*math.acos(1/Rg))**2)
    beta = 1 + 0.639*(1-2/math.pi*math.acos(1/Rg))-0.186*(1-(2/math.pi*math.acos(1/Rg))**2)



    ############################    SIMULATED   CURVES     #######################################

    def cornut(L_data, K):

        iT_ins = ((2.08/Rg**0.358)*(L_data-(0.145/Rg)) + 1.585)/(2.08/(Rg**0.358)*(L_data+0.0023*Rg)+1.57+(math.log(Rg)/L_data)+2/(math.pi*Rg)*math.log(1+(math.pi*Rg)/(2*L_data)))
        #iT_insulated.append(iT_ins) # values are stored backwards to shape the graph as they happen
                            # in reality from 'infinite' distance to aprox. 0
                            # distance tip-to-substrate.

        #iT_cond (Eq. 18 - article)
        iT_cond = alfa + (math.pi/(4*beta*math.atan(L_data))) + ((1-alfa-1/(2*beta))*2/math.pi*math.atan(L_data))
    

        #iT_simulated (Eq. 21 - L,Rg,K)
        iT_sim = alfa + (math.pi/(4*beta*math.atan(L_data+1/K))) + ((1-alfa-1/(2*beta))*2/math.pi*math.atan(L_data+1/K)) + (iT_ins-1)/((1+2.47*Rg**(0.31)*L_data*K)*(1+L_data**(0.006*Rg+0.113)*K**(-0.0236*Rg+0.91)))
        return iT_sim


    ############################    LEAST SQ. FITTING     ######################################


    r = np.vectorize(cornut)

    p0 = [K]


    popt1, pcov = scipy.optimize.curve_fit(r, L_data, iT_data, p0=p0, method = 'lm') #calculates the popt and pcov for the experimental
                                                                                        # data provided by the user

    # whereas -popt gives the: array Optimal values for the parameters so that the sum of the squared residuals of f(xdata, *popt) - ydata is minimized
        # and -pcov returns the: 2d array The estimated covariance of popt. The diagonals provide the variance of the parameter estimate.

    popt = popt1[0] #Leave the parantheses

    # Although in order to also compute one standard deviation errors on the parameters use perr = np.sqrt(np.diag(pcov)). 

    E_sigma = np.sqrt(np.diag(pcov)) # Error parameter
    E_sigma = E_sigma[0] #Leave the parantheses



    ############################  PRINT THE RESULTS     ########################################

    print('Kappa = {}'.format("{:.5f}".format(popt)),'\nCovariance = {}'.format(pcov[0]), '\nE_sigma = {}'.format("{:.5f}".format(E_sigma)))

    ############################    FIGURE BUILDING     ########################################
    # fig = plt.figure(figsize=(10,8))
    # plt.plot(L_data, iT_data, 'k', label = 'Experimental Data')
    # plt.plot(L_data, r(L_data, K), 'b',label = 'First guess for Kappa = {}'.format(K))
    # plt.plot(L_data, r(L_data, popt),'y',label = 'Cornut Fit for Kappa = {}\nWith an estimated error of {} '.format("{:.4f}".format(popt),"{:.5f}".format(E_sigma)))
    # plt.title('Approach Curve Fitting')
    # plt.legend()
    # plt.show()
   
    global iT_simulated
    iT_simulated = r(L_data, popt)

    global final_dataset
    final_dataset = {"L_data":L_data, 
                        "iT_experimental":iT_data,
                        "iT_simulated":iT_simulated}

    Kappa = '{}'.format("{:.5f}".format(popt))
    Chi2 = '{}'.format("{:.5f}".format(E_sigma))
    temp = {'Kappa':[Kappa], 'Chi2':[Chi2]}
    global temp_df 
    # Make this dataframe accessible to the save_file() fn. so it automattically saves the kappa and chi2 along with the processed data.
    temp_df = pd.DataFrame(temp)
    

    
    #################################   THE END     ############################################
def save_file(file_path):
    # Save the simulated current values as well as the original experimental data in a single file.
    # It will have 3 columns (and no index) L_data (distance), iT_data (experim. current values),
    # iT_simulated (fitted current values after passing the functions designed by Cornut et al.)
    df = pd.DataFrame(final_dataset)
    df.to_csv(file_path+'_processed'+'.csv', encoding='utf-8', index=False)
    temp_df.to_csv(file_path+'_params'+'.csv', encoding='utf-8', index=False)

def display_graph(filename):
    # Build up the plot from the arrays in this script and save it alongside the other .xls and .csv
    # files for later use. However, it will only be delivered as a static .png to the final .html
    fig = plt.figure()
    plt.scatter(L_data, iT_data, color='black', label='Experimental data')
    plt.plot(L_data, iT_simulated, 'r', label = 'Fitted Data')
    plt.legend()
    fig.savefig(filename)
    return fig

