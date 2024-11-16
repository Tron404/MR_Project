for ((i=5;i<=100;i+=5)); do
    python evaluation.py --k $i --distance_approach "manual" &
    if (($i % 20 == 0)); then
        wait
    fi
done