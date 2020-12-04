import pytest
from pytest import raises
import process_covid
from process_covid import (load_covid_data,
                           cases_per_population_by_age,
                           hospital_vs_confirmed,
                           generate_data_plot_confirmed,
                           create_confirmed_plot,
                           compute_running_average,
                           simple_derivative,
                           count_high_rain_low_tests_days)

# test json file
def test_load_covid_data():
    data_er = process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    assert data_er is not None



def test_rebin():
    # test 1
    A = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-']
    B = ['0-19', '20-39', '40-']
    result_correct=['0-19', '20-39', '40-']

    data_er=process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    data_er['metadata']['age_binning']['hospitalizations']=A
    data_er['metadata']['age_binning']['population']=B
    result_original=cases_per_population_by_age(data_er)
    age_bins_original=[]
    for key in result_original:
        age_bins_original.append(key)
    age_bins_original
    
    try:
        assert age_bins_original == result_correct
        print('correct result')
    except NotImplementedError:
        print('wrong result')

    #test 2
    A = ['0-14', '15-29', '30-44', '45-']
    B = ['0-19', '20-39', '40-']

    data_er=process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    data_er['metadata']['age_binning']['hospitalizations']=A
    data_er['metadata']['age_binning']['population']=B
    with pytest.raises(ValueError):
        assert list(process_covid.cases_per_population_by_age(data_er).keys())




def test_hospital_vs_confirmed():
    data_er = process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    result = process_covid.hospital_vs_confirmed(data_er)
    try:
        assert ((result[0][0],result[1][0])==('2020-03-16',data_er['evolution']['2020-03-16']['hospitalizations']['hospitalized'] ['new']['all']/data_er['evolution']['2020-03-16']['epidemiology']['confirmed']['new'] ['all']) and\
    (result[0][3],result[1][3])== ('2020-03-19',data_er['evolution']['2020-03-19']['hospitalizations']['hospitalized'] ['new']['all']/data_er['evolution']['2020-03-19']['epidemiology']['confirmed']['new'] ['all']) and\
    (result[0][10],result[1][10])== ('2020-03-26',data_er['evolution']['2020-03-26']['hospitalizations']['hospitalized'] ['new']['all']/data_er['evolution']['2020-03-26']['epidemiology']['confirmed']['new'] ['all']))
        print('correct output')
    except NotImplementedError:
        print('wrong output')


def test_hospital_vs_confirmed_missing_data():
    data_er = process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    date_origin, ratio_dateByAge_origin = hospital_vs_confirmed(data_er)
    del (date_origin[0:2])
    del (ratio_dateByAge_origin[0:2])

    data_er['evolution']['2020-03-16']['hospitalizations']['hospitalized']['new']['all']=None
    data_er['evolution']['2020-03-17']['epidemiology']['confirmed']['new']['all']=None
    date_test, ratio_dateByAge_test = hospital_vs_confirmed(data_er)
    try:
        assert date_origin == date_test
        assert ratio_dateByAge_origin == ratio_dateByAge_test
        print('the result is correct when there is missing data')
    except NotImplementedError:
        print('the result is not correct because of missing data')



def test_generate_data_plot_confirm_missing_data():
    data_er = process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    result = process_covid.generate_data_plot_confirmed(data_er,'male',[],None)
    result[1][3]=None
    result[1][5]=None
    
    data_er['evolution']['2020-03-19']['epidemiology']['confirmed']['total']['male']=None
    data_er['evolution']['2020-03-21']['epidemiology']['confirmed']['total']['male']=None
    result_test=process_covid.generate_data_plot_confirmed(data_er,'male',[],None)
    try:
        assert result == result_test
        print('the result is correct when there is missing data')
    except NotImplementedError:
        print('the result is not correct because of missing data')



def test_generate_data_plot_confirmed_wrong_argument():
    data_er = process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    # sex or max_age allowed at the same time
    try:
        with raises(NotImplementedError):
            process_covid.generate_data_plot_confirmed(data_er, 'male',60, 'total')
            process_covid.generate_data_plot_confirmed(data_er, 4, None, 'total')
            process_covid.generate_data_plot_confirmed(data_er, None, [], 'total')
        print('wrong argument can be processed correctly')
    except NotImplementedError:
        print('the result is not correct because of wrong argument')



def test_compute_running_average():

    #first test with window 3
    try:
        input = [0,1,5,2,2,5]
        output = []
        output_test = [None, 2.0, 2.6666666666666665, 3.0, 3.0, None]
        output = compute_running_average(input, 3)
        assert output == output_test
        print('correct output')
    except NotImplementedError:
        print('wrong output')

        
    # second test with window 5
    try:
        input2 = [0,1,5,2,2,5,3,5,6,4,2]
        output2 = []
        output2_test = [None, None, 2.0, 3.0, 3.4, 3.4, 4.2, 4.6, 4.0, None, None]
        output2 = compute_running_average(input2,5 )
        assert output2 == output2_test
        print('correct output')
    except NotImplementedError:
        print('wrong output')

    
    # third test with None values
    try:
        input3 = [2,None,4]
        output3 = []
        output3_test =[None, 2.0, None]
        output3=compute_running_average(input3,3)
        assert output3 == output3_test
        print('correct output')
    except NotImplementedError:
        print('wrong output')
        
        
    # forth test with even window 2
    try:
        input4 = [2,None,4]
        output4 = []
        output4_test =[None, 2.0, None]
        with raises(NotImplementedError):
            process_covid.compute_running_average(input4,2)
        print('correct output')
    except NotImplementedError:
        print('wrong output')


def test_simple_derivative():
    try:
        input5 = [None,1,2,None,4]
        output5 = []
        output5_test =[None,None,1,None,None]
        output5=simple_derivative(input5)
        assert output5 == output5_test
        print('correct output')
    except NotImplementedError:
        print('wrong output')

if __name__ == '__main__':
    data_er = process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    pytest.main(["-s", "test_process_covid.py"])