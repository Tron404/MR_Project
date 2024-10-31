#!/usr/bin/env bash
PATH_SHAPES=../ShapeDatabase_INFOMR
shape_folders=$(ls $PATH_SHAPES)
limit=0
for folder in ${shape_folders[@]}; do
    path_file=$PATH_SHAPES"/"$folder
    if [ -d $path_file ] && [ $folder != ".git" ]; then
        python shape_computation_distributed.py --shape_class $folder &
        limit=$((limit+1))
    fi
    if [ $limit -eq 10 ]; then
        limit=0
        wait    
    fi
done
