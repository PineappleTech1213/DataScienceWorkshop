# Statistical Data Analytics on Bio-information

## 1 Power Calculation to Estimate Sample Size

How to estimate the least sample size required for conducting a clinical trial? First, we need to know what the clinical trial is for.

For this trial, we have a sample data of 100 patients in a placebo arm, measured at baseline, month 3 and month 6. First we estimate the sample size for the first three months' experiments.

The common procedure for power calculations:

- Acquire the power (confidence level/significance level) of the trial
- Understand the trial goal: what statement to reject? double-sided or single sided?
- Confirm the border line requirement: reduce Type I or Type II error?
- Use appropiate test statistics: for two sample tests, use F or T tests. For one sample test, use Chi-square or Z test.

We would use the T statistic to test the hypothesis that the addition of Palofenac to treat patients with high LDL cholesterol level and Statin treatment for over a year.

Let X be the percentage reduction in LDL cholesterol level compared to baseline after 3 months of treatment of Palofenac, and Y be the percentage reduction without the treatment of Palofenac. Let 1 be the standard variance for the treatment group, 2 be the true deviation for the control group, and n1 the sample size for X and n2 that for Y.
And the hypothesis is 

H0: Y - X<=0.2           vs              H1: Y - X>=0.2 

Thus the test statistics goes like

T = (Y-X- 0.2)/(sigma1^2/n1+ sigma2^2/n2) 

And we need to estimate n1  and  n2. Let n = n1=n2, and X and Y share the same standard deviation s. We use the sample data to estimate Y and s (Appendix 2).

 1, 2 -> s/n , thus  T = (Y-X- 0.2)/s2/n  ~ Tdf = 100-1 , with Y = Y=0.08, and s =0.3  .

Under the null hypothesis, to reject the null hypothesis, we have the following equation

 T <=0 -> P(T <=0)  <= t(1-power)/2.

Since for this trial, we need to maintain a two-sided Type I error of 5% and a power of at least 90%, we would have this equation

 P(T <=0)  <= t0.05 ->(0.08-0.2)/s2/n  <= -1.66.

Let’s substitute T with the sample mean value from the previous study and we have

n >= (1.66/(0.2-0.08) *0.3 * 2)2   = 34.445 ≈ 35.

Considering the dropout rate of 6%, the final desired sample size would be 

2 *  n *(1+dropout %) = 73.001 ≈74

Thus, the total sample size should be at least 74, with 37 in both the placebo arm and the Palofenac arm.

