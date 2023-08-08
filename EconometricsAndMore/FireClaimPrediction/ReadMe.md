# Fire Claim Prediction Using TSA

## Project goal: to facilitate insurance companies in estimating yearly insurance claim size for fires.

## Methodologies

- Establish granularity: how specific of the fire claims to be predicted?
We expect to predict a yearly sum of all fire claims sizes.
- What are our independent variables?
Based on the data available, we decide to estimate fire claims sizes by predicting annual fire accident amounts and losses over different fire intentions.
We can assume that for different reasons of fire, the fire claims sizes vary, and thus the distribution and the prediction model will be different.
- Modeling with Time Series Data
Use a simple ARIMA model to find the most suitable parameters for each model, assign weights and aggregate the results across categories.

## Example Codes
