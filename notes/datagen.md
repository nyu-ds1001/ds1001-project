# Feature Engineering

After collecting our data we saw that we had some variables with a lot of caterogi

## Moving Averages

A main concern we has with this data set was leakage as some of the game data we have is only collected during the game. Thus we would not be able to use this ex-post information into our model. However, these variables contain a lot of valuable information when trying to predict over-unders. To tackle this problem we generate moving averages of the ex-post game information.

