## Code from JDRobotter : https://github.com/JDRobotter ##
import math

class StdDevFilterException(Exception):
    pass

class StdDevFilter:
    def __init__(self, alpha, n):
        """
            This filter will reject value which are over alpha*stddev,
            standard deviation computed over n values

            https://en.wikipedia.org/wiki/Standard_deviation
        """
        self.alpha = alpha
        self.n = n
        self.vs = []

    def insert_value(self, x):
        self.vs.insert(0,x)
        # limit list size to self.n
        self.vs = self.vs[:self.n]

    def mean(self):
        """ Return mean value """
        return sum(self.vs)/len(self.vs)

    def mean_stddev(self):
        """ Return a (mean,standard deviation) tuple """
        if len(self.vs) == 0:
            raise StdDevFilterException

        mx = self.mean()
        # compute variance
        variance = sum([(x - mx)**2 for x in self.vs])/len(self.vs)
        # return mean value and standard deviation (square root of variance)
        return mx,math.sqrt(variance)

    def do(self, x, typ):
        """ Apply filter on value """
        try:
            mean,stddev = self.mean_stddev()
        except StdDevFilterException:
            self.insert_value(x)
            return x,True

        self.insert_value(x)

        # limit dispersion, refuse new value when too far away from mean
        e = abs(x-mean)
        if e <= self.alpha*stddev:
            return x,True
        else:
            return mean,False

