# Imitate Stochastic Process of The Interval Geysers at Yellonstone

## Goal: can we estimate and predict the eruptions of those geysers at Yellowstone using Markov Chain Theories?

## Step 1: Data preprocessing

Read in the data.

```{r}

library(data.table)
library(dplyr)
library(ggplot2)

geyser <- as.data.frame(fread('geysertimes_eruptions_complete_2019-05-31.tsv',quote = ''))
```

Let's filter the data from 1970 and generated a mapped of the before and after geysers.

```{R message=FALSE,warning=FALSE}
geyser$eruption_time_epoch <- as.POSIXct(geyser$eruption_time_epoch,
                                         origin='1970-01-01')
#arrange the records by time
geysertrans <- geyser%>%select(eruption_time_epoch,geyser,duration)%>%
  arrange(eruption_time_epoch)
#extracted geysers after one epoch
geyser1 <- geysertrans$geyser
geyser2 <- geyser1[-1]
geyser2 <- append(geyser2,'norecord')
#combine the prev and aftergeyser
sequal <- data.frame(before=geyser1,after=geyser2)
sequal<- sequal[1:nrow(sequal)-1,]
sequal[,'times'] <- 1
trans <- aggregate(times~before+after,data = sequal,FUN = sum)
states<- trans
#acquire the names of the irreducible states
absorbstate <- c('Daisy', 'Old Faithful','Lion','Plume','Little Cub'  )
print('The names of the aborbing states are ')
absorbstate
```

## Step 2: Identify transition states, non-recurrent states and absorbing states

```{R message=FALSE, warnings=FALSE}
#find transition probs between absord states
irreduciblematrix <- states%>%
  filter(before %in% absorbstate)%>%filter(after %in% absorbstate)%>%
  group_by(before)%>%mutate(insidep=times/sum(times))%>%
  select(before,after, insidep)%>%arrange(before,after)
print(head(irreduciblematrix))
Imatrix <- matrix(irreduciblematrix$insidep, nrow = 5,ncol = 5, byrow = TRUE)
#acquire the transitioning matrix R
getRmatrix <- function(df,absorbstates = absorbstate){
  attach(df)
  beforestates <- unique(df$before)
  k <- length(beforestates)
  m <- length(absorbstates)
  Rmat <- matrix(0,nrow = k,ncol = m)
  j=1
  #find the transition prob for each uniqute state
  while ( j <= k){
    state <- beforestates[j]
    onegeyser <- df%>%filter(before==state)
    if (nrow(onegeyser)==m){
      Rmat[j,] <- onegeyser$rp
    }else{
      Rmat[j,which(absorbstate %in% onegeyser$after)] <- onegeyser$rp
    }
    j <- j+1
  }
  return(Rmat)
}

transitionR <- states%>%filter(! before %in% absorbstate)%>%
  filter(after %in% absorbstate)%>%
  filter(times>500)%>%
  group_by(before)%>%
  mutate(rp = times/sum(times))%>%arrange(before,after)%>%
  select(before,after,rp)
Nonrecurrent <- unique(transitionR$before)
print('The names of the non-recurrent states are ')
Nonrecurrent
```
## Step 3: create matrices 
The formula for identifying the transition probability consists of R and Q matrices.

```{R message=FALSE, warning=FALSE}
#as-a-whole R transition matrix 32*1
allstates <- c(as.factor(absorbstate),as.factor(Nonrecurrent))
wholeR <- states%>%filter(before %in% Nonrecurrent)%>%
  filter(after %in% Nonrecurrent |after %in% absorbstate)%>%
  group_by(before)%>%mutate(wholrrp = times/sum(times))%>%
  filter(after %in% absorbstate)%>%
  arrange(before,after)%>%group_by(before)%>%
  mutate(absorbrp = sum(wholrrp))%>%
  arrange(before,after)
absorbr <- unique(wholeR$absorbrp)
print('The R matrix is ')
absorbr
# Q matrix
transitionQ <- states%>%filter(before %in% Nonrecurrent & 
                                 after %in% Nonrecurrent)%>%
  mutate(Qp=times/sum(times))%>%
  arrange(before,after)%>%
  select(before,after, Qp)
statesQ <- sort(unique(transitionQ$before))
k <-length(unique(transitionQ$before))
k*k
getQmatrix <- function(qstates=transitionQ$before,df=transitionQ){
  attach(df)
  num_states <- length(unique(qstates))
  Qmatrix <- matrix(0,nrow = num_states,ncol = num_states)
  statesall <- unique(qstates)
  j <-1
  while( j <= num_states){
    i <- statesall[j]
    onegeyser <- df%>%filter(before==i)
    if (nrow(onegeyser)==num_states){
      x <- onegeyser$Qp
      Qmatrix[j,] <- x
    }else{
      dest <- onegeyser$after
      Qmatrix[j,which(statesall %in% dest)]<- transitionQ$Qp[which(statesall %in% dest)]
      }
      j <- j+1
  }
  return(Qmatrix)
}
Qmatrix <- getQmatrix()
print('The first five lines of the Q matrix')
Qmatrix[1:5,1:10]
```

## Step 4: Build models with the matrices
```{R message=FALSE,warning=FALSE}
zeromatrix <- matrix(0, nrow = 1,ncol = 32)
imatrix <- matrix(1,nrow = 1,ncol = 1)
bigmatrixup <- cbind(imatrix,zeromatrix)
absorbr <-matrix(absorbr,nrow = 32,ncol = 1,byrow = TRUE )
bigmatrixdown <- cbind(absorbr,Qmatrix)
bigmatrix <- rbind(bigmatrixup,bigmatrixdown)
digmatrix <- diag(1,nrow = 32,ncol = 32)
t <- solve(digmatrix-Qmatrix)
print('The (I-Q)^(-1) matrix')

k<- solve(digmatrix-Qmatrix)%*%absorbr
print('The (I-Q)^(-1)*R matrix')
k
#average transition times before being absorbed into great greysers
back <- data.frame(start=unique(transitionQ$before))
tranday <- c()
for(i in 1:nrow(t)){
  cat(sum(t[i,]), '  ')
  tranday <-append(tranday,sum(t[i,]))
}
tranday <- matrix(tranday,nrow=1,ncol = 32)
print('The average transition steps')
tranday
#pi
ppi <-eigen(t(Imatrix))
eigenv <- ppi$vectors
egenvone <- eigenv[,1]/sum(eigenv[,1])
egenvone
#deal with intervals
#what is the average interval 
intervals <- diff.POSIXt(geysertrans$eruption_time_epoch)/3600
stateint <- data.frame(start=sequal$before,interval=intervals)
gap <- intervals[(intervals>25)]
gap<-gap/24
yeargap <- gap[which(gap>365)]/365
yeargap
stateint$interval<-as.numeric(stateint$interval)
summary(stateint$interval)
stateint <- stateint%>%filter(interval<2)
ggplot(stateint,aes(x=interval))+
  ggtitle('The histogram of intervals')+xlab('Intervals')+
  geom_density(color='blue')+geom_histogram(binwidth = 0.01,fill='light blue',
                                            col='light blue')
ggplot(stateint,aes(x=interval))+
  ggtitle('The density distribution of intervals')+xlab('Intervals')+
  geom_density(color='blue')
#test if the interval follows a poisson (exp) distribution
ks.test(stateint$interval,'pexp',10)
chisq.test(stateint$interval,simulate.p.value = TRUE,B=20)
s <- rexp(1058665,8)
sdf <- data.frame(exp=s)
ggplot(stateint,aes(x=interval))+
  ggtitle('The histogram of intervals')+xlab('Intervals')+
  geom_density(color='blue')+geom_histogram(binwidth = 0.01,fill='light blue',
                                            col='light blue')
ggplot(sdf,aes(x=exp))+geom_histogram(binwidth = 0.01,col='dark blue')+xlab('exp~lambda=10')+
  ggtitle('Histogram of exp(10)')+xlim(c(0,2))
summary(stateint$interval)
ss <- rexp(1058665,8)
ssdf <- data.frame(exp=ss)
ggplot(ssdf,aes(x=exp))+geom_histogram(binwidth = 0.01,col='dark blue')+xlab('exp~lambda=5')+
  ggtitle('Histogram of exp(5)')+xlim(c(0,2))

```
