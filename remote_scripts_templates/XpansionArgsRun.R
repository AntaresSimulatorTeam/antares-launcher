'AntaresXpansion.

Usage:
  XpansionArgsRun.R --study=<study_path>  [--n-cpu=<n_cpu>] [--path_antares=<path_antares>]
  XpansionArgsRun.R (-h | --help)
  XpansionArgsRun.R --version

Options:
  -h --help     		Show this screen.
  --version     		Show version.
  --n-cpu=<n_cpu>  		Number of CPU for Antares --force-parallel [default: 2].
  --path_antares=<path_antares>	Path to the Antares solver binary [default: "antares-solver"].
  --study=<study_path>      	Path to the Antares study to be executed.


' -> doc
library(docopt)
arguments <- docopt(doc, version = 'AntaresXpansion 0.1')

library(antaresRead)
library(antaresXpansion)

setSimulationPath(arguments$study, simulation = 0)

path_solver <- arguments$path_antares

benders(path_solver, display = TRUE, report = TRUE, n_cpu_force_parallel=arguments$n_cpu)

