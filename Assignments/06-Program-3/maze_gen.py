from random import shuffle, randrange, choice, seed, randint
import os, sys
from platform import system as system_name # Returns the system/OS name
from os import system as system_call       # Execute a shell command
import time 


"""
Globals to represent walls or lack of in each cell.
"""
NSBARRIER = "+--"
NSOPEN = "+  "
EWBARRIER = "|  "
EWOPEN = "   "





def clear_screen():
    """Clears the terminal screen on windows or linux.
    """
    # Clear command as function of OS
    command = "-cls" if system_name().lower()=="windows" else "clear"
    # Action
    system_call(command)

def terminal_size():
    """Gets the width and height of terminal.
    """
    return (os.popen('stty size', 'r').read().split())

class Cell(object):
    """ A single cell within the maze
    """
    def __init__(self,row=None,col=None):
        self.row = row
        self.col = col
        self.visited = False
        self.top = NSBARRIER
        self.left = EWBARRIER
        self.path = False 
        self.direction = ''

    def __str__(self):
        return "[ [row:%d, col:%d], vis: %s, top: %s, left:%s ]" % (self.row,self.col,self.visited,self.top,self.left)
        

class Maze(object):
    """ A 2D grid of Cell objects representing a maze. 
        Public Methods:
            print_maze()
            set_start(row,col)
            set_exit(row,col)
        Private Methods:
            __build_maze()                  # Turns 2D array into maze
            __get_direction(r1,c1,r2,c2)    # Which direction did I move (North,South,East,West)
            __in_bounds(row,col)            # Is cell within the bounds of array
            __init_maze()                   # Create 2D array of cells
            __is_exit(cell)                 # Is cell the maze exit
            __unvisited_neighbors(row,col)  # Which directions can I move
            __reset_maze()                  # Reset all "visited" to False
    """
    def __init__(self,rows=32,cols=16,progress=True):
        self.height = rows                  # num rows in maze
        self.width = cols                   # num cols in maze
        self.maze = []                      # 2D list maze container
        self.move_stack = []                # Stack of moves used to build maze
        self.print_progress = progress      # Print build progress to screen.

        self.__init_maze()                  # Creates rows*cols Cells in maze
        self.__build_maze()                 # DFS build maze                                    
        self.__reset_maze()                 # Mark all cells as not visited 

        self.start = self.maze[0][0]        # Mark entrance to maze            
        self.exit = self.maze[-1][-1]       # Mark exit to maze 



    def print_maze(self):
        """ Clears the screenm then prints the maze to stdout.
            Returns: None
        """
        clear_screen()
        #time.sleep(.02)
        out_maze = self.__str__()

        arrows = {
            'N': u'\u21C8',
            'S': u'\u21CA',
            'E': u'\u21C9',
            'W': u'\u21C7'
        }

        # out_maze = out_maze.replace('#',u'\u2588')
        # out_maze = out_maze.replace('N',arrows['N'])
        # out_maze = out_maze.replace('S',arrows['S'])
        # out_maze = out_maze.replace('E',arrows['E'])
        # out_maze = out_maze.replace('W',arrows['W'])
        print(out_maze)

    def set_start(self,row,col):
        """ Sets the starting cell of the maze.
            Returns: None
        """
        self.start = self.maze[row][col]

    def set_exit(self,row,col):
        """ Sets the exiting cell of the maze.
            Returns: None
        """
        self.exit = self.maze[row][col]

    def __possible_moves(self,row,col):
        prospects = [(row - 1, col), (row, col + 1), (row + 1, col), (row, col - 1)]
        moves = []

        for r,c in prospects:
            if not self.__in_bounds(r,c):
                continue
            elif not self.maze[r][c].visited and self.__is_hallway(self.maze[row][col],self.maze[r][c]):
                moves.append((r,c))
        shuffle(moves)
        return moves

    def __is_hallway(self,cell1,cell2):
        """ Determines if there is a hallway between cell1 to cell2.
            Returns: Boolean
        """
        d = self.__get_direction(cell1.row,cell1.col,cell2.row,cell2.col)
        if  d == "North":
            return cell1.top == NSOPEN
        elif d == "East":
            return cell2.left == EWOPEN
        elif d == "South":
            return cell2.top == NSOPEN
        elif d == "West":
            return cell1.left == EWOPEN
        

    def solve_maze(self):
        self.move_stack = []

        # Prime the move stack with the "first" move.
        self.move_stack.append(self.start)
        self.start.path = True
            
        # While there are still cells to be visited:
        while len(self.move_stack) > 0:
            # Print maze to standard out if desired.
            #if self.print_progress:
            self.print_maze()
            
            # Set current to top of stack (end of list)
            current = self.move_stack[-1]

            if current == self.exit:
                sys.exit()

            # Mark current as visited
            current.visited = True

            # Get a list of possible moves from our current location
            moves = self.__possible_moves(current.row,current.col)
            
            # If there are moves:
            if len(moves):
                # Get move out of the random move list 
                # and make that our next location
                # (were moving from current => neighbor)
                dr,dc = moves.pop()
                neighbor = self.maze[dr][dc]

                neighbor.direction = self.__get_direction(current.row,current.col,neighbor.row,neighbor.col)[0]

                # Set the cell to visited
                neighbor.visited = True
                neighbor.path = True

                # Put neighber cell on top of stack
                self.move_stack.append(neighbor)

            # No moves = backtrack 
            else:
                popped = self.move_stack.pop()
                popped.path = False

    

    def __build_maze(self):
        """ Essentially a depth first search to walk a 2D grid randomly knocking down walls to create maze.
            This method is started in the constructor and primed with a single cell on a "stack" of "moves".
            While the stack has a cell in it, the entire grid has not been visited. When the current cell has
            no where to move to, it pops the cell off the stack, essentially backtracking to a previous state
            and looking for unvisited cells. 
        """

        # Prime the move stack with the "first" move.
        self.move_stack.append(self.maze[randrange(self.height)][randrange(self.width)])
            
        # While there are still cells to be visited:
        while len(self.move_stack) > 0:
            # Print maze to standard out if desired.
            if self.print_progress:
                self.print_maze()
            
            # Set current to top of stack (end of list)
            current = self.move_stack[-1]

            # Mark current as visited
            current.visited = True

            # Get a list of possible moves from our current location
            moves = self.__unvisited_neighbors(current.row,current.col)
            
            # If there are moves:
            if len(moves):
                # Get move out of the random move list 
                # and make that our next location
                # (were moving from current => neighbor)
                dr,dc = moves.pop()
                neighbor = self.maze[dr][dc]

                # Set the cell to visited
                neighbor.visited = True

                # Determine what direction we moved to get from current => neighbor
                # (north,south,east,west)
                d = self.__get_direction(current.row,current.col,dr,dc)
   
                # This block determines which "wall" to knock down.
                # A cell holds its own north and west walls. Its 
                # neighbor holds the south and east walls. 
                if d == 'North':
                    current.top = NSOPEN
                elif d == 'East':
                    neighbor.left = EWOPEN
                elif d == 'South':
                    neighbor.top = NSOPEN
                elif d == 'West':
                    current.left = EWOPEN

                # Put neighber cell on top of stack
                self.move_stack.append(neighbor)

            # No moves = backtrack 
            else:
                pop = self.move_stack.pop()

    def __get_direction(self,r1,c1,r2,c2):
        """ Determines direction moved going from cell (r1,c1) => (r2,c2). Used to determine
            which wall to knock down when building the maze.
            Returns: (string , None)
        """
        if r2 < r1:
            return 'North'
        elif c2 > c1:
            return 'East'
        elif r2 > r1:
            return 'South'
        elif c2 < c1:
            return 'West'
        else:
            return None

    def __in_bounds(self,row,col):
        """ Test to see if coords are on the maze.
            Returns: boolean 
        """
        return (row < self.height and col < self.width) and (row >= 0 and col >= 0)

    def __init_maze(self):
        """ Create a new cell for each maze location
        """
        for row in range(self.height):
            self.maze.append([])
            for col in range(self.width):
                self.maze[-1].append(Cell(row,col))

    def __is_exit(self,cell):
        """ Checks to see of the cell passed in, is the exit to the maze. 
            Returns: boolean
        """
        return cell.row == self.exit.row and cell.col == self.exit.col

    def __log(self,m):
        """ Helps debug errors. 
            Usage: `tail -f log.txt` in another terminal window to see logged messages without 
                   messing with maze output.
        """
        self.log = open('log.txt','a')
        if type(m) is list or type(m) is tuple:
            for i in m:
                i = i.__str__()
                self.log.write(i+'\n')
            self.log.write('\n')
        elif type(m) is Cell:
            self.log.write(m.__str__())
            self.log.write('\n')
        else:
            self.log.write(m)
            self.log.write('\n')
        self.log.close()

    def __unvisited_neighbors(self,row,col):
        """ Creates a randomized list of possible direction(s) (if any) that can be moved to from row,col. 
            Returns: list 
        """
        attempts = [(row - 1, col), (row, col + 1), (row + 1, col), (row, col - 1)]
        moves = []

        for r,c in attempts:
            if not self.__in_bounds(r,c):
                continue
            elif not self.maze[r][c].visited:
                moves.append((r,c))
        shuffle(moves)
        return moves
        
    def __reset_maze(self):
        """Mark each cell in maze as not visited.
        """
        for row in range(self.height):
            for col in range(self.width):
                self.maze[row][col].visited = False

    def __str__(self):
        """ String representation of the maze. 
            Returns: string
        """
        strmz = ""
        pmaze = []
        for row in self.maze:
            top = []
            left = []
            for cell in row:
                top.append(cell.top)
                marker = cell.left
                if cell.path:
                    #marker = marker[0] + '# '
                    marker = marker[0] + cell.direction + ' '                    
                left.append(marker)                
            pmaze.append(top)
            pmaze.append(left)
        for row in pmaze:
            strmz += ''.join(map(str, row)) + '|'
            strmz += '\n'
        strmz += NSBARRIER * self.width + '+'

        return strmz.decode('utf-8')


def print_usage():
    print("Usage: Need a width and height.\ne.g. python maze_gen.py 24 24")

def run_test():
    if len(sys.argv) != 3:
        print_usage()
        rows,cols = terminal_size()

        rows = int(float(rows) *.45)
        cols = int(float(cols) *.30)
    else:
        rows = sys.argv[1]
        cols = sys.argv[2]

    M = Maze(int(rows),int(cols),True)
    M.print_maze()
    M.solve_maze()

if __name__ == '__main__':
    #seed(2234)
    clear_screen()
    run_test()