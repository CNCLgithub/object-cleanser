#!/bin/sh

rm -rf /tmp/* 2> /dev/null
module load openmind/singularity/3.5.0

# runBO="${1:-0}"
# testPhase"${2:-1}"

# singularity exec --nv -B /om:/om /om/user/arsalans/containers/pytorchBlenderLatest2.8.simg /usr/bin/python3.7 main.py --runBayesianOpt $runBO

singularity exec --nv -B /om:/om /om/user/arsalans/containers/pytorchBlender.simg python3.7 main.py