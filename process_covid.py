# FIXME add needed imports
import json
from matplotlib import pyplot as plt



def load_covid_data(filepath):
    try:
        with open(filepath, 'r') as jason_file:
            input_data_as_string = jason_file.read()
            input_data = json.loads(input_data_as_string)
        if not check_schema(input_data):
            raise NotImplementedError("The file does not conform to the schema\n")
        return input_data
    except:
        raise NotImplementedError('The file is not json format')

def check_schema(data_json):
    # check "metadata","region","evolution"
    first_layer=["metadata","region","evolution"]
    for field_1 in first_layer:
        if not isinstance(data_json[field_1],dict):
            return False, "%s should be a dict" % field_1 

    # check 'time-range','age_binning'
    sub_metadata=['time-range','age_binning']
    for field_sub_1 in sub_metadata:
        if not isinstance(data_json['metadata'][field_sub_1],dict):
            return False, "%s should be a dict" % field_sub_1
    
    # check "hospitalizations" and "population" in 'age_binning'
    sub_age_binning=["hospitalizations" , "population"]
    for field_sub_2 in sub_age_binning:
        if not isinstance(data_json['metadata']['age_binning'][field_sub_2],list):
            return False, "%s should be a list" % field_sub_2
    
    # check 'populatin' in "region"
    sub_pop_region=["total","male","female","age"]
    for sub_pop in sub_pop_region:
        if sub_pop not in data_json["region"]["population"]:
            return False,"%s is not in population" %sub_pop
    
    # check key(date),"hospitalizations","epidemiology","weather" in "evolution"
    sub_evolution = ["hospitalizations","epidemiology", "weather", "government_response"]
    sub_epidemiology = ['confirmed','deceased','tested']
    for date,v in data_json["evolution"].items():
        if not date:
            return False, "date is wrong"
        if not isinstance(v, dict):
            return False, "content of %s is wrong" % date
        
        for sub in sub_evolution:
            if not isinstance(v[sub], dict):
                return False, "format of %s in %s is wrong" % (sub,date)
    
        # check "hospitalized" in "hospitalizations"
        if 'hospitalized'  not in v['hospitalizations']:
            return False, 'hospitalized is not in %s' %date
    
    # check "confirmed","deceased","tested" in "epidemiology"
    
        for sub in sub_epidemiology:
            if sub not in v['epidemiology']:
                return False, "%s is not in epidemiology" %sub
            else:
                if not isinstance(sub, dict):
                    return False, "format of %s is wrong" % sub
    return True


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
            if None in input_data["region"]["population"]["age"]:
                break
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
    if sex and max_age:
        raise NotImplementedError('at most one of sex or max_age allowed at a time')
    if not sex and not max_age:
        raise NotImplementedError('both of sex and max_age are not provided')
    if sex not in ['male', 'female', False] and max_age==[]:
        raise NotImplementedError('age or sex data are error')

    # set return result
    x_date=[]
    for key in input_data['evolution'].keys():
        x_date.append(key)
    
    y_value=[]

    # sex classification
    if sex:
        for key in input_data['evolution'].keys():
            if input_data['evolution'][key]['epidemiology']['confirmed'][status][sex] is None:
                y_value.append(None)
                continue
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

    # set default status and linestyle
    if status != 'new':
        status = 'total'
        linestyle_value='-'
    else:
        status='new'
        linestyle_value = '--'

        

    # set figure size
    fig = plt.figure(figsize=(10, 10))

    # FIXME change logic so this runs only when the sex plot is required

    if sex:
        for sex in ['male','female']:
            if sex == 'female':
                color_value = 'purple'
            if sex == 'male':
                color_value = 'green'

            date,value = generate_data_plot_confirmed(input_data,sex,None,status)
            plt.plot(date,value,label=status+" "+sex,color=color_value,linestyle=linestyle_value)
        save_path = input_data['region']['name'] + '_evolution_cases_sex.png' 

    # FIXME change logic so this runs only when the age plot is required

    if max_ages:
        for max_age in max_ages:
            age_groups=input_data['metadata']['age_binning']['population']
            age_label=0
            for i in range(len(age_groups)):
                if age_groups[i].split('-')[1]=='':
                    a=age_groups[i].split('-')
                    a[1]='150'
                    age_groups[i]=('-').join(a)
                if int(max_age)>=int(age_groups[i].split('-')[0]):
                    age_label=int(age_groups[i].split('-')[1])
            label_values = 'younger than'+' '+str(age_label)+' '+status
            date,value = generate_data_plot_confirmed(input_data,None,max_age,status)
            if max_age< 75:
                color_value = 'purple'
            if max_age < 50:
                color_value = 'orange'
            if max_age< 25:
                color_value = 'green'
            else:
                color_value = 'pink'
            
            plt.plot(date,value,label=label_values,color=color_value,linestyle=linestyle_value)
        save_path = input_data['region']['name'] + '_evolution_cases_age.png'

    fig.autofmt_xdate()  # To show dates nicely
    # TODO add title with "Confirmed cases in ..."
    plt.title('Confirmed cases in' + input_data['region']['name'])
    # TODO Add x label to inform they are dates
    plt.xlabel('date')
    # TODO Add y label to inform they are number of cases
    plt.ylabel('# cases')
    # TODO Add legend
    plt.legend(loc='upper left')
    # TODO Change logic to show or save it into a '{region_name}_evolution_cases_{type}.png'
    #      where type may be sex or age
    if save:
        plt.savefig(save_path)
    else:
        plt.show()




def compute_running_average(data,window):
    if isinstance(data, list) == 0:
        raise NotImplementedError('inproper data type')
    if window % 2 == 0 or window <= 0:
        raise NotImplementedError('The window size should be a positive odd number.')
        
    
    sum_rainfall=None
    list_sum_rainfall=[]
    average_rainfall=[]
    i=0
    # set the beginning None
    for i in range(int((window-1)/2)):
        sum_rainfall=None
        list_sum_rainfall.append(sum_rainfall)

    for i in range(int((window-1)/2),len(data)-int((window-1)/2)):
        sum_rainfall=0
        if data[i]!=None:
            for j in range(-int((window-1)/2),int((window-1)/2)+1):
                if data[i+j]==None:
                    data[i+j]=0
                    continue  
                sum_rainfall+=data[i+j]
                average_rainfall=sum_rainfall/(window)
            list_sum_rainfall.append(average_rainfall)
        if data[i]==None:
            for j in range(-int((window-1)/2),int((window-1)/2)+1):
                data[i]=0
                sum_rainfall+=data[i+j]
                average_rainfall=sum_rainfall/(window)
            list_sum_rainfall.append(average_rainfall)


    # set the ending None
    for i in range(len(data)-int((window-1)/2),len(data)):
        sum_rainfall=None
        list_sum_rainfall.append(sum_rainfall)
        
    return list_sum_rainfall

def simple_derivative(data):
    if isinstance(data, list) == 0:
        raise NotImplementedError("wrong data")
    list_data_derivative=[None]
    for i in range(1,len(data)):
        if data[i] == None or data[i-1]==None:
            list_data_derivative.append(None)
        else:
            list_data_derivative.append(data[i] - data[i-1])
    return list_data_derivative

def count_high_rain_low_tests_days(input_data):
    data_rainfall=[]
    for key in input_data['evolution']:
        data_rainfall.append(input_data['evolution'][key]['weather']['rainfall'])

    data_tested=[]
    for key in input_data['evolution']:
        data_tested.append(input_data['evolution'][key]['epidemiology']['tested']['new']['all'])


    data_test_smooth = compute_running_average(data_tested,7)
    data_test_deri= simple_derivative(data_test_smooth)
    
    # figure out the rain increase
    data_rain_deri = simple_derivative(data_rainfall)

    # find out the increase in rain while decrease in test
    data_rain_inc=0
    data_rain_inc_test_dec=0
    for i in range(len(data_rain_deri)):
        if data_rain_deri[i] != None and data_rain_deri[i] > 0:
            data_rain_inc+=1
            if data_test_deri[i] != None and data_test_deri[i] < 0:
                data_rain_inc_test_dec = data_rain_inc_test_dec+1
    return data_rain_inc_test_dec/data_rain_inc

