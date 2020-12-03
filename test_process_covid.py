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
    data_json = process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    assert data_json is not None



def test_rebin():
    # test 1
    A = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-']
    B = ['0-19', '20-39', '40-']
    result_correct=['0-19', '20-39', '40-']

    input_data=process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    input_data['metadata']['age_binning']['hospitalizations']=A
    input_data['metadata']['age_binning']['population']=B
    result_original=cases_per_population_by_age(input_data)
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

    input_data=process_covid.load_covid_data('covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json')
    input_data['metadata']['age_binning']['hospitalizations']=A
    input_data['metadata']['age_binning']['population']=B
    with pytest.raises(ValueError):
        assert list(process_covid.cases_per_population_by_age(input_data).keys())