"""
Usage:
~/spark/bin/spark-submit project_csds/blockparser/spark_mapaddr.py
"""

import time
from pyspark import SparkConf, SparkContext


def parse_outputs(line):
    """
    schema:
        txhash, nid, value, addr
    :param line:
    :return (key, value):
    """
    fields = line.split(',')
    return fields[0], (int(fields[2]), fields[3])


def parse_inputs(line):
    """
    schema:
        txhash, mid, value, addr
    :param line:
    :return (key, value):
    """
    fields = line.split(',')
    return fields[0], (int(fields[2]), fields[3])


def one_to_one_tx(two_lists):
    inputs = two_lists[0]
    outputs = two_lists[1]
    if len(inputs) == 0 or len(outputs) == 0:
        return []

    sum_in = 0
    # i = (val, addr)
    # o = (val, addr)
    for i in inputs:
        sum_in += i[0]

    result = []
    for i in inputs:
        for o in outputs:
            if o[0] != 0: # Insidely filter out all zero output
                result.append(((i[1], o[1]), i[0]*o[0]*1.0/sum_in))

    return result


def formatted_print(keyValue):
    with open('addrs.csv', 'a') as f:
        f.write('{},{},{:.2f},{}\n'.format(keyValue[1][0][0], keyValue[1][0][1], keyValue[1][1], keyValue[0]))


def main():
    # Initialize Timer
    start_time = time.time()

    # Initialize Spark Context: local multi-threads
    conf = SparkConf().setMaster("local[4]").setAppName("mapinput")
    sc = SparkContext(conf=conf)

    # Load files
    outputs = sc.textFile('outputs.csv').map(parse_outputs).partitionBy(2).persist()
    inputs = sc.textFile('inputs.csv').map(parse_inputs).partitionBy(2).persist()

    # Transformations and/or Actions
    final = inputs.cogroup(outputs). \
        filter(lambda keyValue: len(keyValue[1][0]) != 0 and len(keyValue[1][1]) != 0). \
        flatMapValues(one_to_one_tx)

    # Output file
    with open('addrs.csv', 'w') as f:
        pass
    final.foreach(formatted_print)

    # End Program
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()
