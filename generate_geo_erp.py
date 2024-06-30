import pandas as pd

sa1_erp_file = "./inputs/sa1_erp/sa1_erp.csv"
meshblock_count_file = "./inputs/abs_data/meshblock_count.csv"
sa1_allocation_file = "./inputs/abs_data/statistical_area_allocation.xlsx"

# Required information for the outputs we want to generate
output_geographies = {
    'suburbs_and_localities': {
        'file': './inputs/abs_data/suburb_localities_allocation.xlsx',
        'mb_code_col': 'MB_CODE_2021',
        'geo_code_col': 'SAL_CODE_2021',
        'keep_cols': ['SAL_CODE_2021', 'SAL_NAME_2021', 'STATE_CODE_2021','STATE_NAME_2021']
    },
    'lga_2021': {
        'file': './inputs/abs_data/lga_2021_allocation.xlsx',
        'mb_code_col': 'MB_CODE_2021',
        'geo_code_col': 'LGA_CODE_2021',
        'keep_cols': ['LGA_CODE_2021', 'LGA_NAME_2021', 'STATE_CODE_2021','STATE_NAME_2021']
    },
    'lga_2022': {
        'file': './inputs/abs_data/lga_2022_allocation.xlsx',
        'mb_code_col': 'MB_CODE_2021',
        'geo_code_col': 'LGA_CODE_2022',
        'keep_cols': ['LGA_CODE_2022', 'LGA_NAME_2022', 'STATE_CODE_2021','STATE_NAME_2021']
    },
    'lga_2023': {
        'file': './inputs/abs_data/lga_2023_allocation.xlsx',
        'mb_code_col': 'MB_CODE_2021',
        'geo_code_col': 'LGA_CODE_2023',
        'keep_cols': ['LGA_CODE_2023', 'LGA_NAME_2023', 'STATE_CODE_2021','STATE_NAME_2021']
    },
    'postal_areas': {
        'file': './inputs/abs_data/postal_areas_allocation.xlsx',
        'mb_code_col': 'MB_CODE_2021',
        'geo_code_col': 'POA_CODE_2021',
        'keep_cols': ['POA_CODE_2021', 'POA_NAME_2021']
    },
    'destination_zone': {
        'file': './inputs/abs_data/destination_zone_allocation.xlsx',
        'mb_code_col': 'MB_CODE_2021',
        'geo_code_col': 'DZN_CODE_2021',
        'keep_cols': ['DZN_CODE_2021', 'SA2_CODE_2021', 'SA2_NAME_2021', 'STATE_CODE_2021', 'STATE_NAME_2021']
    }
}

# Read in inputs and clean
print("Loading SA1 ERPs...")
sa1_erp = pd.read_csv(sa1_erp_file, index_col=0)
sa1_erp.index = sa1_erp.index.astype(str)

print("Loading meshblock counts...")
meshblock_count = pd.read_csv(meshblock_count_file, index_col=0).filter(['Person'])
meshblock_count.index = meshblock_count.index.astype(str)

print("Loading SA1 allocation file...")
meshblock_sa1_alloc = pd.read_excel(sa1_allocation_file, index_col=0).filter(['SA1_CODE_2021'])
meshblock_sa1_alloc.index = meshblock_sa1_alloc.index.astype(str)
meshblock_sa1_alloc['SA1_CODE_2021'] = meshblock_sa1_alloc['SA1_CODE_2021'].astype(str)

# Merge the counts into the allocation dataframe
print("Making meshblock ERPs...")
meshblock_sa1_alloc = pd.merge(meshblock_sa1_alloc, meshblock_count, how='inner', on='MB_CODE_2021')

# Use the allocations to apportion each SA1 into meshblocks based on counts
# If the sum of the counts is zero, apportion evenly across the underlying meshblocks
grouped_sum = meshblock_sa1_alloc.groupby('SA1_CODE_2021')['Person'].transform('sum')
grouped_count = meshblock_sa1_alloc.groupby('SA1_CODE_2021')['Person'].transform('count')

def apportion_count(row):
    if grouped_sum[row.name] != 0:
        return row['Person'] / grouped_sum[row.name]
    else:
        return 1 / grouped_count[row.name]

meshblock_sa1_apportionment = meshblock_sa1_alloc
meshblock_sa1_apportionment['Person'] = meshblock_sa1_apportionment.apply(apportion_count, axis=1)

meshblock_erp = meshblock_sa1_apportionment.merge(sa1_erp, left_on='SA1_CODE_2021', right_on='SA1', how='left').set_index(meshblock_sa1_apportionment.index).fillna(0)

for name in sa1_erp:
    meshblock_erp[name] = meshblock_erp[name] * meshblock_erp['Person']

meshblock_erp = meshblock_erp.drop(['Person', 'SA1_CODE_2021'], axis=1)

#meshblock_erp.to_csv('outputs/meshblock_erp.csv')

# Create ERP tables for all the other geographies
print("Working on outputs...")
print("\n")

for key in output_geographies.keys():
    # Load in inputs
    print(f"Working on {key}...")
    allocation_file = output_geographies[key]['file']
    output_file = f'outputs/{key}.csv'
    mb_code_col = output_geographies[key]['mb_code_col']
    geo_code_col = output_geographies[key]['geo_code_col']
    cols_to_keep = output_geographies[key]['keep_cols']
    
    print(f"Loading allocation file...")
    geo_allocation = pd.read_excel(allocation_file)
    
    # Merge the meshblock ERPs into the allocation file
    print(f"Merging meshblock ERP table...")
    geo_erp = geo_allocation.merge(meshblock_erp, left_on=mb_code_col, right_on='MB_CODE_2021', how='inner')
    
    # Group by geography code and sum to get the total ERP for the geography
    print(f"Making geo ERPs...")
    geo_erp = geo_erp.groupby(geo_code_col)[meshblock_erp.columns].sum()
    
    # Re-add the columns we want to keep and drop any duplicates
    print(f"Making output table...")
    geo_erp = geo_allocation.filter(cols_to_keep).merge(geo_erp, on=geo_code_col).drop_duplicates()
    
    # Write the table to the output file
    print(f"Writing table to file...")
    geo_erp.to_csv(output_file, index=False)
    print("\n")

print("Finished.")
