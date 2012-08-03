'''
Created on Nov 17, 2010

Batch run made to test the binary model. This model is used to test the
realistic landscape provided by the theory of mind literature.

Must use "set_up_patches" whenever radius size changes.

The information on variance in significance contribution per turtle
is calculated from "frac{number of explored, significant patches}{number of significant patches}."
See EL_Radius for more info.

@author: korydjohnson
'''
#include: wasted effort, agents_peak, percent_progress

import EL_Binary as EL
from scipy import array, zeros, var, mean, median
from scipy.stats import skew
from numpy import reshape, arange
from operator import mul
from time import time as time
from os import getcwd

class G():
    # Edit this section to set parameters of batch run, similar to behavior space
    COLLECT_DATA = [False, 1]  # Model will print data during run, How frequently data is printed (in ticks)
    COMPLETE_DIM = [101,101]  # The complete dimensions and dimension sizes. A subset of this list will be used depending
                                # on the specification for the model. All subsets begin from the left. Also, the hills begin
                                # from the left as well. So a hill_dim of 2 means the hill is in the first two dimensions.
    NEMPTY_DIM = [0]  # Number of empty dimensions
    HILL_DIM = [[2,2]]  # Number of dimensions the hill(s) will cover. For multiple hills, the set of hills must be
                        # an element of the list ie [[2,2],[2,4]] has 2 different hill specifications with 2 hills each.
                        # (easiest to use the zip() function to test many sets of hills).
    NUM_RUNS = 25  # Number of repetitions per parameter specification
    TURTLE_MULTIPLE = .03
    TICKS = {"controls": range(10,301,10), "pcontrols": range(10,301,10), "followers": range(10,301,10), "pfollowers": range(10,301,10), "mavericks": range(10,301,10)}  # Length of each model run in terms of ticks
    TYPES = ["controls","pcontrols","followers","pfollowers","mavericks"]  # The types of turtles to use. Note: currently only handles homogeneous turtles
    
    PATH = getcwd() + '/Model_Output'
    Setup_File = '/Setup_Times.csv'  # This file will store the time it takes to precompute model parameters

    # To specify a different filename, change "file" in the function "main()"
    # "file" is placed within the function to that it can make uniquely named files during the batch run
    # Currently, a new file is made for each new dimension size in order to keep the csv file(s) a manageable size
    
    ### Don't edit these
    filename = ''
    type = ''
    i = 0
    Time = [0, 0]
    Setup_filename = PATH + Setup_File
    Setup_Time = [0, 0]

def prnt(filename, type, duration, run):
    sptp = EL.G.sig_per_turtle_p  # Sig per turtle based on percent of total significance
    sptn = EL.G.sig_per_turtle_n  # Sig per turtle based on number of significant patches visited
    open(filename, 'a').write(str(type) + ',' + str(EL.G.NUM_TURTLES[type]) + \
        ',' + str(duration) + ',' + str(run) + ',' + \
        str(EL.G.epprog) + ',' + str(EL.G.total_prog) + ',' + str(EL.G.percent_progress) + \
        ',' + str(EL.G.agents_peak) + ',' + str(EL.G.agents_hill) + ',' + str(EL.G.wasted_effort) + \
        ',,' + str(min(sptp)) + ',' + str(max(sptp)) + ',' + str(mean(sptp)) + ',' + str(median(sptp)) + \
        ',' + str(var(sptp)) + ',' + str(skew(sptp)) + ',,' + str(min(sptn)) + ',' + str(max(sptn)) + \
        ',' + str(mean(sptn)) + ',' + str(median(sptn)) + ',' + str(var(sptn)) + ',' + str(skew(sptn)) + '\n')

def model_components():
    DIM_SIZE = EL.G.DIM_SIZE
    EL.G.arr_size = reduce(mul, DIM_SIZE)
    EL.G.patches_arr = reshape(arange(EL.G.arr_size), DIM_SIZE)  # Integers in each cell
    EL.G.patches_loc = [0] * EL.G.arr_size  # Integer index corresponds to location in array
    EL.G.patches_sig = array(zeros(DIM_SIZE), 'f')  # Array of significances of patches
    EL.G.patches_vis = array(zeros(DIM_SIZE), int)  # Array of visited variable of patches

def main():
    open(G.Setup_filename, 'a').write('Hill_Dim,Dim_Size,Time\n')
    for hill_dim in G.HILL_DIM:
        for nempty_dim in G.NEMPTY_DIM:
            if hill_dim.__class__ == int:  # Model needs to receive this variable as a list.
                EL.G.HILL_DIM = [hill_dim]
                EL.G.DIM_SIZE = G.COMPLETE_DIM[:hill_dim + nempty_dim]
            else: 
                EL.G.HILL_DIM = list(hill_dim)
                EL.G.DIM_SIZE = G.COMPLETE_DIM[:max(hill_dim) + nempty_dim]
            G.Setup_Time[0] = time()
            model_components()
            EL.set_up_patches()
            G.Setup_Time[1] = time()
            hillstr = str(reduce(lambda x, y: str(x) + '-' + str(y), EL.G.HILL_DIM))  # Make the string of hill dimensions.
            open(G.Setup_filename, 'a').write(hillstr + ',' + str(len(EL.G.DIM_SIZE)) + ',' + \
                                    str((G.Setup_Time[1] - G.Setup_Time[0]) / 3600) + ',hours\n')
            for type in G.TYPES:
                G.Time[0] = time()
                EL.G.COLLECT_DATA = G.COLLECT_DATA
                EL.G.NUM_TURTLES = {"controls": 0, "followers": 0, "mavericks": 0, "pcontrols": 0}
                EL.G.type = type
                #############################
                file = '/ToM_' + str(EL.G.type) + '_HD' + hillstr + '_DS' + str(len(EL.G.DIM_SIZE)) + '.csv'
                #############################
                filename = G.PATH + file
                open(filename, 'a').write("Patches,Sig Patches,Starting Patches,,Dimensions,\n" + str(EL.G.arr_size) + \
                                          ',' + str(EL.G.sig_patches) + ',' + str(len(EL.G.starting_patches)) + \
                                          ',,' + str(EL.G.DIM_SIZE).replace(',',' ')[1:-1] + '\n\n')
                open(filename, 'a').write('Turtle Type,Number of Turtles,Ticks,Run,Epprog,Total Progress' + \
                                        ',Percent Progress,Agents at Peak,Agents on Hill,Wasted Effort' + \
                                        ',,Sig Min P,Sig Max P,Sig Mean P,Sig Median P,Sig Var P,Sig Skew P' + \
                                        ',,Sig Min N,Sig Max N,Sig Mean N,Sig Median N,Sig Var N,Sig Skew N\n')
                #order: min max, mean, mdedian, var, skew
                EL.G.filename = filename
                num = int(EL.G.arr_size * G.TURTLE_MULTIPLE)
                EL.G.NUM_TURTLES.update({type:num})
                for duration in G.TICKS[type]:
                    EL.G.END_TIME = duration
                    for i in range(G.NUM_RUNS):
                        EL.G.run = i + 1
                        EL.simulate()
                        if G.COLLECT_DATA[0] == False:
                            prnt(filename, type, duration, i + 1)
                G.Time[1] = time()
                open(filename, 'a').write('Run Time,' + str((G.Time[1] - G.Time[0]) / 3600) + ',Hours')
            reload(EL)
        
                             
if __name__ == '__main__': main()

'''
The printouts made from the above code put the run time at the bottom of the document.
The following code moves this information to the top of the document.
Need to uncheck the "if __name__ == '__main__'..." line below.
'''
def Modify_Files():
    path = "/home/korydjohnson/workspace/Epistemic_Landscapes/Model_Output/Theory_of_Mind"
    nempty_dim = G.NEMPTY_DIM
    hill_dim = G.HILL_DIM
    types = G.TYPES
    for h in hill_dim:
        for ne in nempty_dim:
            for type in types:
                if h.__class__ == int:  # Model needs to receive this variable as a list.
                    hill = [h]
                else: 
                    hill = list(h)
                hillstr = str(reduce(lambda x, y: str(x) + '-' + str(y), hill))
                file = '/ToM_' + str(type) + '_HD' + hillstr + '_DS' + str(max(hill) + ne) + '.csv'
                f = open(path + file)
                lines = f.readlines()
                time = lines.pop()
                lines.insert(2, time)
                lines.insert(3, "\n")
                f = open(path + file, 'w')  
                f.writelines(lines)
                f.close()
                
#if __name__ == '__main__': Modify_Files()

'''
To test the constant ratios between significant patches/total patches/and turtles.
Need to uncheck the "if __name__ == '__main__'..." line below.
'''

def Check_Ratios():
    path = "/home/korydjohnson/workspace/Epistemic_Landscapes/Model_Output/Theory_of_Mind"
    
    HD = G.HILL_DIM
    ED = G.NEMPTY_DIM
    types = G.TYPES
    
    for h in HD:
        for ne in ED:
            for type in types:
                if h.__class__ == int:  # Model needs to receive this variable as a list.
                    hill = [h]
                else: 
                    hill = list(h)
                hillstr = str(reduce(lambda x, y: str(x) + '-' + str(y), hill))
                file = '/ToM_' + str(type) + '_HD' + hillstr + '_DS' + str(max(hill) + ne) + '.csv'
                f = open(path + file)
                lines = f.readlines()
                line = [lines[1]]
                line.append(lines[5])
                temp = []
                for x in line:
                    temp.append(x.split(','))
                info = {'Patches': float(temp[0][0]), 'Sig Patches':float(temp[0][1]), 'Starting Patches':float(temp[0][2]), 'Turtles':float(temp[1][1])}
                print h, ne
                print info['Sig Patches'] / info['Patches']
                print info['Starting Patches'] / info['Patches']
                print info['Turtles'] / info['Patches']

#if __name__ == '__main__': Check_Ratios()


'''
This will combine files if runs of longer duration were tested. The folders for the
original (shorter) runs and second (longer) runs need to be specified. For (well, my)
convenience, and since the main run attributes are the same, the file names are the
same for the short and long durations. The shorter duration files are extended to include
the longer duration data. Need to uncheck the "if __name__ == '__main__'..." line below.
Note: "Modify_Files()" needs to be run before this.
'''

def Combine_Files1():  # Testing longer durations.
    Short_Folder = '/Theory_of_Mind/Test 2: Numerous Empty Dimensions'  # Name of folder containing shorter runs.
    Long_Folder = '/Theory_of_Mind'  # Name of folder containing longer runs.
    Output_Folder = '/Modified_Files'
    path = "/home/korydjohnson/workspace/Epistemic_Landscapes/Model_Output"
    HD = G.HILL_DIM
    ED = G.NEMPTY_DIM
    types = G.TYPES
    
    for h in HD:
        for ne in ED:
            for type in types:
                if h.__class__ == int:  # Model needs to receive this variable as a list.
                    hill = [h]
                else: 
                    hill = list(h)
                hillstr = str(reduce(lambda x, y: str(x) + '-' + str(y), hill))
                file = '/ToM_' + str(type) + '_HD' + hillstr + '_DS' + str(max(hill) + ne) + '.csv'
                with open(path + Short_Folder + file, 'r') as f:
                    short_lines = f.readlines()
                with open(path + Long_Folder + file, 'r') as f:
                    long_lines = f.readlines()
                short_lines.extend(long_lines[5:])
                long_time = long_lines[2].split(',')
                short_time = short_lines[2].split(',')
                short_time[1] = str(float(long_time[1]) + float(short_time[1]))
                short_lines[2] = ','.join(short_time)
                with open(path + Output_Folder + file, 'w') as f: 
                    f.write(''.join(short_lines))
            
#if __name__ == '__main__': Combine_Files1()

'''
This will combine files if a simulation run is repeated so the number of runs is increased.
The folders for the original runs and second runs need to be specified. For (well, my)
convenience, and since the main run attributes are the same, the file names are the
same for two files. Need to uncheck the "if __name__ == '__main__'..." line below.
Note: "Modify_Files()" needs to be run before this.
'''

def Combine_Files2():  # Gathering more runs/trials for each duration.
    First_Folder = ''  # Name of folder containing shorter runs.
    Second_Folder = '/Theory_of_Mind'  # Name of folder containing longer runs.
    Output_Folder = '/Theory_of_Mind/Temp Data'
    path = "/home/korydjohnson/workspace/Epistemic_Landscapes/Model_Output"
    HD = G.HILL_DIM
    ED = G.NEMPTY_DIM
    types = G.TYPES
    nruns1 = 25  # Number of runs for each simulation specification in the first batch.
    nruns2 = 25  # Number of runs for each simulation specification in the second batch.
    for h in HD:
        for ne in ED:
            for type in types:
                if h.__class__ == int:  # Model needs to receive this variable as a list.
                    hill = [h]
                else: 
                    hill = list(h)
                hillstr = str(reduce(lambda x, y: str(x) + '-' + str(y), hill))
                file = '/ToM_' + str(type) + '_HD' + hillstr + '_DS' + str(max(hill) + ne) + '.csv'
                with open(path + First_Folder + file, 'r') as f:
                    lines1 = f.readlines()
                with open(path + Second_Folder + file, 'r') as f:
                    lines2 = f.readlines()
                output_lines = lines1[0:5]
                ntests = len(lines1[5:]) / nruns1
                runs1 = range(5, len(lines1) + 1, nruns1)
                runs2 = range(5, len(lines2) + 1, nruns2)
                for i in range(ntests):
                    output_lines.extend(lines1[runs1[i]:runs1[i+1]])
                    temp_lines = lines2[runs2[i]:runs2[i+1]]
                    for i in range(nruns2):
                        line = temp_lines[i].split(',')
                        line[3] = str(nruns1+i+1)
                        output_lines.append(','.join(line))
                time1 = lines1[2].split(',')
                time2 = lines2[2].split(',')
                time1[1] = str(float(time1[1]) + float(time2[1]))
                output_lines[2] = ','.join(time1)
                with open(path + Output_Folder + file, 'w') as f: 
                    f.write(''.join(output_lines))
                    
#if __name__ == '__main__': Combine_Files2()
    
    
