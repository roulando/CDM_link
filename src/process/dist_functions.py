import gzip
import numpy as np
from abc import ABC, abstractmethod

class Dist_function(ABC):
    @abstractmethod
    def encode_single(self, x1):
        pass
    
    @abstractmethod
    def encode_concat(self, x1, x2):
        pass

    @abstractmethod
    def calc_function(self, c_x1, c_x2 , c_x1x2):
        pass

    def __call__(self, x1, x2, c_x1 = None, c_x2 = None):
        if x1 == x2:
            return 0.
        if not c_x1:
            c_x1 = self.encode_single(x1)
        if not c_x2:
            c_x2 = self.encode_single(x2)
        c_x1x2 = self.encode_concat(x1,x2)
        return self.calc_function(c_x1, c_x2, c_x1x2)

class CDM_gzip(Dist_function):
    def __init__(self,prefix = 'IHerzMichi'):
        self.prefix = prefix
    
    def encode_single(self, x1):
        return len(gzip.compress((self.prefix+x1).encode("utf-8")))
        
    def encode_concat(self, x1, x2):
        return max(len(gzip.compress(" " . join ([self.prefix,x1, x2 ]).encode("utf-8")))
                 , len(gzip.compress(" " . join ([self.prefix,x2, x1 ]).encode("utf-8"))))
                   
    def calc_function(self, c_x1, c_x2 , c_x1x2):
        return 2. - ((c_x1+c_x2)/ ( c_x1x2) )
    
class CBC_gzip(Dist_function):
    def __init__(self,prefix = 'IHerzMichi'):
        self.prefix = prefix
    
    def encode_single(self, x1):
        return len(gzip.compress((self.prefix+x1).encode("utf-8")))
    
    def encode_concat(self, x1, x2):
        return max(len(gzip.compress(" " . join ([self.prefix,x1, x2 ]).encode("utf-8")))
                 , len(gzip.compress(" " . join ([self.prefix,x2, x1 ]).encode("utf-8"))))

    def calc_function(self, c_x1, c_x2 , c_x1x2):
        return 1. - (c_x1+c_x2-c_x1x2)/(np.sqrt(c_x1*c_x2))

class NCD_gzip(Dist_function):
    def __init__(self,prefix = 'IHerzMichi'):
        self.prefix = prefix
    
    def encode_single(self, x1):
        return len(gzip.compress((x1).encode("utf-8")))
    
    def encode_concat(self, x1, x2):
        return max(len(gzip.compress(" " . join ([self.prefix,x1, x2 ]).encode("utf-8")))
                 , len(gzip.compress(" " . join ([self.prefix,x2, x1 ]).encode("utf-8"))))

    def calc_function(self, c_x1, c_x2 , c_x1x2):
        return (c_x1x2- min(c_x1,c_x2))/max(c_x1,c_x2)

class CDM_double_gzip(Dist_function):
    def __init__(self,prefix = 'IHerzMichi'):
        self.prefix = prefix
    
    def encode_single(self, x1):
        return len(gzip.compress((self.prefix+x1+x1).encode("utf-8")))
    
    def encode_concat(self, x1, x2):
        return max(len(gzip.compress(" " . join ([self.prefix,x1,x1, x2, x2 ]).encode("utf-8")))
                 , len(gzip.compress(" " . join ([self.prefix,x2,x2, x1,x1 ]).encode("utf-8"))))

    def calc_function(self, c_x1, c_x2 , c_x1x2):
        return -1. + 2.* (c_x1x2/(c_x1+c_x2))