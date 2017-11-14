import numpy as np 

def sanitize_mask(x):
    return x==x

class NH1(object):
    def __init__(self, bins=[0,1]):
        assert(len(bins) > 1)
        self.bins = np.array(bins )
        self._content = np.array([0 for x in range(len(bins)+1)], dtype=np.float64)
    def find_bin(self, x):
        for ix in xrange(len(self.bins)):
            if x < self.bins[ix]:
                return ix 
        return len(self.bins)
    def get_content(self, ix):
        return self._content[ix]
    def set_content(self, ix, val):
        self._content[ix] = val
    def fill(self, x, y=1):
        self._content[self.find_bin(x)] += y
    def fill_array(self, x, weights=None):
        mask = sanitize_mask(x)
        mask &= sanitize_mask(weights)
        x_masked = x[mask]
        weights_masked = None if (weights is None) else weights[mask]
        hist = np.histogram(x_masked, bins=self.bins, weights=weights_masked, density=False)[0]
        self._content += np.concatenate([[0],hist,[0]])
    def add_array(self, arr):
        self._content += arr.astype(np.float64)
    def save(self, fpath):
        save_arr = np.array([
                np.concatenate([[0],self.bins,[0]]), 
                self._content
            ])
        np.save(fpath, save_arr)
    def load(self, fpath):
        load_arr = np.load(fpath)
        self.bins = load_arr[0][1:-1]
        self._content = load_arr[1]
    def add_from_file(self, fpath):
        load_arr = np.load(fpath)
        try:
            assert(np.array_equal(load_arr[0][1:-1], self.bins))
        except AssertionError as e:
            print fpath 
            print load_arr[0]
            print self.bins 
            raise e
        add_content = load_arr[1].astype(np.float64)
        self._content += add_content
    def integral(self):
        return np.sum(self._content)
    def scale(self, scale=None):
        norm = np.float64(scale if scale else 1./self.integral())
        self._content *= norm 
    def invert(self):
        for ix in range(self._content.shape[0]):
            val = self._content[ix]
            if val:
                self._content[ix] = 1000./val
    def eval_array(self, arr):
        def f(x):
            return self.get_content(self.find_bin(x))
        f = np.vectorize(f)
        return f(arr)
    def plot(self, opts):
        plt.hist(self.bins[:-1], bins=self.bins, weights=self._content[1:-1],
                 histtype='step',
                 color=opts['color'],
                 label=opts['label'],
                 linewidth=2)
    def mean(self):
        sumw = 0 
        bin_centers = 0.5 * (self.bins[:-1] + self.bins[1:])
        for ix in xrange(bin_centers.shape[0]):
            sumw += bin_centers[ix] * self._content[ix+1]
        return sumw / self.integral()
    def quantile(self, threshold):
        acc = 0 
        threshold *= np.sum(self._content[1:-1])
        for ix in xrange(1, self._content.shape[0]-1):
            acc += self._content[ix]
            if acc >= threshold:
                return 0.5 * (self.bins[ix-1] + self.bins[ix])
    def median(self):
        return self.quantile(threshold = 0.5)
    def stdev(self, sheppard = False):
        # sheppard = True applies Sheppard's correction, assuming constant bin-width
        mean = self.mean()
        bin_centers = 0.5 * (self.bins[:-1] + self.bins[1:])
        integral = self.integral()
        variance = np.sum(bin_centers * bin_centers * self._content[1:-1])
        variance -= integral * mean * mean
        variance /= (integral - 1)
        if sheppard:
            variance -= pow(self.bins[1] - self.bins[0], 2) / 12 
        return np.sqrt(max(0, variance))

