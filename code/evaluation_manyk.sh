for ((i=5;i<=100;i+=5)); do
    python evaluation.py --k $i &
done
wait