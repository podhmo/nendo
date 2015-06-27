#!/bin/bash

OUT=$1
for i in examples/*.py
do
    echo $i >> ${OUT}
    echo "" >> ${OUT}
    echo ".. code-block:: python" >> ${OUT}
    echo "" >> ${OUT}
    N=`wc -l $i| sed 's/^ *//g' | cut -d ' ' -f 1`
    cat $i | tail -n `expr $N - 3` | sed 's/^/  /g;' >> ${OUT}
    echo "" >> ${OUT}
    echo "result:" >> ${OUT}
    echo "" >> ${OUT}
    echo ".. code-block:: sql" >> ${OUT}
    echo "" >> ${OUT}
    python $i | sed 's/^/  /g;' >> ${OUT}
    echo "" >> ${OUT}
done
