#!/usr/bin/env bash
PATH_SHAPES=../ShapeDatabase_INFOMR_norm
shape_folders=($(ls $PATH_SHAPES))
limit=0
for folder in ${shape_folders[@]}; do
    path_file=$PATH_SHAPES"/"$folder
    if [ -d $path_file ] && [ $folder != ".git" ]; then
        python feature_shape_computation_distributed.py --shape_class $folder &
        limit=$((limit+1))
    fi
    shape_list_len=${#shape_folders[@]}
    if [ $(($limit % 5)) -eq 0 ] || [ $limit -ge $shape_list_len ]; then
        wait    
    fi
done
