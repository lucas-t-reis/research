for i in {4..8} 
do
	for j in {4..8}
	do 
		python3 kmeans.py $i $j 
	done
done

mkdir graph 2>/dev/null || true
mkdir graph/dot 2>/dev/null || true
mkdir input 2>/dev/null || true
mv *.in input

for file in *.dot
do 
		dot $(basename $file) -Tsvg -o $(basename $file ".dot").svg
done

mv *.svg graph
mv *.dot graph/dot
