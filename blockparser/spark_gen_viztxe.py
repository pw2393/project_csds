"""
Author: Peng Wu
License: MIT
"""

# Initialize Spark Context: local multi-threads
from pyspark import SparkConf, SparkContext

output_folder = './csv/'


def main():
    import sys
    if len(sys.argv) == 2:
        if sys.argv[1] == 'local[*]' or sys.argv[1] == 'yarn':
            argv_setMaster = sys.argv[1]
    else:
        print "\n\tUSAGE:\n\
                spark-submit spark_mapinput.py local[*]\
                spark-submit spark_mapinput.py yarn\
              "
        return


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
        return (fields[2], fields[3]), (fields[0], fields[1], fields[4])


    outputs = sc.textFile(output_folder+'outputs.csv').map(parse_outputs)
    inputs = sc.textFile(output_folder+'inputs_mapping.csv').map(parse_inputsmapping)

    # Transformations and/or Actions

    # op: transformation + action
    mine = sc.parallelize([(('0000000000000000000000000000000000000000000000000000000000000000', '4294967295'), ('0', 'x'))])
    final = inputs.join(outputs.union(mine))


    with open(output_folder+'viz_txedge.csv', 'w') as f:
        pass
    def formatted_print_2(keyValue):
        with open(output_folder+'viz_txedge.csv', 'a') as f:
            f.write('{},{},{},{}\n'.format(keyValue[0][0], keyValue[1][1][0], keyValue[1][0][0], keyValue[1][0][2]))
    final.foreach(formatted_print_2)
    #print final.first()

if __name__ == "__main__":

    import time
    # Initialize Timer
    start_time = time.time()

    main()

    print("--- %s seconds ---" % (time.time() - start_time))