---
author: xxx
---
# AB Testing Project - AB Testing Modeling

## Load in packages
```{r}
library(plm)
library("data.table")
library(stargazer)
library(MatchIt)
```
## Read in Data (Extraction)
```{r}
options(scipen = 100)
MyData<-fread('merged_data.csv', verbose = F)
MyData <- na.omit(MyData)
nrow(MyData)
```
## Preprocessing before modeling
To make data more suitable for analysis, we decide to further aggregate emotion difference data for different emotions into one value.
```{r}
MyData$avg_emot_diff = (abs(MyData$emot_happiness_diff) + abs(MyData$emot_neutral_diff) +
  abs(MyData$emot_sadness_diff) + abs(MyData$emot_surprise_diff)) / 4

mean = mean(MyData$avg_emot_diff)
MyData$emot_match[MyData$avg_emot_diff < mean] <- 1
MyData$emot_match[MyData$avg_emot_diff >= mean] <- 0
```
Have a look at the data here.
```{r}
nrow(MyData)
View(MyData)
```



```{r}
summary(MyData)
```
## modeling part
Our reason for modeling:
1. include fixed-individual effect
2. include time effect (comparing post-quiz correctness with pre-quiz correctness

### Model 1
```{r}
model1 <- lm(correct_post_quiz ~ 
                emot_match +
                correct_pre_quiz +
                factor(demo_age) +
                factor(demo_gender) +
                factor(demo_education),
              data = MyData)
summary(model1)
```
Visualization:

```{r}
stargazer(model1,
          se=list(
            sqrt(diag(vcovHC(model1, method='arellano',type='HC1')))),
          type='text',
          model.numbers=FALSE,
          column.labels=c('OLS model')
          )
```
### Model 2
3. perform psm (score matching) to reduce unseen biases in the samples.
```{r}
set.seed(1979)
Match <- matchit(emot_match ~ correct_pre_quiz +
                   factor(demo_age) +
                   factor(demo_gender) +
                   factor(demo_education),
                 data = MyData,
                 method = 'nearest',
                 distance = 'logit',
                 caliper = 0.001)
summary(Match)
```

```{r}
matched_data <- match.data(Match)
```

```{r}
model2 <- lm(correct_post_quiz ~ 
                emot_match +
                correct_pre_quiz +
                factor(demo_age) +
                factor(demo_gender) +
                factor(demo_education),
              data = matched_data)
summary(model2)
```
### T-test to examine its feasibility and significance

```{r}
t.test(MyData$correct_pre_quiz[MyData$emot_match==0],
       MyData$correct_pre_quiz[MyData$emot_match==1],
       alternative = "two.sided")
```

```{r}
t.test(matched_data$correct_pre_quiz[MyData$emot_match==0],
       matched_data$correct_pre_quiz[MyData$emot_match==1],
       alternative = "two.sided")
```
4. Examine Heterogenous effects of variabls on different features
```{r}
model_hetero <- lm(correct_post_quiz ~
                     emot_match +
                     I(correct_pre_quiz > 1) +
                     emot_match:I(correct_pre_quiz > 1),
                   data = matched_data)
summary(model_hetero)
```
Age effect on emotion sync

```{r}
model_hetero_age <- lm(correct_post_quiz ~ emot_match +I(demo_age == 'e') +emot_match:I(demo_age == 'e'), data = MyData)
summary(model_hetero_age)
```

Camera effect on emotion sync

```{r}
model_hetero_cam <- lm(correct_post_quiz ~
                     emot_match +
                     I(cam_allowed > 0) +
                     emot_match:I(cam_allowed > 0),
                   data = MyData)
summary(model_hetero_cam)
```
Education effect on emotion sync
```{r}
model_hetero_edu <- lm(correct_post_quiz ~
                     emot_match +
                     I(demo_education == 'e') +
                     emot_match:I(demo_education == 'e'),
                   data = MyData)
summary(model_hetero_edu)
```

Visualization:
```{r}
model_hetero <- lm(correct_post_quiz ~emot_match +I(correct_pre_quiz > 1) +emot_match:I(correct_pre_quiz > 1), data = matched_data)
model_hetero_cam <- lm(correct_post_quiz ~emot_match +I(cam_allowed > 0) +emot_match:I(cam_allowed > 0),data = matched_data)
model_hetero_age <- lm(correct_post_quiz ~ emot_match +I(demo_age == 'e') +emot_match:I(demo_age == 'e'), data = matched_data)
model_hetero_edu <- lm(correct_post_quiz ~emot_match +I(demo_education == 'e') +emot_match:I(demo_education == 'e'),data = matched_data)

stargazer(model_hetero,model_hetero_cam,model_hetero_age,model_hetero_edu,
          se=list(
            sqrt(diag(vcovHC(model1, method='arellano',type='HC1')))),
          type='text',
          model.numbers=FALSE,
          column.labels=c('pre-quiz','Camera allowed','age','education')
          )
```







