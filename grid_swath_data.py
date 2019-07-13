"""
===============================
Jeb Jeffery
July 1, 2019
Satellite Swath Gridder
===============================
Grids Level-2 satellite data
without interpolation
===============================
Python 3.7.3
===============================
"""

##-- Import Packages --##
import numpy as np

##-- Function that creates of latitudes and longitudes based upon grid resolution --##
def create_grid(grid_resolution):
    ##-- Define starting points in grid
    lat_start = - 90.0
    lat_end = 90.0 + grid_resolution
    lon_start = -180.0
    lon_end = 180.0 + grid_resolution
    grid_spacing = float(grid_resolution)
    ##-- Create grid --##
    grid_lons, grid_lats = np.mgrid[lon_start:lon_end:grid_spacing, lat_start:lat_end:grid_spacing]
    ##-- Return Grid --##
    return grid_lons, grid_lats

##-- Define function that grids satellite data without interpolation
def grid_swath_data(lons, lats, data, grid_lons, grid_lats):
    
    ##-- Define starting points in grids
    lon_start = grid_lons[0,0]
    lat_start = grid_lats[0,0]
    
    ##-- Calculate grid resolution by finding difference between two points --##
    grid_resolution = float(grid_lons[1,0] - grid_lons[0,0])
    
    ##-- Retrieve dimensions of 1D ungridded data and passed 2D grids --##
    # Get 1D shape of input data array
    data_length = len(data)
    # Get 2D shape from lons and lats grid
    stack_dimensions = grid_lons.shape
    
    ##-- Function that rounds longitudes and latitudes to nearest grid point --##
    def round_coordinate_to_grid(value):
        reciprical = 1.0 / grid_resolution
        return np.round_(value * reciprical) / reciprical
    
    ##-- Function that gets index in 2D longitude array for ungridded point --##
    def get_longitude_index(value):
        return int((round_coordinate_to_grid(value) - lon_start) / grid_resolution)
    
    ##-- Function that gets index in 2D longitude array for ungridded point --##
    def get_latitude_index(value):
        return int((round_coordinate_to_grid(value) - lat_start) / grid_resolution)
    
    ##-- Initialize 1D arrays that relate ungridded geocoordinates to the defined grid --##
    data_longitude_indicies = np.zeros((data_length))
    data_latitude_indicies = np.zeros((data_length))
    
    ##-- Initialize 2D array to hold stack indices for each grid point --##
    # NOTE: Indicies start at 0 and increase whenever a data value is added to a particular grid point
    data_stack_indicies = np.zeros((stack_dimensions))
    
    ##-- Calculate Geocoordinate indices for ungridded data --##
    # Loop through the lons, lats, and data values for ungridded data
    for point_index in np.arange(0, data_length, 1):
        
        ##-- Calculate indicies for longitudes and latidudes of ungridded data points --##
        lon_index = get_longitude_index(lons[point_index])
        lat_index = get_latitude_index(lats[point_index])
        
        ##-- Pass geocoordinate incidies for ungridded data points into their respective 1D arrays --##
        data_longitude_indicies[point_index] = lon_index
        data_latitude_indicies[point_index] = lat_index
        
        ##--  Update stack index for current grid point --##
        data_stack_indicies[lon_index, lat_index]+= 1

    # Calculate stack height of 3D stacked data array as value of the most populated grid point
    stack_height = int(np.max(data_stack_indicies))
    
    ##-- Create a 3D stacked array to hold gridded data --##
    # Create stacked array using the grid dimensions and stack height
    data_stack = np.zeros((stack_height, stack_dimensions[0], stack_dimensions[1]))
    # Fill stacked array with nan values as a default
    data_stack.fill(np.nan)
    
    ##-- Reset stack indicies before gridding data --##
    data_stack_indicies.fill(0)
    
    ##-- Grid data onto 3D stacked grid --##
    # Loop through the lons, lats, and data values for ungridded data
    for point_index in np.arange(0, data_length, 1):
        
        ##-- Calculate index for longitudes and latidudes of ungridded point --##
        lon_index = int(data_longitude_indicies[point_index])
        lat_index = int(data_latitude_indicies[point_index])
        
        ##-- Get stack index for current grid point --##
        stack_index = int(data_stack_indicies[lon_index, lat_index])
        
        ##--  Update stack index fr current grid point --##
        data_stack_indicies[lon_index, lat_index]+= 1
        
        ##-- Pass current ungridded data value data to stacked array --##
        data_stack[stack_index, lon_index, lat_index] = data[point_index]
    
    ##-- Return gridded 2D data by averaging 3D stacked array --##
    return np.nanmean(data_stack, axis=0)