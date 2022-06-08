# Ariel Simon 

# Environment:
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from easygui import multenterbox

# Grid cells values :
# Empty cell
EC = 0
# Healthy person (not vaccinated)
NH = 1
# Sick person (not vaccinated)
NS = 2
# A person who is vaccinated or recovering
NV = 3
vals = [EC, NH, NS, NV]
# board size
size = 30

# input user box(1):
text = "The board size is " + str(size*size) + " squares. define parameters for population initial status:"
title = ""
# parameters explanation and default values
initial_values_box = ["initial number of healthy people", "initial number of sick people", "initial number of vaccinated people"]
initial_values = [int(size*size * 0.25), int(size*size * 0.25), int(size*size * 0.25)]
input = multenterbox(text, title, initial_values_box, initial_values)
for i in range(3):
   input[i] = int(input[i])
NH_num, NS_num, NV_num = input
EMPTY_num = size*size - (NH_num+NS_num+NV_num)
if EMPTY_num <1:
    bad_size = NH_num+NS_num+NV_num
    print("You used",bad_size,"squares out of", size*size, ", and left no more place for empty cells. please try again")
    exit(0)

# input user box(2):
text2 = "Define parameters for infection probabilities:"
# parameters explanation and default values
initial_values_box2 = ["Probability (0<P<1) of healthy pearson become infected from sick neighbor",
                       " Probability (0<P<1) of vaccinated/recovering pearson become infected from sick neighbor",
                       "How many iterations sick person need to be recovering (minimum = 2)"]
initial_values2 = [0.5, 0.1, 2]
input2 = multenterbox(text2, title, initial_values_box2, initial_values2)
for i in range(3):
   input2[i] = float(input2[i])
PI, PV, limit_clock = input2
if PI >= 1 or PI <= 0 or PV >= 1 or PV <= 0 or limit_clock <2:
    print("Sorry. Probabilities have to be smaller than 1 and bigger than 0, recovering iteration have to be at least 2")
    exit(0)
   # Probabilities
   # PI = probability of healthy pearson to be infected from his sick neighbor
   # PV = probability of vaccinated or recovering pearson to be infected from his sick neighbor


# This function returns a random game grid board with:
# vals = optional cells value
# board size = size*size
# p = probability of reshape
def createGrid():
    board_size = size * size
    # returns a grid of NxN random values
    # box message and title
    grid = np.random.choice(vals, board_size, p=[EMPTY_num/board_size, NH_num/board_size, NS_num/board_size,NV_num/board_size]).reshape(size, size)
    print("This is the First Grid:")
    print(grid)
    print("continue")
    return grid

def get_value(i, j,new_i, new_j, grid, sick_neighbor, clock_grid_next):
    status = grid[i, j]
    # a healthy pearson with a sick neighbor can stay healthy or become sick in probability PI
    # remove option 3 (vaccinated or recovering) from vals:
    if status == NH and sick_neighbor == True:
        return np.random.choice(list(set(vals)-set([3, 0])), 1, p=[1 - PI, PI])
    # a healthy pearson with no sick neighbor will stay healthy
    elif status == NH and sick_neighbor == False:
        return 1
    # a vaccinated or recovering pearson with a sick neighbor can stay at his status or make sick in probability PV
    # remove option 1 (healthy) from vals
    if status == NV and sick_neighbor == True:
        maybeGetSick = np.random.choice(list(set(vals)-set([1, 0])), 1, p=[PV, 1 - PV])
        if maybeGetSick == NS:
            clock_grid_next[new_i,new_j] = 1
        return maybeGetSick
    # a vaccinated or recovering pearson with no sick neighbor will stay vaccinated or recovering
    elif status == NV and sick_neighbor == False:
        return 3
    # after limit_clock(parameter) generation a sick pearson becomes recover
    if status == NS and clock_grid_next[new_i, new_j] == limit_clock:
        # restart clock
        clock_grid_next[new_i, new_j] = 0
        return 3
    # sick pearson remain sick if not passed 3 generations
    elif status == NS and clock_grid_next[new_i, new_j] < limit_clock:
        return 2
    if status == EC:
        return 0

# this function check if one of the neighbors of cell[x, y] has the value that the function get(val_to_compare)
def check_neighbor(x, y, grid, val_to_compare):
    # go through all the neighbors ( x-1,x,x+1)(y-1,y,y+1)
    for i in range(x-1, x + 2):
        for j in range(y-1, y + 2):
            k = i
            t = j
            # change i,j to zero when the equal to the edges.
            # WRAP_AROUND model
            if i == size:
               k = 0
            if j == size:
                t = 0
            # if your neighbor is sick and the neighbor is noy yourself then return True
            if grid[k, t] == val_to_compare:
                return True
    return False


def legal_movement(i, j, move, movementGrid):
    new_x, new_y = new_place(i, j, move)
    if movementGrid[new_x, new_y] == 1:
        return False
    else:
        return True


def now_empty(i, j, move, grid):
    new_x, new_y = new_place(i, j, move)
    if grid[new_x, new_y] != 0:
        return False
    else:
        return True


def select_move(i, j, movementGrid, grid):
    # possibles moves :
    # 1 = Left Up (LU) ,2 = Up ,3 = Right Up (Ru), 4 = Left
    # 5 = Stay at your place ,6 = Right ,7 = Left Down (LD) ,8 = Down ,9 = Right Down (Rd)
    movement = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    illegalMovementList = []
    for move in movement:
        if not legal_movement(i, j, move, movementGrid):
            illegalMovementList.append(move)
        if move > 3 and i > 0:
            if not now_empty(i, j, move, grid):
                illegalMovementList.append(move)
    legalMovementList = list(set(movement) - set(illegalMovementList))
    # chose movement.
    # P(probability) not given so assumes a uniform distribution
    # one in order to select one value
    if legalMovementList == []:
        # if there is no legal movement stay at your place
        legalMovementList.append(5)
    return np.random.choice(legalMovementList, 1)


# return new i and new j as a result from the selected movement
def new_place(i, j, movement):
    # calculate new x new y as a result of the choice of action
    if movement == 1 or movement == 2 or movement == 3:
        new_x = i - 1
    if movement == 4 or movement == 5 or movement == 6:
        new_x = i
    if movement == 7 or movement == 8 or movement == 9:
        new_x = i + 1
        # if new x is out from edges,return to the other side (WRAP_AROUND)
        if new_x == size:
            new_x = 0
    if movement == 1 or movement == 4 or movement == 7:
        new_y = j - 1
    if movement == 2 or movement == 5 or movement == 8:
        new_y = j
    if movement == 3 or movement == 6 or movement == 9:
        new_y = j + 1
        #  if new y is out from edges,return to the other side (WRAP_AROUND)
        if new_y == size:
            new_y = 0
    return new_x, new_y


# for each pearson who sick, we save the time generation that the pearson is sick
def clock_sick_generation(i, j, new_i, new_j, grid, clock_grid_now, clock_grid_next):
    if grid[i, j] == NS:
        clock_grid_next[new_i, new_j] = clock_grid_now[i, j] + 1
    return clock_grid_now, clock_grid_next


def statistic_info(i, j, grid, info):
    n_people = size
    if grid[i,j] == NS:
        info['sick'] += 1
    if grid[i, j] == NH:
        info['healthy'] += 1
    if grid[i, j] == NH:
        info['vaccinated_recovering'] += 1
    return info


def update(frameNum, img, grid, size, clock_grid_now, clock_grid_next, ax):
    # each cell has 8 neighbors
    # for calculation and we go line by line
    # newGrid = grid.copy()
    newGrid = np.zeros((size, size), dtype=int)
    # create movementGrid which represent which cell is available in the next generation
    # and which is captured by another cell,
    movementGrid = np.zeros((size, size), dtype=int)
    clock_grid_next = np.zeros((size, size), dtype=int)
    for i in range(size):
        for j in range(size):
            # if cell is not empty
            if grid[i, j] != EC:
                # select new move for cell[i,j]
                move = select_move(i, j, movementGrid, grid)
                new_i, new_j = new_place(i, j, move)
                # check if cell [i,j] has a sick (NS) neighbor. return True or False
                sickNeighbor = check_neighbor(i, j, grid, NS)
                # for sick people count how many iteration they sick
                clock_grid_now, clock_grid_next = clock_sick_generation(i, j, new_i, new_j, grid, clock_grid_now, clock_grid_next)
                newGrid[new_i, new_j] = get_value(i, j,new_i,new_j, grid, sickNeighbor, clock_grid_next)
                # report that this cell is not available in this generation
                movementGrid[new_i, new_j] = 1
                #ax.text(i, j, newGrid[i, j], ha="center", va="center", color="k", visible="True")

    firstStep = 0
    secondStep = 0
    thirdStep = 0
    recoverd = 0
    for i in range (size):
        for j in range (size):
            if clock_grid_next[i,j] == 1:
                firstStep += 1
            elif clock_grid_next[i,j] == 2:
                secondStep += 1
            if clock_grid_next[i,j] == 3:
                thirdStep += 1
    for i in range (size):
        for j in range (size):
            if newGrid[i,j] == 3:
                recoverd += 1
    recoverd = recoverd
    print(newGrid)
    print("continue")
    # update data
    img.set_data(newGrid)
    grid[:] = newGrid[:]
    clock_grid_now[:] = clock_grid_next[:]
    return img

# main() function
def main():
    # set animation update interval
    updateInterval = 200
    grid = createGrid()

    # set up animation
    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest')
    # life clock - count generations
    clock_grid_now = np.zeros((size,size),dtype=int)
    # initialize life clock - when write 2, check 1
    for i in range(size):
        for j in range(size):
            if grid[i, j] == 2:
                clock_grid_now[i, j] = 1
    clock_grid_next = np.zeros((size, size), dtype=int)
    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, size, clock_grid_now, clock_grid_next, ax),
                                  frames=10,
                                  interval=updateInterval)
    # addGlider(0,0,grid)
    plt.show()


# call main
if __name__ == '__main__':
    main()
    # grid = np.matrix([[1, 2,5], [3, 4,6]])
    # print(grid)
    # print(grid[0,-1])