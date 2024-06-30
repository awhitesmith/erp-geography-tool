# ERP geography tool

Simple Python script to generate estimated resident population (ERP) series for geographies published by the Australian Bureau of Statistics (ABS).

The table below links to the outputs of the script, being ERP series from 2011 to 2023 for a number of ABS geographies.

| Geography  | Output file |
| ------------- | ------------- |
| Suburbs and localities  | [suburbs_and_localities.csv](outputs/suburbs_and_localities.csv)  |
| LGA 2021  | [lga_2021.csv](outputs/lga_2021.csv)  |
| LGA 2022  | [lga_2022.csv](outputs/lga_2022.csv)  |
| LGA 2023  | [lga_2023.csv](outputs/lga_2023.csv)  |
| Postal areas  | [postal_areas.csv](outputs/postal_areas.csv)  |
| Destination zone  | [destination_zones.csv](outputs/destination_zone.csv)  |

## Calculation

Population estimates for each SA1 (published by the [Queensland Government Statistician's Office](https://www.qgso.qld.gov.au/statistics/theme/population/population-estimates/regions)) are apportioned into their constituent meshblocks on a pro-rata basis with respect to counts from the 2021 Census. This gives population estimates for meshblocks. As meshblocks form the basis of all ABS-published geographies, meshblock population estimates are combined to form population estimates for higher-level geographies.
