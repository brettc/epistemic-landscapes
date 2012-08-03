'''
Created on Oct 4, 2010

boolean dimensions. This model also does not reload
the landscape during each iteration and pre-computes communities. 

explore stats are not set up to run in arbitrary spaces.

@author: korydjohnson
'''

from decimal import Decimal
from itertools import product
from math import exp, sqrt
from numpy import ravel, reshape, arange, where
from numpy.ma import max as ma_max
from operator import mul
from random import choice,sample,random
from scipy import array, stats, zeros, sum as scipy_sum


if __name__ != '__main__':
    from Batch_Binary import prnt

class G:  # Global variables
    ###### Modify these to set parameters of experiment
    COLLECT_DATA = [False,10]  # This file will or will not print data, How frequently data is collected
    DIM_SIZE = [50,3]  # List with the sizes of each dimension
    END_TIME = 300  # Number of ticks in the simulation
    HILL_DIM = [2]  # Each entry will correspond to a hill over that many dimensions
    NUM_TURTLES = {"controls": 0, "pcontrols": 20, "followers": 0, "pfollowers": 0, "mavericks": 0}
    PFollower_PROG = 1
    RADIUS = 1
    
    ###### Do not modify these
    # Hill Variables
    size = 1 # 1 usually, but for hill climbing needs to be smaller (used to scale gaussian hills)
    
    # Patches Variables
    percent_sig = .34
    percent_starting = .78
    set_of_patches = []
    sig_patches = 0  # Number of significant patches
    sig_patches_loc = set()  # Locations of significant patches
    starting_patches = set()
    wasted_effort = 0  # Count of times a patch is visited more than once 
                       # Ignore the peak's moore neighborhood (once all peaks have been explored)
    
    # Turtles Variables
    agents_hill = 0  # Count of agents that have found the hill.
    agents_peak = 0  # Count of agents that have found the peak.
    sig_per_turtle_n = []  # Significance per turtle based on the number of significant patches visited.
    sig_per_turtle_p = []  # Significance per turtle based on the percentage of total significance.
    times_p = []  # List of turtles. Will be switched to times of reaching the peak.
    times_h = []  # List of turtles. Will be switched to times of reaching the hill.
    
    # Hill Variables
    peaks = []
    
    # General Variables
    ave_peak_dist = []
    count_patches = [0,0]  # Number of patches visited, number of significant patches visited, resp.
    epprog = Decimal(0)  # Epistemic progress
    percent_progress = Decimal(0)  # Total discovered significance / total significance on hill
    total_prog = Decimal(0)
    total_significance = 0  # Total significance on hill
    
    # Model Components
    arr_size = reduce(mul,DIM_SIZE)
    hills = []  # List of all instances of the "Hills" class
    patches_arr = reshape(arange(arr_size),DIM_SIZE)  # Integers in each cell
    patches_nhbd = []  # Neighborhood of each patch
    patches_nhbd_sig = []  # Significant of the patches in the neighborhood
    patches_loc = [0]*arr_size  # Integer index corresponds to location in array
    patches_sig = array(zeros(DIM_SIZE),'f')  # Array of significances of patches
    patches_vis = array(zeros(DIM_SIZE),int)  # Array of visited variable of patches
    peak_explored = False  # Records whether or not the peaks/plateaus have been completely explored
    set_of_patches = []  #  All patches in array
    turtles = []  # List of all instances of the different turtles classes
    
    # Printing variables
    run = 0  # Run number of batch
    filename = '\home\korydjohnson\workspace\Epistemic_Landscapes\Model_Output\Model_Test.csv'
    type = ''

class Hills():
    next_id = 1
    def __init__(self, num_dim):  # num_dim = Number of dimension(s) hill will cover
        self._id = Hills.next_id
        self._num_dim = num_dim
        # For Gaussian hills, activate the first of the following lines. Deactivate the others except the final one.
        self.make_hill_gauss(num_dim)
#        self.make_hill(num_dim)
#        self.set_distance()  # Sets the distance between the peak and the base of the hill.
#        self.classify_patches()  # Creates set of starting patches and significant patches based on this hill location.
#        if self._id == 1:
#            G.starting_patches = self._starting_patches
#        elif self._id > 1:
#            G.starting_patches = G.starting_patches & self._starting_patches        
        Hills.next_id += 1
    def make_hill(self, num_dim):
        #size = G.size  # Set the total size of hills. Larger number creates smaller hills. Range from .5 to 50.5.
        self._location = len(G.DIM_SIZE)*[None]
        for i in range(num_dim):
            self._location[i] = choice(range(G.DIM_SIZE[i]))
        self._location = tuple(self._location)
    def distance(self,patch):
        hill = self._location
        sum = 0
        dim_size = G.DIM_SIZE
        for i in range(len(hill)):
            try:
                sum += min(((hill[i]-patch[i])%dim_size[i])**2,((patch[i]-hill[i])%dim_size[i])**2)
            except TypeError:
                pass
        return sqrt(sum)
    def set_sig(self, patch_location):
        if patch_location in self._sig_patches:
            return stats.norm.pdf(self._distances[patch_location],scale=self._hillradius/2)
            # Returns the normal pdf with standard deviation of 1/2 of the hill's radius.
        else:
            return 0
    def set_distance(self):  # This function creates the variable _distances of the distances from the hill to all patches
        set_of_patches = G.set_of_patches
        self._distances = array(zeros(G.DIM_SIZE),'f')
        for patch in set_of_patches:
            self._distances[patch] = self.distance(patch)
    def find_optimal_dist(self,lbound,ubound,ratio):  # Finds the appropriate distance to call the base of the hill
        # The variables are the lower and upper bound on the distances it can choose and the ratio it is seeking to match
        bounds = [lbound, ubound]
        temp_dist = sum(bounds)/len(bounds)
        temp_sig = float(len(where(self._distances < temp_dist)[0]))/G.arr_size
        while abs(temp_sig-ratio) > .001:
            if temp_sig > ratio:
                bounds = [bounds[0],temp_dist]
            elif temp_sig < ratio:
                bounds = [temp_dist,bounds[1]]
            temp_dist = sum(bounds)/len(bounds)
            temp_sig = float(len(where(self._distances < temp_dist)[0]))/G.arr_size
        return temp_dist
    def classify_patches(self):
        self._hillradius = self.find_optimal_dist(0,ma_max(self._distances),G.percent_sig/len(G.HILL_DIM))
        sig_numbers = list(G.patches_arr[self._distances < self._hillradius])
        self._sig_patches = set([G.patches_loc[x] for x in sig_numbers])
        # Gives set of indices with the corresponding patch locations in G.patches_loc
        starting_dist = self.find_optimal_dist(0,self._hillradius,(1-G.percent_starting)/len(G.HILL_DIM))
        starting_numbers = set(G.patches_arr[self._distances >= starting_dist])
        patches_loc = G.patches_loc
        self._starting_patches = set([patches_loc[x] for x in starting_numbers])
    '''
    The following two functions are used to create gaussian hills. Currently they only cover
    two dimensions. In order to use these functions, the function calls to "make_hill" and "set_sig"
    need to be changed below (ie hard-code the change in functions). The functions that need to be
    changed are Patches.assign_significance(), Hills.__init__(), and set_up_patches.
    '''
    def make_hill_gauss(self, num_dim):
        size = G.size  # Set the total size of hills. Larger number creates smaller hills. Range from .5 to 50.5.
        if self._id == 1:
            self._gaussian = (.75, .02*size, .01*size, .02*size)  # A, a, b, c
            loc = [75,75]
            while 1:
                if num_dim > len(loc):
                    loc.append([choice(range(G.DIM_SIZE[len(loc) + 1]))])
                else:
                    break
            self._location = tuple(loc)
        if self._id == 2:
            self._gaussian = (.7, .01*size, .01*size, .01*size)  # A, a, b, c
            loc = [45, 45]
            while 1:
                if num_dim > len(loc):
                    loc.append([choice(range(G.DIM_SIZE[len(loc) + 1]))])
                else:
                    break
            self._location = tuple(loc)
    def set_sig_gauss(self, patch_location):
        sig1 = self._gaussian[0] * exp(-1*(self._gaussian[1] * (patch_location[0] - \
                    self._location[0])**2 + self._gaussian[2] * (patch_location[0] - \
                    self._location[0]) * (patch_location[1] - self._location[1]) + \
                    self._gaussian[3] * (patch_location[1] - self._location[1])**2))  
        sig2 = self._gaussian[0] * exp(-1*(self._gaussian[1] * (self._location[0] - \
                    patch_location[0])**2 + self._gaussian[2] * (self._location[0] - \
                    patch_location[0]) * (self._location[1] - patch_location[1]) + \
                    self._gaussian[3] * (self._location[1] - patch_location[1])**2))  
        return max(sig1, sig2)
    
        
            
class Patches(): 
    def __init__(self,location):  # Location of the patch as an array
        self._location = location
        self._visited = [0,0,0,0]  # Total, Control, Follower, Maverick, resp.     
        self.assign_significance()
    def assign_significance(self):
        # For Gaussian hills, activate the first 6 of the following 7 lines. Deactivate the last.
        patches_loc = G.patches_loc
        patches_arr = G.patches_arr
        self._sig = int(1000*max([hill.set_sig_gauss(self._location) for hill in G.hills]))
        if self._sig > 0:
            G.sig_patches += 1
        if self._sig < 10:
            G.starting_patches |= set([patches_loc[patches_arr[self._location]]])
#        self._sig = max([hill.set_sig(self._location) for hill in G.hills])

class Turtle():
    next_id = 1
    def __init__(self,location):
        self._id = [Turtle.next_id,0,0,0,0,0]  # Turtle,control,pcontrol,follower,pfollower,maverick resp.
        Turtle.next_id += 1
        self._location = [location,0]
#        G.ave_peak_dist.append(distance(location,(45,45))) 
        self._sig = [G.patches_sig[self._location[0]], 0]  # Current significance, previous significance, resp.
        self.community()
        Turtle.heading(self)
        self._explored = set([location])  # These are the patches that the turtle explored first for epprog
        self._visited = set([location])  # These are the patches that the turtle has visited at any time
        self._totalsig = 0
    def heading(self):
        self._heading = choice(self._community[0])[0]
    def prev_direction(self):
        old_heading = len(G.DIM_SIZE) * [0]
        for i in range(len(G.DIM_SIZE)):
            old_heading[i] = (2*self._location[0][i] - self._location[1][i]) % G.DIM_SIZE[i]
        return tuple(old_heading)
    def prev_patch(self):
        old_patch = len(G.DIM_SIZE) * [0]
        for i in range(len(G.DIM_SIZE)):
            old_patch[i] = (2*self._location[1][i] - self._heading[i]) % G.DIM_SIZE[i]
        return tuple(old_patch)
    def move(self):
        self._location = [self._heading, self._location[0]]
        self._sig = [G.patches_sig[self._location[0]], self._sig[0]]
        self.community()
        self._heading = self.prev_direction()
        self._visited.add(self._location[0])
        if G.patches_vis[self._location[0]] == 0:
            self._explored.add(self._location[0])
    def back(self):
        self._location = [self.prev_patch(), self._location[0]]  # Must call prev_patch b/c of changes made in update_data
        self._sig[0] = self._sig[1]
        self.community()
        Turtle.heading(self) 

class Control(Turtle):
    next_id = 1
    def __init__(self,location):
        Turtle.__init__(self,location)
        self._id[1] = Control.next_id
        Control.next_id += 1
    def community(self):  # Actually sets the Moore neighborhood as Turtle variable
        nh_loc = G.patches_nhbd[G.patches_arr[self._location[0]]]
        self._community = [zip(nh_loc,[0]*len(nh_loc)),0]
    def move(self):
        if self._sig[0] > self._sig[1]:  # If current sig > previous sig
            Turtle.move(self)  # Move same, previously specified direction
        elif self._sig[0] == self._sig[1]:  # Else if current sig == previous sig
            if random() < .02:  # 2% of the time
                self.heading()  # Pick a random, new direction
                Turtle.move(self)  # Move in this direction
        else:  # If current sig < previous sig
            Turtle.back(self)  # Move to previous patch
        # Note: this procedure typically stays still if current sig == previous sig
        
class PControl(Control):
    next_id = 1
    def __init__(self,location):
        Turtle.__init__(self,location)
        self._id[2] = PControl.next_id
        PControl.next_id += 1
    def move(self):
        if self._sig[0] > self._sig[1]:  # If current sig > previous sig
            Turtle.move(self)  # Move in same, previously specified direction
        elif self._sig[0] == self._sig[1]:  # Else if current sig == previous sig
            if random() < .02:  # 2% of the time
                self.heading()  # Pick a random, new direction
            Turtle.move(self)  # Move in previously specified direction or new direction
        else:  # If current sig < previous sig
            Turtle.back(self)  # Move to previous patch
        # Note: this procedure always moves if current sig == previous sig

class Follower(Control):
    next_id = 1
    def __init__(self,location):
        Turtle.__init__(self,location)
        self._id[3] = Follower.next_id
        Follower.next_id += 1
    def community(self):
        nh_loc = G.patches_nhbd[G.patches_arr[self._location[0]]]
        nh_sig = G.patches_nhbd_sig[G.patches_arr[self._location[0]]]
        
        patches_vis = G.patches_vis
        nh_vis = [patches_vis[x] for x in nh_loc]
        
        nh_loc = zip(nh_loc,nh_sig)
        vis = [nh_loc[x] for x in range(len(nh_loc)) if nh_vis[x] != 0]
        unvis = [nh_loc[x] for x in range(len(nh_loc)) if nh_vis[x] == 0]
    
        self._community = [nh_loc,unvis,vis] # List of tuples of neighborhood: all patches, unvisited patches, visited patches. Each paired with significance.
    def new_patch(self):  # Returns the location of the max visited patch in the neighborhood
        max_sig = max([x[1] for x in self._community[2]])
        max_patches = [x[0] for x in self._community[2] if x[1] == max_sig]
        return choice(max_patches)
    def heading(self):
        self._heading = choice(self._community[1])[0]  # Pick an unvisited patch
    def move(self):
        if len(self._community[2]) != 0:  # If there are visited patches
            new_patch = self.new_patch()  # Pick patch with highest sig in neighborhood
            if G.patches_sig[new_patch] >= self._sig[0]:  # If new patch sig >= current sig
                self._heading = new_patch  # Set heading toward new patch
            elif len(self._community[1]) != 0:  # If new patch sig < current sig & there are unvisited patches
                self.heading()  # Set heading toward a random unvisited patch
        else:  # If there are not any visited patches
            self.heading()  # Set heading toward a random unvisited patch
        if self._heading != self._location[0]:  # If you are heading toward a new patch
            Turtle.move(self)  # Move to heading

class PFollower(Follower):  # Like follower except that it cannot follow its own path.
                            # When stuck on flat ground, it moves with prob = G.PFollower_prob
    next_id = 1
    def __init__(self,location):
        Turtle.__init__(self,location)
        self._id[4] = PFollower.next_id
        PFollower.next_id += 1
    def move(self):
        prob = 1
        test_prob = 0 # can make them behave in this way x% of the time.
        patches_sig = G.patches_sig
        if len(self._community[2]) != 0:  # If there are visited patches
            new_patch = self.new_patch()  # Pick patch with highest sig in neighborhood
            if G.patches_sig[new_patch] > self._sig[0]:  # If new patch sig > current sig
                self._heading = new_patch  # Set heading toward new patch
            elif G.patches_sig[new_patch] == self._sig[0]:  # If new patch sig == current sig and
                if new_patch not in self._visited:  # This turtle has not visited new_patch
                    self._heading = new_patch  # Set heading toward new patch
                else:  # If this turtle has visited new_patch
                    unvisited = [x[0] for x in self._community[2] if x[0] not in self._visited]
                    #  See if there are any visited patches that this turtle hasn't visited.
                    if len(unvisited) != 0:  # There is such a visited patch
                        unvisited_m = max([patches_sig[x] for x in unvisited])
                        self._heading = choice([x for x in unvisited if patches_sig[x] == unvisited_m])
                        # Pick one such patch with max sig at random
                    else:  #  If there are not any such patches
                        if len(self._community[1]) != 0:
                            self.heading()  # Set heading toward a random unvisited patch
                            test_prob = random()  # Random float number in [0,1)
                            prob = G.PFollower_PROG
            elif len(self._community[1]) != 0:  # If new patch sig < current sig & there are unvisited patches
                self.heading()  # Set heading toward a random unvisited patch
        else:  # If there are not any visited patches
            self.heading()  # Set heading toward a random unvisited patch
        if self._heading != self._location[0]:
            if test_prob < prob:
                # If turtle is heading toward a new patch and   
                Turtle.move(self)  # Move to heading

class Maverick(Follower):
    next_id = 1
    def __init__(self,location):
        Turtle.__init__(self,location)
        self._id[5] = Maverick.next_id
        Maverick.next_id += 1
    def move(self):
        if self._sig[0] >= self._sig[1]:  # If current sig >= previous sig
            if len(self._community[1]) != 0:  # If there are any unvisited patches in neighborhood
                if G.patches_vis[self._heading] != 0:  # If patch in current direction has been visited
                    self.heading()  # Set heading to a random unvisited patch
                Turtle.move(self)  # Move to heading
            else:  # If there aren't any unvisited patches
                new_patch = self.new_patch()  # Pick neighbor with highest sig. If more than 1 with
                                              # this significance, pick one of them at random.
                if G.patches_sig[new_patch] >= self._sig[0]:  # If this is >= current sig
                    self._heading = new_patch  # Set heading toward new patch
                    Turtle.move(self)  # Move to heading
        else:  # If current sig < previous sig
            Turtle.back(self)
    
def set_up_patches():
    string = 'G.set_of_patches = list(product('  
    for x in G.DIM_SIZE:
        string = string + 'range(' + str(x) + '),'
    string = string[:-1] + '))'
    exec string
    set_of_patches = G.set_of_patches
    setup_loc_arr()
    G.hills = tuple([Hills(dim) for dim in G.HILL_DIM])
    G.peaks = set([x._location[:x._num_dim] for x in G.hills])
    # For Gaussian hills, deactive the For loop and until the next for loop (ie until "for patch...")
#    for hill in G.hills:
#        try:
#            starting_patches = hill._starting_patches & starting_patches
#            sig_patches = sig_patches | hill._sig_patches
#        except:
#            starting_patches = hill._starting_patches
#            sig_patches = hill._sig_patches
#    G.starting_patches = starting_patches
#    G.sig_patches_loc = sig_patches
#    G.sig_patches = len(sig_patches)
    for patch in set_of_patches:
        temp = Patches(patch)
        G.patches_sig[patch] = temp._sig
        G.patches_vis[patch] = 0
    G.total_significance = float(scipy_sum(G.patches_sig))
    
    #Finding neighborhood and neighborhood significance
    arr_size = G.arr_size
    patches_loc = G.patches_loc
    patches_sig = G.patches_sig
    patches_nhbd = [neighborhood(x) for x in patches_loc]
    G.patches_nhbd_sig = [[patches_sig[x] for x in patches_nhbd[i]] for i in range(arr_size)]
    G.patches_nhbd = patches_nhbd

def setup_loc_arr(): # Produces an array of integers with a corresponding list. Index of list corresponds to a location in array.
    array = G.patches_arr
    list = G.patches_loc
    for i in range(G.arr_size):
        item = where(array==i)
        index = []
        for j in range(len(G.DIM_SIZE)):
            index.append(int(item[j]))
        list[i] = tuple(index)
        
def neighborhood(location):  # Produces the list of locations of moore-neighborhood      
    def distance(patch,center):
        sum = 0
        dim_size = G.DIM_SIZE
        for i in range(len(center)):
            if patch[i] != center[i]:
                sum += min(((center[i]-patch[i])%dim_size[i] - .5)**2,((patch[i]-center[i])%dim_size[i] - .5)**2)
        return sqrt(sum)
    def edge():  # Function to identify neighborhood if current cell is on an edge.
        '''
        Finds neighborhood by picking elements from 1 row, column, etc, at a time.
        Picks all columns of data, then picks all rows of data from the columns.
        '''
        arr = G.patches_arr
        dim = list(G.DIM_SIZE)
        size = 2*radius + 1  # "Breadth" of neighborhood
        for j in range(len(location)):
            x = location[j]
            dim[j] = size
            temp_arr = zeros(dim,int)  # Array of zeros
            for i in range(size):
                obj1 = []  # These represent the row, column, etc, to be selected.
                obj2 = []
                for k in range(j):
                    obj1.append(slice(None))  # Skip dimensions that have already been selected from
                    obj2.append(slice(None))
                obj1.append(slice(i,i+1))  # This is the row, col, etc, of temp_arr to be replaced
                temp = (x+i-radius)%dim_size[j]  # This is the row, col, etc, of the arr to be selected
                obj2.append(slice(temp,temp+1))  # Select that row, col, etc
                temp_arr[obj1] = arr[obj2]  # Row, col, etc of temp_arr replaced with that of arr 
            arr = temp_arr  # Set arr to the reduced array in temp_arr
        return list(ravel(arr))
    def inside():  # Function to identify neighborhood if current cell is an interior cell.
        obj = []
        for x in location:
            obj.append(slice((x-radius),(x+radius+1)))
        return list(ravel(G.patches_arr[obj]))
    
    if type(G.RADIUS) != int:
        radius = int(G.RADIUS) + 1  # Needs to be an integer for selecting in array
    else:
        radius = G.RADIUS
    dim_size = G.DIM_SIZE        
    for i in range(len(location)):
        if (location[i] - radius < 0) or (location[i] + radius >= dim_size[i]):
            nh_arr = edge()
            break
        if i == len(location)-1:
            nh_arr = inside()
            
    patches_loc = G.patches_loc
    nh_arr = list(set(nh_arr))
    nh_arr.remove(G.patches_arr[location])  # remove current location
    radius = G.RADIUS  # Actual radius to measure distance from origin
    nh_arr = [x for x in nh_arr if distance(patches_loc[x],location) <= radius]  # Only consider those w/in radius
    nh_loc = [patches_loc[x] for x in nh_arr]
    return nh_loc

def set_up_turtles():
    starting_patches = G.starting_patches
    for type in G.NUM_TURTLES.keys():
        if type == "controls":
            for i in range(G.NUM_TURTLES["controls"]):
                location = sample(starting_patches,1)[0]
                G.turtles.extend([Control(location)])
        elif type == "pcontrols":
            for i in range(G.NUM_TURTLES["pcontrols"]):
                location = sample(starting_patches,1)[0]
                G.turtles.extend([PControl(location)])
        elif type == "followers":
            for i in range(G.NUM_TURTLES["followers"]):
                location = sample(starting_patches,1)[0]
                G.turtles.extend([Follower(location)])
        elif type == "pfollowers":
            for i in range(G.NUM_TURTLES["pfollowers"]):
                location = sample(starting_patches,1)[0]
                G.turtles.extend([PFollower(location)])
        elif type == "mavericks":
            for i in range(G.NUM_TURTLES["mavericks"]):
                location = sample(starting_patches,1)[0]
                G.turtles.extend([Maverick(location)])
    G.times_p = list(G.turtles)
    G.times_h = list(G.turtles)
    G.turtles = tuple(G.turtles)
    
def update_data():
    if G.peak_explored == False:
        turtle_list = G.turtles  # Consider all turtles for updating visited array
        # Determine if the peaks have been explored
        peaks = G.peaks
        patches_vis = G.patches_vis
        for peak in peaks:  # Checks if the peak has been explored
            try:
                nhbd_peak = G.patches_nhbd[G.patches_arr[peak]]  # This is a list of patches in nbhd of peak
                temp = [patches_vis[x] for x in nhbd_peak]
                temp.remove(0)  # Operation that will fail if there are no zeros (ie unexplored patches)
                G.peak_explored = False
                break
            except:
                G.peak_explored = True
    else:
        turtle_list = G.times_p  # Only consider turtles that are not at the peak for counting visited
        # This avoids over counting due to agents roaming on the peak
    turtles = [x for x in turtle_list if x.__class__ != int and x._location[0] != x._location[1]]
    new_patches = [x._location[0] for x in turtles]  
    update_array = zeros(G.DIM_SIZE,int)
    for patch in new_patches:
        update_array[patch] += 1
    for turtle in turtles:
        turtle._location[1] = turtle._location[0]
    G.patches_vis += update_array    
##    newly_visited = [x for x in new_patches if G.patches_vis[x] == 1]
#    newly_visited = [x._location[0] for x in turtles if x._location[0] == x._explored[len(x._explored)-1]]
##    G.count_patches[0] += len(set(newly_visited))
##    G.count_patches[1] += len(set([x for x in newly_visited if G.patches_sig[x] > 0]))
#    test0 = G.count_patches[0] + len(set(newly_visited))
#    test1 = G.count_patches[1] + len(set([x for x in newly_visited if G.patches_sig[x] > 0]))
    G.count_patches[0] = len(where(G.patches_vis>0)[0])
    G.count_patches[1] = len(where(G.patches_sig[where(G.patches_vis > 0)] > 0)[0])
#    if test0 != G.count_patches[0]:
#        pass
#    if test1 !=G.count_patches[1]:
#        pass
#    if G.count_patches[1] > G.sig_patches:
#        pass
    G.epprog = Decimal(G.count_patches[1])/G.sig_patches
#    if G.epprog > 1:
#        pass

def progress():
    patches_sig = G.patches_sig
    patches_vis = G.patches_vis
    sig_per_turtle_p = []
    sig_per_turtle_n = []
    total_explored = set()
    sum_n = 0
    for turtle in G.turtles:
#        explored = turtle._explored
        explored = turtle._explored - total_explored
        total_explored = total_explored | explored
#        This sig_per_turtle is calculated as a percentage of total significance on hill
        turtle_sig_p = sum([patches_sig[x] for x in explored])
        sig_per_turtle_p.append(turtle_sig_p/G.total_significance)
#        This sig_per_turtle is calculated as a percentage of significant patches
#        turtle_sig_n = len([x for x in explored if patches_sig[x] > 0])
        turtle_sig_n = len(explored & G.sig_patches_loc)
        sum_n += turtle_sig_n
        sig_per_turtle_n.append(float(turtle_sig_n)/G.sig_patches)
    G.sig_per_turtle_p = sig_per_turtle_p
    G.sig_per_turtle_n = sig_per_turtle_n
    G.percent_progress = sum(patches_sig[patches_vis != 0])/G.total_significance
    G.total_prog = G.count_patches[0]/Decimal(G.arr_size)
    G.wasted_effort = scipy_sum(patches_vis) - len(where(patches_vis > 0)[0])
    # Wasted effort excludes patches surrounding the peak after the peak has been explored
    # This is to avoid over counting

def climb_stats(time=0): 
    # Agents at Peak
    peaks = G.peaks
    turtles = G.times_p
    for i in range(len(turtles)):
        if (type(turtles[i]) != int):
            for peak in peaks:
                if turtles[i]._location[0][:len(peak)] in peaks:
                    turtles[i] = time
                    break
    times = [x for x in turtles if type(x) == int]
    G.agents_peak = len(times)
    
    # Agents on Hill
    turtles = G.times_h
    for i in range(len(turtles)):
        if (type(turtles[i]) != int) and (turtles[i]._sig[0] != 0):
            turtles[i] = time
    times = [x for x in turtles if type(x) == int]
    G.agents_hill = len(times)

def clean_var():
    #Patches Variables
    G.percent_progress = Decimal(0)  # Total discovered significance / total significance on hill
    G.wasted_effort = 0  # Count of times a patch is visited more than once (ignore peak's moore neighborhood)
    
    #Turtles Variables
    G.agents_hill = 0  # Count of agents that have found the hill
    G.agents_peak = 0  # Count of agents that have found the peak
    G.sig_per_turtle_n = []
    G.sig_per_turtle_p = []
    G.times_p = []  # List of turtles. Will be switched to times of reaching the peak.
    G.times_h = []  # List of turtles. Will be switched to times of reaching the hill.
    
    #General Variables
    G.ave_peak_dist = []
    G.count_patches = [0,0]  # Number of patches visited, number of significant patches visited, resp.
    G.epprog = Decimal(0)  # Epistemic progress
    G.percent_progress = Decimal(0)  # Total discovered significance / total significance on hill
    G.total_prog = Decimal(0)
    
    # Model Components
    G.patches_vis = array(zeros(G.DIM_SIZE),int)  # Array of visited variable of patches
    G.peak_explored = False
    G.turtles = []  # List of all instances of the different turtles classes

def simulate():
    clean_var()
    set_up_turtles()
    update_data()
    for i in range(1,G.END_TIME+1):
        if G.COLLECT_DATA[0] == True:
            if i%G.COLLECT_DATA[1] == 0:
#                if __name__ != '__main__':
                    progress()
                    prnt(G.filename,G.type,i-1,G.run)
        for turtle in G.turtles:
            turtle.move()
        update_data()
        climb_stats()
    progress()
    
def main():
    set_up_patches()
    sum = 0
    set_up_turtles()
#    climb_stats()
#    explore_stats()
    simulate()

if __name__ == '__main__': main()