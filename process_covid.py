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
    if age_hos==[] or age_pop==[]:
        raise NotImplementedError('Age groups are not been provided')
    if age_hos==age_pop:
        age_bins=age_hos
    if age_hos!=age_pop:
        a=age_hos[-1].split('-')
        b=age_pop[-1].split('-')
        a[-1]='150'
        b[-1]='150'
        age_hos[-1]='-'.join(a)
        age_pop[-1]='-'.join(b)

        data_age_hos=[]
        for i in range(len(age_hos)):
            data_age_hos.append([int(age_hos[i].split('-')[0]),int(age_hos[i].split('-')[1])])
        
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
    age_start=0
    age_end=0
    i=0
    age_pop_start=0
    age_pop_end=0
    data_pop=0
    data_con=0



    result = {i: [] for i in age_bins}

    for dates, values in input_data['evolution'].items():
        # raise error when the age group is not provided
        if 'age' not in values['epidemiology']['confirmed']['total']:
            raise NotImplementedError('the age group of confirmed epidemiology is not provided')

        # data of confirmed epidemiology is none, continue
        elif values['epidemiology']['confirmed']['total']['age']==None\
        or values['epidemiology']['confirmed']['total']['age']==[]\
        or None in values['epidemiology']['confirmed']['total']['age']:
            continue
        # calculate the values of new age ranges
        for i in range(len(age_bins)):
            age_start=age_bins[i].split('-')[0]
            age_end=age_bins[i].split('-')[1]

            for j in range(len(age_pop)):
                if age_pop[j].split('-')[0]==age_start:
                    age_pop_start=j

            for k in range(len(age_pop)):
                if age_pop[k].split('-')[1]==age_end:
                    age_pop_end=k+1

            data_con=sum(values["epidemiology"]["confirmed"]["total"]["age"][age_pop_start:age_pop_end])
            data_pop=sum(input_data["region"]["population"]["age"][age_pop_start:age_pop_end])
            # calculate the ratios by date in age ranges
            result.get(age_bins[i]).append((dates, data_con * 100 / data_pop))
        return result



def hospital_vs_confirmed(input_data):
    date=[]
    data_evo=[]

    for key in input_data['evolution']:
        # numerator is 0 or None
        if input_data['evolution'][key]['hospitalizations']['hospitalized']['new']['all']==0\
        or input_data['evolution'][key]['hospitalizations']['hospitalized']['new']['all'] is None:
            continue
        # denominator is 0 or None
        if input_data['evolution'][key]['epidemiology']['confirmed']['new']['all']==0\
        or input_data['evolution'][key]['epidemiology']['confirmed']['new']['all'] is None:
            continue
        # data is empty
        if input_data['evolution'][key]['hospitalizations']['hospitalized']['new'] is None\
        or input_data['evolution'][key]['epidemiology']['confirmed']['new'] is None:
            continue
        # classification is empty
        if 'new' not in input_data['evolution'][key]['hospitalizations']['hospitalized'].keys()\
        or 'new' not in input_data['evolution'][key]['epidemiology']['confirmed'].keys():
            continue
        # create the list of date and ratio
        if input_data['evolution'][key]['hospitalizations']['hospitalized']['new']['all'] is not None and input_data['evolution'][key]['hospitalizations']['hospitalized']['new']['all']!=0:
            if input_data['evolution'][key]['epidemiology']['confirmed']['new']['all'] is not None and input_data['evolution'][key]['epidemiology']['confirmed']['new']['all'] !=0:
                date.append(key)
                data_evo.append(input_data['evolution'][key]['hospitalizations']['hospitalized']['new']['all']/input_data['evolution'][key]['epidemiology']['confirmed']['new']['all'])
    
    result=(date,data_evo)
    return result

def generate_data_plot_confirmed(input_data, sex, max_age,status):
    """
    At most one of sex or max_age allowed at a time.
    sex: only 'male' or 'female'
    max_age: sums all bins below this value, including the one it is in.
    status: 'new' or 'total' (default: 'total')
    """
    # set default status
    if status != 'new':
        status = 'total'
    else:
        status='new'

    # set classification to plot
    if sex==True and max_age==True:
        raise NotImplementedError('at most one of sex or max_age allowed at a time')
    if not sex and not max_age:
        raise NotImplementedError('both of sex and max_age are not provided')

    # set return result
    x_date=[]
    for key in input_data['evolution'].keys():
        x_date.append(key)
    
    y_value=[]

    # sex classification
    if sex:
        for key in input_data['evolution'].keys():
            y_value.append(input_data['evolution'][key]['epidemiology']['confirmed'][status][sex])

    # age classification
    else:
        age_range=input_data['metadata']['age_binning']['population']
        index=0
        sum_con_age=0
        for i in range(len(age_range)):
            if int(max_age)>=int(age_range[i].split('-')[0]):
                index+=1
            else:
                break
        for key in input_data['evolution']:
            sum_con_age=0
            if input_data['evolution'][key]['epidemiology']['confirmed'][status]['age']==None or input_data['evolution'][key]['epidemiology']['confirmed'][status]['age']==[] or None in input_data['evolution'][key]['epidemiology']['confirmed'][status]['age']:
                y_value.append(None)
                continue
            sum_con_age=sum(input_data['evolution'][key]['epidemiology']['confirmed'][status]['age'][0:index])
            y_value.append(sum_con_age)
    return x_date, y_value
      


def create_confirmed_plot(input_data, sex=False, max_ages=[], status=..., save=...):
    # FIXME check that only sex or age is specified.
    if sex==True and max_ages==True:
        raise NotImplementedError('at most one of sex or max_age allowed at a time')
    if not sex and not max_ages:
        raise NotImplementedError('both of sex and max_age are not provided')
    if sex > 1:
        raise Exception('sex error')

    # set default status
    if status != 'new':
        status = 'total'
    else:
        status='new'

    # set figure size
    fig = plt.figure(figsize=(10, 10))

    # FIXME change logic so this runs only when the sex plot is required
    if sex:
        for sex in ['male','female']:
            date,values = generate_data_plot_confirmed(input_data,sex,False)
            if sex=='female':
                colour_values="purple"
            if sex=='male':
                colour_values='green'
            
            if status=='new':
                linestyle_values='--'
            else:
                linestyle_values='-'
            plt.plot(date,values,label=status+" "+sex,color=colour_values,linestyle=linestyle_values)
            save_path = input_data + 'evolution_by_sex_groups' 

    # FIXME change logic so this runs only when the age plot is required
    if max_ages:
        for max_age in max_ages:
            (date,values,label_values,colour_values,linestyle_values) = generate_data_plot_confirmed(input_data, None, max_age, status)
            plt.plot(date,values,label=label_values,color=colour_values,linestyle=linestyle_values)
            save_path = input_data + 'evolution_by_age_ranges' 

    fig.autofmt_xdate()  # To show dates nicely
    # TODO add title with "Confirmed cases in ..."
    plt.title('Confirmed cases in' + input_data['region']['name'])
    # TODO Add x label to inform they are dates
    plt.xlabel('Date')
    # TODO Add y label to inform they are number of cases
    plt.ylabel('Cases')
    # TODO Add legend
    plt.legend(loc='upper left')
    # TODO Change logic to show or save it into a '{region_name}_evolution_cases_{type}.png'
    #      where type may be sex or age
    if save:
        plt.savefig(save_path)
    else:
        plt.show()



def compute_running_average(data_tested,size_window):
    if isinstance(data_tested, list) == 0:
        raise NotImplementedError('inproper data type')
    if size_window % 2 == 0 or size_window <= 0:
        raise NotImplementedError('The window size should be a positive odd number.')
        
    
    sum_rainfall=None
    list_sum_rainfall=[]
    average_rainfall=[]
    i=0
    # set the beginning None
    for i in range(int((size_window-1)/2)):
        sum_rainfall=None
        list_sum_rainfall.append(sum_rainfall)

    for i in range(int((size_window-1)/2),len(data_tested)-int((size_window-1)/2)):
        sum_rainfall=0
        if data_tested[i]!=None:
            for j in range(-int((size_window-1)/2),int((size_window-1)/2)+1):
                sum_rainfall+=data_tested[i+j]
                average_rainfall=sum_rainfall/(size_window)
            list_sum_rainfall.append(average_rainfall)
        if data_tested[i]==None:
            for j in range(-int((size_window-1)/2),int((size_window-1)/2)+1):
                data_tested[i]=0
                sum_rainfall+=data_tested[i+j]
                average_rainfall=sum_rainfall/(size_window)
            list_sum_rainfall.append(average_rainfall)


    # set the ending None
    for i in range(len(data_tested)-int((size_window-1)/2),len(data_tested)):
        sum_rainfall=None
        list_sum_rainfall.append(sum_rainfall)
        
    return list_sum_rainfall

def simple_derivative(data):
    raise NotImplementedError

def count_high_rain_low_tests_days(input_data):
    raise NotImplementedError
