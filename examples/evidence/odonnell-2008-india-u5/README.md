# O'Donnell et al. 2008, Table 8.1 — India under-five deaths (REPRODUCED)

O'Donnell, van Doorslaer, Wagstaff and Lindelow, *Analyzing Health Equity Using Household Survey Data: A Guide to Techniques and Their Implementation*, World Bank, 2008. Chapter 8, Table 8.1. DOI [10.1596/978-0-8213-6933-3](https://doi.org/10.1596/978-0-8213-6933-3). Licence **CC BY 3.0 IGO** ([Open Knowledge Repository](https://openknowledge.worldbank.org/entities/publication/8c581d2b-ea86-56f4-8e9d-fbde5419bc2a/full)).

The table is five wealth quintiles of Indian births, 1982–92, with under-five mortality rates and implied deaths. Chapter 8 defines the concentration index as twice the area between the concentration curve and the line of equality, and computes it from this table with the grouped Kakwani formula (8.4). The printed result is **−0.1694**. The negative sign is the higher mortality among poorer children.

This repository redistributes the five-row table with attribution. That is permitted under CC BY 3.0 IGO; it is not an endorsement by the World Bank.

moveq's documented method is the covariance form of the same index (`wagstaff-covariance`) on the five U5MR rows, weighted by births, ranked by wealth (`higher_is_advantaged`). The independent grouped-rank oracle in `oracles.py` agrees with −0.1694 to the four decimal places the book reports. This is a reproduction of the published grouped example, not a reconstruction from NFHS microdata.
