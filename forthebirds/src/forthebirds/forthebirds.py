import requests
import json
import pandas as pd
import re
from bs4 import BeautifulSoup

class eBirdTripPlanner:
    '''
    This class uses the eBird API region endpoints to find recent, notable, and specific species observations for locations
    around the world. Using the eBird API requires obtaining a token, which anyone with an eBird account can do at
    https://ebird.org/api/keygen.

    Parameters
    ----------
    token : String
        Token that can be obtained at https://ebird.org/api/keygen
    state : String, default null
        Full name of desired state to explore
    country : String, default null
        Full name of desired country to explore

    Returns
    -------
    Class object

    Examples
    >>> from forthebirds import eBirdTripPlanner
    >>> eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
    '''

    def __init__(self, token, state_name='', country_name=''):
        assert token, 'eBirdTripPlanner requires use of a token sourced from eBird.org.'
        assert isinstance(token,str), 'API token must be a string.'
        self.token = token
        self.state_name = state_name
        self.country_name = country_name

    def _ebird_api_call(self, url, params={}):
        '''
        Helper function to call eBird API endpoints.

        Parameters
        ----------
        url : String
            The endpoint url of interest
        params = Dict, default null
            Dictionary of parameters for endpoint of interest

        Returns
        -------
        The JSON output of the API call

        Example
        -------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner._ebird_api_call(url='https://api.ebird.org/v2/ref/region/list/country/world')
        [{'code': 'AF', 'name': 'Afghanistan'},
         {'code': 'AL', 'name': 'Albania'},
         {'code': 'DZ', 'name': 'Algeria'},
         {'code': 'AS', 'name': 'American Samoa'},
         ...]

        '''

        assert isinstance(params,dict), 'Parameters must be given in dictionary format.'
        payload={}
        headers = {'X-eBirdApiToken': self.token}

        r = requests.get(url, headers=headers, data=payload, params=params)

        return r.json()

    @staticmethod
    def _find_region_code(region_to_find, region_list, region_type):
        '''
        Helper function to find one region name from a given list of region names. Used for endpoints that require
        region codes that are not intuitive for a user.

        Parameters
        ----------
        region_to_find : String
            The name of the region of interest
        region_list : List
            The list of dictionaries containing region name and region code, found through an endpoint
        region_type : String
            The type of region to search for. Used in an error message if the region is not found. The region types supported
            are 'substate', 'state', and 'country'

        Returns
        -------
        String
            The region code

        Examples
        --------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner._find_region_code('New York', list_of_state_codes, 'state')
        US-NY

        The code of the region (New York State).

        >>> birdplanner._find_region_code('Kings', list_of_ny_counties, 'substate')
        US-NY-047

        The code of the region (Kings County, New York)
        '''

        assert isinstance(region_to_find,str), 'The geography to search for must be a string.'
        assert isinstance(region_list,list), 'Must have a list of regions for region_list input.'

        region_code = ''
        for region in region_list:
            if region['name'].lower() == region_to_find.lower():
                region_code = region['code']

        if region_code:
            return region_code
        else:
            raise ValueError(f'{region_to_find} does not exist within the {region_type} list. Use find_{region_type}_code to see all supported names.')

    @staticmethod
    def _get_bird_id_info(bird_abbr):
        '''
        Helper function to scrape identification information from the eBird website.

        Parameters
        ----------
        bird_abbr : String
            The eBird abbreviation of the species of interest

        Returns
        -------
        String
            A short paragraph with some information on habitat, size, shape, color pattern, and/or behavior of the species
            of interest

        Example
        -------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner._get_bird_id_info('amewoo')
        'Plump, well-camouflaged shorebird that favors wooded or shrubby areas, usually near open fields. Plain
        buffy-salmon belly distinctive; also note intricately patterned upperparts with broad gray stripes down the back.
        Goofy-looking expression with huge dark eye placed high and far back on head. Extremely long bill used to probe the
        ground for worms. When flushed from dense cover, listen for high-pitched wing twittering and note rotund shape and
        long bill. Might be confused with Wilson’s Snipe, but woodcock is not nearly as dark and patterned. Fairly common
        throughout eastern North America, but secretive and rarely seen well in daytime. Always on the ground, except during
        well-known elaborate courtship display performed from dusk to dawn in spring. Listen for loud nasal “PEENT!” calls
        from the ground and high-pitched chirps and twitters (produced by the outer wing feathers) from high in the sky.'

        The identifying information for the American Woodcock ('amewoo').
        '''

        url = f'https://ebird.org/species/{bird_abbr}'
        page = requests.get(url)

        birdsoup = BeautifulSoup(page.text, 'html.parser')
        taginfo = str(birdsoup.find('meta', property='og:description'))
        birdid = re.search(r'(content=\")([^\"]*)',taginfo).group(2).strip()

        return birdid

    def find_country_code(self, find_all=True):
        '''
        Function to find the code of the country given when the class was instantiated or to view all supported country
        names. Default is to view all supported country names.

        Parameters
        ----------
        find_all : Boolean, default True
            If True, will return a list of country names

        Returns
        -------
        String of one specified country code or List of all supported country names

        Examples
        --------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner.find_country_code()
        ['Afghanistan',
         'Albania',
         'Algeria',
         'American Samoa',
         ...]

        A list of supported country names.

        >>> birdplanner.find_country_code(find_all=False)
        'US'

        The country code given for the United States, the country given when the class was instantiated.
        '''

        url = 'https://api.ebird.org/v2/ref/region/list/country/world'
        countries = self._ebird_api_call(url)
        if find_all:
            country_names = [country['name'] for country in countries]
            return country_names
        else:
            if self.country_name:
                country_code = self._find_region_code(self.country_name, countries, 'country')
                return country_code
            else:
                raise ValueError('Class instantiated without a country name.')

    def find_state_code(self, find_all=True):
        '''
        Function to find the code of the state given when the class was instantiated or to view all supported state names.
        Default is to view all supported state names.

        Parameters
        ----------
        find_all : Boolean, default True
            If True, will return a list of state names within the country used when class was instantiated.

        Returns
        -------
        String of one specified state code or List of all supported state names

        Examples
        --------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner.find_state_code()
        ['Alabama',
         'Alaska',
         'Arizona',
         'Arkansas',
         'California',
         ...]

        A list of supported state names.

        >>> birdplanner.find_substate_code(find_all=False)
        US-NY

        The region code of New York State in the United States, both given when the class was instantiated.
        '''

        country_code = self.find_country_code(find_all=False)
        url = f'https://api.ebird.org/v2/ref/region/list/subnational1/{country_code}'
        states = self._ebird_api_call(url)
        if find_all:
            state_names = [state['name'] for state in states]
            return state_names
        else:
            if self.state_name:
                state_code = self._find_region_code(self.state_name, states, 'state')
                return state_code
            else:
                raise ValueError('Class instantiated without a state name.')

    def find_substate_code(self, substate_name='', find_all=True):
        '''
        Function to find the code of a given substate (in the United States, the county) from the state input when the class
        was instantiated or to view all supported substate (county) names. Default is to view all supported substate names.

        Parameters
        ----------
        substate_name : String, default null
            The name of the substate or county of interest. This defaults to null to support the find_all function.
        find_all : Boolean, default True
            If True, will return a list of county names within the state used when class was instantiated.

        Returns
        -------
        String of one specified substate code or List of all supported substate names

        Examples
        --------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner.find_substate_code()
        ['Albany',
         'Allegany',
         'Bronx',
         'Broome',
         'Cattaraugus',
         'Cayuga',
         ...]

        A list of supported substate (county) names.

        >>> birdplanner.find_substate_code(substate='Kings',find_all=False)
        US-NY-047

        The region code of Kings County in New York State in the United States, the latter two given when the class was
        instantiated.
        '''
        country_code = self.find_country_code(find_all=False)
        state_code = self.find_state_code(find_all=False)
        url = f'https://api.ebird.org/v2/ref/region/list/subnational2/{state_code}'
        substates = self._ebird_api_call(url)
        if find_all:
            substate_names = [substate['name'] for substate in substates]
            return substate_names
        else:
            substate_code = self._find_region_code(substate_name, substates,'substate')
            return substate_code

    def get_regional_hotspots(self, substate_name='', region_type='state', json=False):
        '''
        Function to list the birding hotspots at either substate or state level, and can return in either a user-friendly
        dataframe or a json dictionary. The state-level search will return hotspots for the state name given when the class
        was instantiated.

        Parameters
        ----------
        substate_name : String, default null
            The name of the substate or county of interest. This defaults to null to support state-level searches.
        region_type : String, default 'substate'
            The level of region at which to search for hotspots. Must be indicator of 'state' or 'substate'. Defaults to
            'state'.
        json : Boolean, default False
            Indicates whether or not to return results in JSON or DataFrame.

        Returns
        -------
        DataFrame or JSON of all hotspots within the given region

        Examples
        --------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner.get_regional_hotspots(json=True)
        A JSON dictionary of all hotspots within New York State.

        >>> birdplanner.get_regional_hotspots('Kings', region_type='substate')
        A DataFrame of all hotspots within Kings County in New York State.
        '''
        if substate_name:
            assert region_type == 'substate', 'If substate_name is given, region_type must be substate.'
        if region_type == 'substate':
            region_code = self.find_substate_code(substate_name, find_all=False)
        elif region_type == 'state':
            region_code = self.find_state_code(find_all=False)

        url = f'https://api.ebird.org/v2/ref/hotspot/{region_code}'
        hotspots = self._ebird_api_call(url, params={'fmt':'json'})
        if json:
            return hotspots
        else:
            hotspot_df = pd.DataFrame(hotspots)[['locId', 'locName', 'lat', 'lng', 'latestObsDt', 'numSpeciesAllTime']]
            rename_cols = {'locId':'Location ID', 'locName':'Location Name', 'lat':'Latitude', 'lng':'Longitude',
                          'latestObsDt':'Latest Observation Date', 'numSpeciesAllTime':'Number of Species'}
            hotspot_df = hotspot_df.rename(columns=rename_cols)
            return hotspot_df

    def find_hotspot_code(self, hotspot_name, substate_name='', region_type='state'):
        '''
        Function to find the region code of a given birding hotspot within the state input at class instantiation, or within
        a substate if hotspot names are non-unique.

        Parameters
        ----------
        hotspot_name : String
            The name of the hotspot of interest
        substate_name : String, default null
            The name of the substate or county of interest. This defaults to null to support state-level searches.
        region_type : String, default 'state'
            The level of region at which to search for the hotspot name. Must be indicator of 'state' or 'substate'.
            Defaults to 'state'.

        Returns
        -------
        String
            Location code of the hotspot in question

        Example
        -------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner.find_hotspot_code(hotspot_name='Prospect Park')
        L109516

        The location code of Prospect Park, a birding hotspot, in New York.
        '''
        if substate_name:
            assert region_type == 'substate', 'If substate_name is given, region_type must be substate.'
        assert region_type in ('substate', 'state'), 'Region type must be substate or state to find a hotspot.'

        hotspot_list = self.get_regional_hotspots(substate_name, region_type, json=True)

        hotspot_code = ''
        for hotspot in hotspot_list:
            if hotspot['locName'] == hotspot_name:
                hotspot_code = hotspot['locId']

        if hotspot_code:
            return hotspot_code
        else:
            raise ValueError('This hotspot does not exist within the given region.')

    def recent_region_observations(self, hotspot_name='', substate_name='', region_type='state', idinfo=False,
                                   days_back=14, locations=[], only_hotspots=False, json=False):
        '''
        Function to find recent bird observations within a region. The user can look at a hotspot, substate, state, or
        country level. This function can also return identification information for each bird record. Default is to return
        observations at the state level.

        Parameters
        ----------
        hotspot_name : String, default null
            The name of a birding hotspot. This defaults to null to support state-level searches.
        substate_name : String, default null
            The name of a substate or county of interest. This defaults to null to support state-level searches.
        region_type : String, default null
            The level of region at which to search for the hotspot name. Must be indicator of 'substate', 'state', or
            'country'. Defaults to 'state'.
        idinfo : Boolean, default False
            Flag to indicate whether the function should return bird identification information with each record. This
            scrapes eBird.org. Default is False because it significantly slows down the function.
        days_back : Int, default 14
            The number of days to look back for observations. The limit of the API for recent observations is 30 days.
            Default is set to 14 because that is the API default.
        locations : List, default null
            A list of up to 10 location IDs (hotspot, substate, state, or country) to pull recent observations from.
        only_hotspots : Boolean, default False
            Flag to indicate whether to only return bird observations from hotspot locations.
        json : Boolean, default False
            Flag to indicate whether to return results in JSON or DataFrame.

        Returns
        -------
        DataFrame or JSON of recent bird observations within a geography

        Examples
        -------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner.recent_region_observations()
        DataFrame of observations within the last 14 days in New York State.

        >>> birdplanner.recent_region_observations(hotspot_name='Prospect Park', idinfo=True, days_back=30, json=True)
        JSON of observations within the last 30 days in Prospect Park (New York), with bird ID info for each record.
        '''
        if locations:
            region_code = ''
        elif hotspot_name:
            region_code = self.find_hotspot_code(hotspot_name, substate_name, region_type)
        elif region_type == 'substate':
            region_code = self.find_substate_code(substate_name, find_all=False)
        elif region_type == 'state':
            region_code = self.find_state_code(find_all=False)
        elif region_type == 'country':
            region_code = self.find_country_code(find_all=False)

        params={'back':days_back, 'r':locations, 'hotspot':only_hotspots}

        url = f'https://api.ebird.org/v2/data/obs/{region_code}/recent'
        observations = self._ebird_api_call(url,params=params)

        if len(observations) == 0:
            raise ValueError('No recent observations in this location.')

        if idinfo:
            for obs in observations:
                birdabb = obs['speciesCode']
                obs['ID Info'] = self._get_bird_id_info(birdabb)
                obs_df = pd.DataFrame(observations)[['comName', 'sciName', 'locName', 'obsDt', 'howMany', 'lat', 'lng', 'ID Info']]
        else:
            obs_df = pd.DataFrame(observations)[['comName', 'sciName', 'locName', 'obsDt', 'howMany', 'lat', 'lng']]

        if json:
            return observations
        else:
            rename_cols = {'comName':'Common Name', 'sciName':'Scientific Name','locName':'Location Name', 'obsDt':'Date Observed',
                           'howMany':'How Many Observed', 'lat':'Latitude', 'lng':'Longitude'}
            obs_df = obs_df.rename(columns=rename_cols)
            return obs_df

    def recent_rare_region_observations(self, hotspot_name='', substate_name='', region_type='state', idinfo=False,
                                        days_back=14, locations=[], only_hotspots=False):
        '''
        Function to find rare and recent bird observations within a region. The user can look at a hotspot, substate, state,
        or country level. This function can also return identification information for each bird record. Default is to return
        observations at the state level.

        Parameters
        ----------
        hotspot_name : String, default null
            The name of a birding hotspot. This defaults to null to support state-level searches.
        substate_name : String, default null
            The name of a substate or county of interest. This defaults to null to support state-level searches.
        region_type : String, default null
            The level of region at which to search for the hotspot name. Must be indicator of 'substate', 'state', or
            'country'. Defaults to 'state'.
        idinfo : Boolean, default False
            Flag to indicate whether the function should return bird identification information with each record. This
            scrapes eBird.org. Default is False because it significantly slows down the function.
        days_back : Int, default 14
            The number of days to look back for observations. The limit of the API for recent observations is 30 days.
            Default is set to 14 because that is the API default.
        locations : List, default null
            A list of up to 10 location IDs (hotspot, substate, state, or country) to pull recent observations from.
        only_hotspots : Boolean, default False
            Flag to indicate whether to only return bird observations from hotspot locations.

        Returns
        -------
        DataFrame of recent rare bird observations within a geography

        Examples
        -------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner.recent_rare_region_observations()
        DataFrame of rare observations within the last 14 days in New York State.

        >>> birdplanner.recent_rare_region_observations(hotspot_name='Prospect Park', idinfo=True, days_back=30)
        DataFrame of rare observations within the last 30 days in Prospect Park (New York), with bird ID info for each
        record.
        '''
        if locations:
            region_code = ''
        elif hotspot_name:
            region_code = self.find_hotspot_code(hotspot_name, substate_name, region_type)
        elif region_type == 'substate':
            region_code = self.find_substate_code(substate_name, find_all=False)
        elif region_type == 'state':
            region_code = self.find_state_code(find_all=False)
        elif region_type == 'country':
            region_code = self.find_country_code(find_all=False)

        params={'back':days_back, 'r':locations, 'hotspot':only_hotspots}

        url = f'https://api.ebird.org/v2/data/obs/{region_code}/recent/notable'
        observations = self._ebird_api_call(url,params=params)

        if idinfo:
            for obs in observations:
                birdabb = obs['speciesCode']
                obs['ID Info'] = self._get_bird_id_info(birdabb)
                obs_df = pd.DataFrame(observations)[['comName', 'sciName', 'locName', 'obsDt', 'howMany', 'lat', 'lng', 'ID Info']]
        else:
            obs_df = pd.DataFrame(observations)[['comName', 'sciName', 'locName', 'obsDt', 'howMany', 'lat', 'lng']]

        obs_df['obsDt'] = pd.to_datetime(obs_df['obsDt']).dt.date
        rename_cols = {'comName':'Common Name', 'sciName':'Scientific Name', 'locName':'Location Name', 'obsDt':'Date Observed',
                      'lat':'Latitude', 'lng':'Longitude', 'howMany':'How Many Observed'}
        obs_df = obs_df.rename(columns=rename_cols)
        obs_df_deduped = obs_df.drop_duplicates().reset_index(drop=True)
        return obs_df_deduped

    def recent_species_observations_by_location(self, bird_name, hotspot_name='', substate_name='',
                                                region_type='state', idinfo=False, days_back=14, locations=[],
                                                only_hotspots=False):
        '''
        Function to find recent observations of a specific species within a region. The user can look at a hotspot, substate,
        state, or country level. This function can also return identification information for each bird record. Default is to
        return observations at the state level.

        Parameters
        ----------
        hotspot_name : String, default null
            The name of a birding hotspot. This defaults to null to support state-level searches.
        substate_name : String, default null
            The name of a substate or county of interest. This defaults to null to support state-level searches.
        region_type : String, default null
            The level of region at which to search for the hotspot name. Must be indicator of 'substate', 'state', or
            'country'. Defaults to 'state'.
        idinfo : Boolean, default False
            Flag to indicate whether the function should return bird identification information with each record. This
            scrapes eBird.org. Default is False because it significantly slows down the function.
        days_back : Int, default 14
            The number of days to look back for observations. The limit of the API for recent observations is 30 days.
            Default is set to 14 because that is the API default.
        locations : List, default null
            A list of up to 10 location IDs (hotspot, substate, state, or country) to pull recent observations from.
        only_hotspots : Boolean, default False
            Flag to indicate whether to only return bird observations from hotspot locations.

        Returns
        -------
        DataFrame of recent specific species observations within a geography

        Examples
        -------
        >>> birdplanner = eBirdTripPlanner(token='abc123', state_name='New York', country_name='United States')
        >>> birdplanner.recent_rare_region_observations()
        DataFrame of rare observations within the last 14 days in New York State.

        >>> birdplanner.recent_rare_region_observations(hotspot_name='Prospect Park', idinfo=True, days_back=30)
        DataFrame of rare observations within the last 30 days in Prospect Park (New York), with bird ID info for each
        record.
        '''
        region_observations = self.recent_region_observations(hotspot_name=hotspot_name, substate_name=substate_name,
                                                              region_type=region_type, days_back=days_back,
                                                              locations=locations, only_hotspots=only_hotspots, json=True)

        if locations:
            region_code = ''
        elif hotspot_name:
            region_code = self.find_hotspot_code(hotspot_name, substate_name, region_type)
        elif region_type == 'substate':
            region_code = self.find_substate_code(substate_name, find_all=False)
        elif region_type == 'state':
            region_code = self.find_state_code(find_all=False)
        elif region_type == 'country':
            region_code = self.find_country_code(find_all=False)

        species_code = ''
        for reg_obs in region_observations:
            if reg_obs['comName'].lower() == bird_name.lower():
                species_code = reg_obs['speciesCode']

        params={'back':days_back, 'r':locations, 'hotspot':only_hotspots}

        if species_code:
            url = f'https://api.ebird.org/v2/data/obs/{region_code}/recent/{species_code}'
            species_observations = self._ebird_api_call(url, params=params)
            species_observation_info = [{key:obs[key] for key in obs.keys() & {'comName', 'sciName', 'locName', 'howMany', 'obsDt'}} for obs in species_observations]

            if idinfo:
                for observation in species_observation_info:
                    observation['ID Info'] = self._get_bird_id_info(species_code)

            species_df = pd.DataFrame(species_observation_info)
            rename_cols = {'comName':'Common Name', 'sciName':'Scientific Name', 'locName':'Location Name',
                           'howMany':'Number of Observations', 'obsDt':'Date Observed'}
            species_df = species_df.rename(columns=rename_cols)
            return species_df
        else:
            if hotspot_name:
                raise ValueError(f'No recent observations of {bird_name} in {hotspot_name}.')
            elif substate_name:
                raise ValueError(f'No recent observations of {bird_name} in {substate_name}.')
            else:
                raise ValueError(f'No recent observations of {bird_name} in {self.state_name}.')
