from forthebirds.forthebirds import eBirdTripPlanner
import pytest
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
token = os.getenv('EBIRD_API_VAR')

def test_class_token_init():
    with pytest.raises(Exception):
        birdplanner = eBirdTripPlanner(country_name='United States')

def test_class_token_input_type():
    with pytest.raises(Exception):
        birdplanner = eBirdTripPlanner(token=123)

def test_api_call_params():
    url = 'https://api.ebird.org/v2/ref/region/list/country/world'
    birdplanner = eBirdTripPlanner(token)
    with pytest.raises(Exception):
        call_result = birdplanner._ebird_api_call(url, params=['a','b'])

def test_api_call():
    url = 'https://api.ebird.org/v2/ref/region/list/country/world'
    birdplanner = eBirdTripPlanner(token)
    call_result = birdplanner._ebird_api_call(url)
    assert isinstance(call_result,list)

def test_bird_info_output():
    birdplanner = eBirdTripPlanner(token)
    rocpig = birdplanner._get_bird_id_info('rocpig')
    assert isinstance(rocpig,str)

def test_country_code_error():
    birdplanner = eBirdTripPlanner(token)
    with pytest.raises(ValueError):
        country_code = birdplanner.find_country_code(find_all=False)

def test_country_code_output():
    expected = 'US'
    birdplanner = eBirdTripPlanner(token, country_name='United States')
    actual = birdplanner.find_country_code(find_all=False)
    assert actual == expected

def test_country_code_list_output():
    birdplanner = eBirdTripPlanner(token)
    country_codes = birdplanner.find_country_code()
    assert isinstance(country_codes,list)

def test_state_code_error():
    birdplanner = eBirdTripPlanner(token,country_name='United States')
    with pytest.raises(ValueError):
        state_code = birdplanner.find_state_code(find_all=False)

def test_state_code_output():
    expected = 'US-NY'
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    actual = birdplanner.find_state_code(find_all=False)
    assert actual == expected

def test_state_code_list_output():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    state_codes = birdplanner.find_state_code()
    assert isinstance(state_codes,list)

def test_substate_code_output():
    expected = 'US-NY-047'
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    actual = birdplanner.find_substate_code(substate_name='Kings',find_all=False)
    assert actual == expected

def test_substate_code_list_output():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    substate_codes = birdplanner.find_substate_code()
    assert isinstance(substate_codes,list)

def test_regional_hotspots_error():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    with pytest.raises(Exception):
        hotspots = birdplanner.get_regional_hotspots(substate_name='Kings')

def test_hotspot_json_list_output():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    hotspots = birdplanner.get_regional_hotspots(json=True)
    assert isinstance(hotspots,list)

def test_hotspot_json_output():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    hotspots = birdplanner.get_regional_hotspots(json=True)
    hotspot = hotspots[0]
    assert isinstance(hotspot,dict)

def test_hotspot_code_except_error():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    with pytest.raises(Exception):
        hotspot_code = birdplanner.find_hotspot_code(substate_name='Kings')

def test_hotspot_code_output_error():
    birdplanner = eBirdTripPlanner(token, 'Oregon', 'United States')
    with pytest.raises(ValueError):
        hotspot_code = birdplanner.find_hotspot_code('Prospect Park')

def test_hotspot_code_output():
    expected = 'L109516'
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    actual = birdplanner.find_hotspot_code('Prospect Park')
    assert actual == expected

def test_recent_region_observations_json_output():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    observations = birdplanner.recent_region_observations(json=True)
    assert isinstance(observations,list)

def test_recent_region_observations_df_output():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    observations = birdplanner.recent_region_observations()
    assert isinstance(observations,pd.DataFrame)

def test_recent_region_observations_no_idinfo():
    expected = ['Common Name',
                 'Scientific Name',
                 'Location Name',
                 'Date Observed',
                 'How Many Observed',
                 'Latitude',
                 'Longitude']
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    observations = birdplanner.recent_region_observations()
    actual = list(observations.columns)
    assert actual == expected

def test_no_recent_region_observations():
    birdplanner = eBirdTripPlanner(token, 'Oregon', 'United States')
    hotspot_name = 'stakeout Snowy Owl, Umatilla Co. (2015)'
    with pytest.raises(ValueError):
        observations = birdplanner.recent_region_observations(hotspot_name=hotspot_name)

def test_recent_rare_region_observations_output():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    observations = birdplanner.recent_rare_region_observations()
    assert isinstance(observations,pd.DataFrame)

def test_recent_rare_region_observations_no_idinfo():
    expected = ['Common Name',
                 'Scientific Name',
                 'Location Name',
                 'Date Observed',
                 'How Many Observed',
                 'Latitude',
                 'Longitude']
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    observations = birdplanner.recent_rare_region_observations()
    actual = list(observations.columns)
    assert actual == expected

def test_recent_species_by_location_no_observations():
    birdplanner = eBirdTripPlanner(token, 'New York', 'United States')
    with pytest.raises(ValueError):
        observations = birdplanner.recent_species_observations_by_location('Southern Cassowary')
