# FIXME add needed imports
import json
from matplotlib import pyplot as plt
import pytest


def load_covid_data(filepath):
    with open(filepath, 'r') as jason_file:
        input_data_as_string = jason_file.read()
        try:
            input_data = json.loads(input_data_as_string)
        except:
            raise NotImplementedError('The file is not json format')
    return input_data

def cases_per_population_by_age(input_data):
    age_hos = input_data['metadata']['age_binning']['hospitalizations']
    age_pop = input_data['metadata']['age_binning']['population']
    a=age_hos[-1].split('-')
    b=age_pop[-1].split('-')
    a[-1]='150'
    b[-1]='150'
    age_hos[-1]='-'.join(a)
    age_pop[-1]='-'.join(b)

    data_age_hos=[]
    for i in range(len(age_hos)):
        data_age_hos.append([int(age_hos[i].split('-')[0]),int(age_hos[i].split('-')[1])])
    data_age_hos
    data_age_pop=[]
    for j in range(len(age_pop)):
        data_age_pop.append([int(age_pop[j].split('-')[0]),int(age_pop[j].split('-')[1])])


    age_bins=[]
    i=0
    j=0
    while i < len(data_age_hos) and j < len(data_age_pop):
        if data_age_hos[i][0] == data_age_pop[j][0]:
            if data_age_hos[i][1]==data_age_pop[j][1]:
                age_bins.append('-'.join([str(data_age_pop[j][0]),str(data_age_pop[j][1])]))
                i+=1
                j+=1

            elif data_age_hos[i][1]<int(data_age_pop[j][1]):
                i+=1
            else: # int(data_age_hos[i][1])>int(data_age_pop[j][1]):
                j+=1

        elif data_age_hos[i][0] > data_age_pop[j][0]:
            if data_age_hos[i][1] > data_age_pop[j][1]:
                raise ValueError('rebin fail')
            elif data_age_hos[i][1]< data_age_pop[j][1]:
                i+=1
            else: # age_hos_i[1]==age_pop_j[1]:
                age_bins.append('-'.join([str(data_age_pop[j][0]),str(data_age_pop[j][1])]))
                i+=1
                j+=1


        else: # data_age_hos[i][0] < data_age_pop[j][0]:
            if data_age_hos[i][1]< data_age_pop[j][1]:
                raise ValueError('rebin fail')
            elif data_age_hos[i][1] > data_age_pop[j][1]:
                j+=1
            else: # age_hos_i[1]==age_pop_j[1]:
                age_bins.append('-'.join([str(data_age_hos[i][0]),str(data_age_hos[i][1])]))
                i+=1
                j+=1
        # recover the original 
    a=age_hos[-1].split('-')
    a[-1]=''
    age_hos[-1]='-'.join(a)
    input_data['metadata']['age_binning']['hospitalizations']=age_hos

    b=age_pop[-1].split('-')
    b[-1]=''
    age_pop[-1]='-'.join(b)
    input_data['metadata']['age_binning']['population']=age_pop

    # get result: rebin of age groups
    c=age_bins[-1].split('-')
    c[-1]=''
    age_bins[-1]='-'.join(c)
        
    # create the list of date and total of confirmed epidemiology
    date=[]
    data_con_byAge=[]
    for key in input_data['evolution']:
        # raise error when the age group is not provided
        if 'age' not in input_data['evolution'][key]['epidemiology']['confirmed']['total']:
            raise NotImplementedError('the age group of confirmed epidemiology is not provided')
            
        # data of confirmed epidemiology is none, continue
        elif input_data['evolution'][key]['epidemiology']['confirmed']['total']['age']==None\
        or input_data['evolution'][key]['epidemiology']['confirmed']['total']['age']==[]\
        or None in input_data['evolution'][key]['epidemiology']['confirmed']['total']['age']:
            continue
            
        else: # data of confirmed epidemiology is valid
            date.append(key)
            data_con_byAge.append(input_data['evolution'][key]['epidemiology']['confirmed']['total']['age'])
    
    # create rate of people hospitalised and confirmed cases everyday by age_bins
    i_age=0
    i_date=0
    ratio_DateByAge=[]
    result={}
    
    for i_age in range(len(age_bins)):
        if input_data["region"]["population"]["age"][i_age]==None or input_data["region"]["population"]["age"][i_age]==[]:
            raise NotImplementedError('the population of age group is not provided')
        else:
            ratio_DateByAge=[]
            for i_date in range(len(date)):
                ratio_date=(date[i_date],data_con_byAge[i_date][i_age]/input_data["region"]["population"]["age"][i_age])
                ratio_DateByAge.append(ratio_date)
            result.update({age_bins[i_age]:ratio_DateByAge})
    return result


def hospital_vs_confirmed(input_data):
    raise NotImplementedError

def generate_data_plot_confirmed(input_data, sex, max_age, status):
    """
    At most one of sex or max_age allowed at a time.
    sex: only 'male' or 'female'
    max_age: sums all bins below this value, including the one it is in.
    status: 'new' or 'total' (default: 'total')
    """
    raise NotImplementedError

def create_confirmed_plot(input_data, sex=False, max_ages=[], status=..., save=...):
    # FIXME check that only sex or age is specified.
    fig = plt.figure(figsize=(10, 10))
    # FIXME change logic so this runs only when the sex plot is required
    for sex in ['male', 'female']:
        # FIXME need to change `changeme` so it uses generate_data_plot_confirmed
        plt.plot('date', 'value', changeme)
    # FIXME change logic so this runs only when the age plot is required
    for age in max_ages:
        # FIXME need to change `changeme` so it uses generate_data_plot_confirmed
        plt.plot('date', 'value', changeme)
    fig.autofmt_xdate()  # To show dates nicely
    # TODO add title with "Confirmed cases in ..."
    # TODO Add x label to inform they are dates
    # TODO Add y label to inform they are number of cases
    # TODO Add legend
    # TODO Change logic to show or save it into a '{region_name}_evolution_cases_{type}.png'
    #      where type may be sex or age
    plt.show()

def compute_running_average(data, window):
    raise NotImplementedError

def simple_derivative(data):
    raise NotImplementedError

def count_high_rain_low_tests_days(input_data):
    raise NotImplementedError
