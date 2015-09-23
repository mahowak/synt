library(Hmisc)

d <- read.csv("syntcatmat.csv")

s <- read.csv("~/db/subtlex/sub", sep="\t")

d$Word = d$N
d <- merge(d, s, by = c("Word"))


d$ScaleFreq = scale(d$Lg10CD)[,1]
d$Cut = cut2(d$ScaleFreq, g=4)

d <- filter(d, abs(ScaleFreq + .74) > .05, abs(ScaleFreq + .25) > .05, abs(ScaleFreq - .694) > .05)

d <- group_by(d, Cut) %>% mutate(Category = sample(1:length(Cut))) %>% filter(Category <= 32)

#d$Category = factor(d$Cut, levels=c("lo", "lm", "hm", "hi")) #as.numeric(as.factor(d$Cut))
d$Category = ifelse(d$ScaleFreq < -.744, "lo", "hi")
d[d$ScaleFreq >= -.744 & d$ScaleFre < -.25, "Category"] = "lm"
d[d$ScaleFreq >= -.25 & d$ScaleFre < .694, "Category"] = "hm"

###
prep <- read.csv("prep.csv")
names(prep) = c("Word")
prep <- merge(s, prep, by = c("Word"))
prep$Cat = ifelse(prep$Lg10CD > median(prep$Lg10CD), "FW_hi", "FW_lo")
prep$word = prep$Word
prep$logfreq = prep$Lg10CD
prep$L = nchar(as.character(prep$word))
prep = sample_n(prep, nrow(prep))
prep = group_by(prep, Cat) %>% mutate(RunNum = rep(c(1,2,3,4), 8))
prep = prep[, c("word", "logfreq", "Cat", "L", "RunNum")]


#
d = group_by(d, Category) %>% mutate(Run = rep(sample(1:4), 8))
d <- gather(d, variable, value, -Lg10CD, -Category, -Run) %>% filter(variable %in% c("N", "A", "V", "AV")) 
d$Cat = paste(d$variable, d$Category, sep="_")
names(d) = c("logfreq", "Cat2", "RunNum", "pos", "word", "Cat")
d$L = nchar(as.character(d$word))
d  = d[, c("word", "logfreq", "Cat", "L", "RunNum")]

d = rbind(d, prep)
