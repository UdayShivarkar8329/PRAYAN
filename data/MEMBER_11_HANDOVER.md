# PRAYAN - Member 11 Handover

## Role
Member 11 - Data Preparation + Admin Support

## Completed Work

Prepared and organized realistic fictional test data for:

- Cars
- Drivers
- Bookings
- Data validation

## Files Created

- data/sample_cars.sql
- data/sample_drivers.sql
- data/sample_bookings.sql
- data/data_validation.sql

## Database Validation

Current Aiven database validation results:

- Users: 3
- Cars: 2
- Drivers: 2
- Bookings: 7

Service types verified:

- Car Only: 2
- Driver Only: 2
- Car + Driver: 3

## Data Integrity Checks

The following checks passed:

- Car seat values are positive.
- Car prices are positive.
- Driver experience values are valid.
- Driver prices are positive.
- Car availability values are valid.
- Driver availability values are valid.
- Booking dates are valid.
- Booking -> User relationships are valid.
- Booking -> Car relationships are valid.
- Booking -> Driver relationships are valid.
- Car Only bookings contain a car and no driver.
- Driver Only bookings contain a driver and no car.
- Car + Driver bookings contain both car and driver.

## Test Data

All sample data prepared by Member 11 is fictional/demo data
and is intended for development and testing only.

## Important Note

The sample booking SQL contains test pricing assumptions.
The final pricing formula should follow the project's implemented
booking/pricing logic once finalized by the development team.

## Security

No database password or private connection information is included
in the repository.

The local .env file is excluded through .gitignore.

## Handover

Member 11 data files and validation queries are ready for use by
the development and testing team.