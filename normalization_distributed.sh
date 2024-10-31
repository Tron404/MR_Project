#!/usr/bin/env bash
PATH_SHAPES=../ShapeDatabase_INFOMR_orig
shape_folders=$(ls $PATH_SHAPES)
limit=0
for folder in ${shape_folders[@]}; do
    path_file=$PATH_SHAPES"/"$folder
    if [ -d $path_file ] && [ $folder != ".git" ]; then
        python normalization_distributed.py --shape_class $folder &
        limit=$((limit+1))
    fi
    if [ $limit -eq 5 ]; then
        limit=0
        wait    
    fi
done
