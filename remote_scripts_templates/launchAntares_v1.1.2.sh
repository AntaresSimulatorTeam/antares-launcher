#!/bin/bash
#SBATCH --ntasks=1                      # Number of MPI ranks
#SBATCH --nodes=1                       # Number of nodes
#SBATCH --output=antares-out-%j.txt      # Standard output log
#SBATCH --error=antares-err-%j.txt       # Standard error log

INPUT_ZIPNAME=$1
ANTARES_VERSION=$2
JOB_TYPE=$3
POST_PROCESSING=$4
OTHER_OPTIONS=$5

# Set Variables and load modules
# ==============================

if [ "$ANTARES_VERSION" = "610" ]; then
    export ANTARES_SOLVER_BIN="/path/to/antares/solver/610/antares-6.1-solver"
elif [ "$ANTARES_VERSION" = "700" ]; then
    export ANTARES_SOLVER_BIN="/path/to/antares/solver/700/antares-7.0-solver"
fi

module load xpress/xpress8.8.0
module load ampl/ampl
module load R/R-3.6.2
# Load module xpansion and R_libraries TODO
export XPANSION_RSCRIPT="/path/to/antares/xpansion/XpansionArgsRun.R"
export R_LIBS_SITE=/path/to/antares/R-libs/%v

# Set OMP_NUM_THREAD variable for R parallelization
if [ -n "$SLURM_CPUS_PER_TASK" ]; then
  export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
else
  exit 1
fi

# Set local variables
USER_HOME=$PWD
JOB_SCRATCH_DIR=/scratch/antares_${SLURM_JOB_ID}
STUDY_NAME=$SLURM_JOB_NAME
STUDY_PATH=$JOB_SCRATCH_DIR/$STUDY_NAME
SLURM_LOG_FILE=$USER_HOME/${STUDY_NAME}_job_data_${SLURM_JOB_ID}.txt
DATE_FORMAT="%Y-%m-%d-%H:%M"
START_TIME=$(date +$DATE_FORMAT)
POST_PROCESSING_SCRIPT_NAME="post-processing.R"

if [ "$JOB_TYPE" = "ANTARES_XPANSION" ]; then
  STAT_FILE=$USER_HOME/stats-xpansion-v1.1.txt
  FINAL_ZIP_FILE=finished_XPANSION_${STUDY_NAME}_${SLURM_JOB_ID}.zip
else
  STAT_FILE=$USER_HOME/stats-antares-v1.1.txt
  FINAL_ZIP_FILE=finished_${STUDY_NAME}_${SLURM_JOB_ID}.zip
fi

function print_message {
 echo "$1" >> "$SLURM_LOG_FILE"
}

function print_timed_message {
  local MY_TIME
  MY_TIME=$(date +$DATE_FORMAT)
  print_message "$MY_TIME >>> $1"
}

print_timed_message "START"
print_message "JOB_TYPE = $JOB_TYPE"
print_message "INPUT_ZIPNAME as from stdin  = $1"
print_message "antares_version from stdin  = $ANTARES_VERSION"
print_message "name of the study: $STUDY_NAME"
print_message "zipfile: $INPUT_ZIPNAME"
print_message "home directory: $USER_HOME"
print_message "hostname: $SLURM_JOB_NODELIST"
print_message "local directory: $JOB_SCRATCH_DIR"
print_message " "

# create job-specific temporary scratch directory
mkdir "$JOB_SCRATCH_DIR"
# copy input_zipfile to JOB_SCRATCH_DIR
cp "$INPUT_ZIPNAME" "$JOB_SCRATCH_DIR"
# change pwd to JOB_SCRATCH_DIR
cd "$JOB_SCRATCH_DIR" || exit

# Unzip input zipfile
SECONDS=0
print_timed_message "start UNZIP"
srun unzip "$INPUT_ZIPNAME" > /dev/null 2>&1
rm "$INPUT_ZIPNAME"
print_timed_message "end UNZIP"
UNZIP_DURATION=$SECONDS
print_message "unzip duration = $UNZIP_DURATION"
print_message " "

# Launch ANTARES or ANTARES_XPANSION
SECONDS=0
print_timed_message "start $JOB_TYPE"
if [ "$JOB_TYPE" = "ANTARES_XPANSION" ]; then
  srun Rscript $XPANSION_RSCRIPT --study="$STUDY_PATH" --path_antares=$ANTARES_SOLVER --n-cpu=${SLURM_CPUS_PER_TASK}
else
  srun $ANTARES_SOLVER_BIN --force-parallel=${SLURM_CPUS_PER_TASK} -i "$STUDY_PATH"
fi
print_timed_message "end $JOB_TYPE"
ANTARES_DURATION=$SECONDS
print_message "$JOB_TYPE duration = $ANTARES_DURATION"
print_message " "

# Launch post processing
POST_PROC_DURATION=0
if [ "$POST_PROCESSING" = "True" ]; then
  SECONDS=0
  print_timed_message "start POST-PROCESSING"
  cd "$STUDY_PATH" || exit

  srun Rscript $POST_PROCESSING_SCRIPT_NAME
  print_timed_message "end POST-PROCESSING"
  POST_PROC_DURATION=$SECONDS
  print_message "post processing duration = $POST_PROC_DURATION"
  print_message " "
  cd "$JOB_SCRATCH_DIR" || exit
fi

# Zip finished study
SECONDS=0
print_timed_message "start ZIP"
# shellcheck disable=SC2086
srun zip -2 -r "${USER_HOME}"/"$FINAL_ZIP_FILE" "$STUDY_NAME" > /dev/null 2>&1
print_timed_message "finish ZIP"
ZIP_DURATION=$SECONDS
print_message "final zip duration = $ZIP_DURATION"
print_message " "

# Print SLURM environment to file
SLURM_ENV=$(env | grep SLURM)
print_message "$SLURM_ENV"
print_message " "

# remove scratch folder
srun rm -rf ${JOB_SCRATCH_DIR}

# Output job stat to file
if [[ ! -f "$STAT_FILE" ]]; then
    echo "START-TIME SLURM_JOB_NAME SLURM_JOB_ID SLURM_CPUS_PER_TASK  UNZIP_DURATION ANTARES_DURATION POST_PROC_DURATION ZIP_DURATION" > ${STAT_FILE}
fi
echo $START_TIME $SLURM_JOB_NAME $SLURM_JOB_ID $SLURM_CPUS_PER_TASK $UNZIP_DURATION $ANTARES_DURATION $POST_PROC_DURATION $ZIP_DURATION >> ${STAT_FILE}

# Goodbye
print_timed_message "THE END"
