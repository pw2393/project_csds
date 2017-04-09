"""
Author: Peng Wu
License: MIT
"""

# Initialize Spark Context: local multi-threads
from pyspark import SparkConf, SparkContext

output_folder = './csv/'


def main(argv_setMaster):

    conf = SparkConf().setMaster(argv_setMaster).setAppName("mapinput")
    sc = SparkContext(conf=conf)


    # Loading files
    def parse_outputs(line):
        """
        schema:
            txhash, nid, value, addr
        :param line:
        :return (key, value):
        """
        fields = line.split(',')
        return (fields[0], fields[1]), (fields[2], fields[3])


    def parse_inputsmapping(line):
        """
        schema:
            txhash, mid, prev_txhash, nid
        :param line:
        :return (key, value):
        """
        fields = line.split(',')
        return (fields[2], fields[3]), (fields[0], fields[1])


    outputs = sc.textFile(output_folder+'outputs.csv').map(parse_outputs).persist()
    inputs = sc.textFile(output_folder+'inputs_mapping.csv').map(parse_inputsmapping).persist()

    # Transformations and/or Actions

    # op: transformation + action
    metafinal = inputs.join(outputs)
    final = metafinal.values()

    # op: transformation
    # UTXOs = outputs.subtractByKey(inputs)
    # can be then reduced on address thus to obtain the total value for an UTXO address


    # final.map(lambda x:(x[0][0],x[0][1],x[1][0],x[1][1])).saveAsTextFile("input_final")
    with open(output_folder+'inputs.csv', 'w') as f:
        pass
    def formatted_print(keyValue):
        with open(output_folder+'inputs.csv', 'a') as f:
            f.write('{},{},{},{}\n'.format(keyValue[0][0], keyValue[0][1], keyValue[1][0], keyValue[1][1]))
    final.foreach(formatted_print)

    with open(output_folder+'viz_txedge.csv', 'w') as f:
        pass
    def formatted_print_2(keyValue):
        with open(output_folder+'viz_txedge.csv', 'a') as f:
            f.write('{},{},{}\n'.format(keyValue[0][0], keyValue[1][1][0], keyValue[1][0][0]))
    metafinal.foreach(formatted_print_2)


if __name__ == "__main__":

    import sys
    import time
    # Initialize Timer
    start_time = time.time()

    if len(sys.argv) == 2:
        if sys.argv[1] == 'local[*]' or sys.argv[1] == 'yarn':
            main(argv_setMaster = sys.argv[1])
    else:
        print "\n\tUSAGE:\n\
                spark-submit spark_mapinput.py local[*]\
                spark-submit spark_mapinput.py yarn\
              "

    print("--- %s seconds ---" % (time.time() - start_time))