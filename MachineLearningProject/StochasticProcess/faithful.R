library(data.table)
library(dplyr)
library(ggplot2)
geyser <- as.data.frame(fread('geysertimes_eruptions_complete_2019-05-31.tsv',quote = ''))
geyser$eruption_time_epoch <- as.POSIXct(geyser$eruption_time_epoch,
                                         origin='1970-01-01')
geysertrans <- geyser%>%select(eruption_time_epoch,geyser,duration)%>%
  arrange(eruption_time_epoch)
geyser1 <- geysertrans$geyser
geyser2 <- geyser1[-1]
geyser2 <- append(geyser2,'norecord')
sequal <- data.frame(before=geyser1,after=geyser2)
sequal<- sequal[1:nrow(sequal)-1,]
sequal[,'times'] <- 1
trans <- aggregate(times~before+after,data = sequal,FUN = sum)
states<- trans
statenames <- data.frame(geysername=sort(unique(states$before)),geyserid = c(1:length(unique(states$before))))
states <- merge(states,statenames,by.x='before',by.y='geysername')
states <- merge(states, statenames,by.x='after',by.y='geysername')
names(states)[4:5]<- c('BEFOREID','AFTERID')
#acquire the names of the irreducible states
absorbstate <- c('Daisy', 'Old Faithful',' Lion','Plume','Little Cub'  )
absorbstate
#acquire the transition matrix in the irreducible set

irreduciblematrix <- states%>%
  filter(before %in% absorbstate)%>%filter(after %in% absorbstate)%>%
  group_by(before)%>%mutate(insidep=times/sum(times))%>%
  select(before, BEFOREID,after,AFTERID, insidep)%>%arrange(before,after)
Imatrix <- matrix(irreduciblematrix$insidep, nrow = 5,ncol = 5, byrow = TRUE)
#acquire the transitioning matrix R
transitionR <- states%>%filter(! before %in% absorbstate)%>%
  filter(after %in% absorbstate)%>%
  filter(times>500)%>%
  group_by(before)%>%
  mutate(rp = times/sum(times))%>%arrange(before,after)%>%
  select(before, BEFOREID,after,AFTERID, rp)
Nonrecurrent <- unique(transitionR$before)
getRmatrix <- function(df,absorbstates = absorbstate){
  attach(df)
  beforestates <- unique(df$before)
  k <- length(beforestates)
  m <- length(absorbstates)
  Rmat <- matrix(0,nrow = k,ncol = m)
  j=1
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
# Qmatrix
transitionQ <- states%>%filter(before %in% Nonrecurrent & 
                                 after %in% Nonrecurrent)%>%
  mutate(Qp=times/sum(times))%>%
  arrange(before,after)%>%
  select(before, BEFOREID,after,AFTERID, Qp)
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
#null matrix
zeromatrix <- matrix(0, nrow = 1,ncol = 32)
imatrix <- matrix(1,nrow = 1,ncol = 1)
bigmatrixup <- cbind(imatrix,zeromatrix)
absorbr <-matrix(absorbr,nrow = 32,ncol = 1,byrow = TRUE )
bigmatrixdown <- cbind(absorbr,Qmatrix)
bigmatrix <- rbind(bigmatrixup,bigmatrixdown)
digmatrix <- diag(1,nrow = 32,ncol = 32)
t <- solve(digmatrix-Qmatrix)
t
k<- solve(digmatrix-Qmatrix)%*%absorbr
k

#average transition times before being absorbed into great greysers

back <- data.frame(start=unique(transitionQ$before))
tranday <- c()
for(i in 1:nrow(t)){
  cat(sum(t[i,]), '  ')
  tranday <-append(tranday,sum(t[i,]))
}
tranday <- matrix(tranday,nrow=1,ncol = 32)
#pi
ppi <-eigen(t(Imatrix))
eigenv <- ppi$vectors
egenvone <- eigenv[,1]/sum(eigenv[,1])
egenvone
#deal with intervals
intervals <- diff.POSIXt(geysertrans$eruption_time_epoch)/3600
stateint <- data.frame(start=sequal$before,interval=intervals)
gap <- intervals[(intervals>25)]
gap<-gap/24
yeargap <- gap[which(gap>365)]/365
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
ks.test(stateint$interval,'pexp',10)
chisq.test(stateint$interval,simulate.p.value = TRUE,B=20)
s <- rexp(1058665,8)
sdf <- data.frame(exp=s)
hist(s)
par(mfrow=c(2,1))
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
write.csv(transitionQ,file='Qoridata.csv')
write.csv(transitionR,file = 'Roridata.csv')
write.csv(irreduciblematrix,file='Ioridata.csv')
