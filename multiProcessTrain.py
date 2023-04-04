# Comparing how different sized networks perform
# Anton Alley

import importlib
import trainSimpNoFitness as train

import multiprocessing as MP
import file as FH


#def train3V(): -> I think Only length as fitness has most potential

def train3():
    results = []
    sets = []
    queues = []
    defaultArgs =(10000,70,7) 


    for i in range(3):
        queues.append(MP.Queue())
        p = MP.Process(target=train.train, args=[*defaultArgs],
                       kwargs={'q':queues[-1], 'extraLosers':2, 'numCrossovers':5,
                               'networkShape':[train.INPUT_DATA_SIZE,
                                                18, 24, 36, 45, 36, 24, 18, 12, 9, 3]}
                       )
        sets.append(p)
        p.start()

    for p, q in zip(sets, queues):
        results.append(q.get())
        p.join()

    megaBatch = []
    for a in results:
        for i in a[0]:
            megaBatch.append(i)
    print(megaBatch)
    print("------------On to the final megaBatch------------")
    final = train.train(10000, 80, 8, numCrossovers=6, batch=megaBatch, extraLosers=1,
                        networkShape=[train.INPUT_DATA_SIZE, 18, 24, 36, 45, 36, 24, 18, 12, 9, 3])
    try:
        for ai in final[0]:
            ai.save()
        FH.save("Dec112018_10000x3_mega", [results, final])
    except:
        pass
    
    return results, final

##if __name__ == '__main__':
##    results, final = train3()
##    FH.save("10000x3", [results, final])




# Longer is better I think
def train3DIFF(): # 3 half the time of doing 4, different sized nets
    results = []
    sets = []
    queues = []
    defaultArgs =(5000,50,10) 

    queues.append(MP.Queue())
    p = MP.Process(target=train.train, args=[*defaultArgs],
                   kwargs={'q':queues[-1], 'extraLosers':2, 'numCrossovers':6,
                           'networkShape':[train.INPUT_DATA_SIZE,
                                           12, 16, 20, 16, 12, 8, 3]}
                   )
    sets.append(p)
    p.start()

    queues.append(MP.Queue())
    p = MP.Process(target=train.train, args=[*defaultArgs],
                   kwargs={'q':queues[-1], 'extraLosers':2, 'numCrossovers':6,
                           'networkShape':[train.INPUT_DATA_SIZE,
                                           14, 24, 18, 8, 3]}
                   )
    sets.append(p)
    p.start()

    queues.append(MP.Queue())
    p = MP.Process(target=train.train, args=[*defaultArgs],
                   kwargs={'q':queues[-1], 'extraLosers':2, 'numCrossovers':6,
                           'networkShape':[train.INPUT_DATA_SIZE,
                                           12, 18, 24, 24, 24, 18, 12, 9, 3]}
                   )
    sets.append(p)
    p.start()

    
    for p, q in zip(sets, queues):
        results.append(q.get())
        p.join()
        

    return results



