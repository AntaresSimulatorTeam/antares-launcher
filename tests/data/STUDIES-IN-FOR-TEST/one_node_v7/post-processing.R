library(antaresRead)
##Loas sim

opts <- setSimulationPath('./', "input" )

## R script

if(!dir.exists("user")){
	dir.create("user")
}

for(i in seq_along(opts))
	try(cat(paste0(i,"."), opts[[i]], "\n", file = "user/outputR.txt", append = TRUE))

