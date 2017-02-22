assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def remove_naked_twins_values(values, twins):
    """Utility function to eliminate naked twins values as possibilities from their peers.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        twins(tuple): a tuple indicating naked twins found in a give unit
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    jointPeers = peers[twins[0]].copy()
    jointPeers = jointPeers.intersection(peers[twins[1]]) - set([twins[0], twins[1]])
    for peer in jointPeers:
        if values[twins[0]][0] in values[peer]:
            values = assign_value(values, peer, values[peer].replace(values[twins[0]][0], ''))
        if values[twins[0]][1] in values[peer]:
            values = assign_value(values, peer, values[peer].replace(values[twins[0]][1], ''))
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    nakedTwinsRows = {}
    for box in boxes:
        if len(values[box]) == 2:
            currValue = ''.join(sorted(values[box]))
            for peer in peers[box]:
                peerValue = ''.join(sorted(values[peer]))
                if peerValue == currValue:
                    if peerValue not in nakedTwinsRows:
                        nakedTwinsRows[peerValue] = set([(box, peer)])
                        # Eliminate the naked twins as possibilities for their peers
                        values = remove_naked_twins_values(values, (box, peer))
                    elif (peer, box) not in nakedTwinsRows[peerValue]:
                        nakedTwinsRows[peerValue].add((box,peer))
                        # Eliminate the naked twins as possibilities for their peers
                        values = remove_naked_twins_values(values, (box, peer))

    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81
    default = '123456789'
    return dict((boxes[i], grid[i] if grid[i] != '.' else default) for i in range(len(grid)))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solvedBoxes = [box for box in values if len(values[box]) == 1]
    for box in solvedBoxes:
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(values[box], ''))
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # TODO: Implement only choice strategy here
    for unit in unitlist:
        for digit in cols:
            foundMatches = []
            for box in unit:
                if digit in values[box]:
                    foundMatches.append(box)
            if len(foundMatches) == 1:
                values = assign_value(values, foundMatches[0], digit)
    return values

def reduce_puzzle(values):
    """Reduce the puzzle using the elimination, only choice and naked twins
       strategies.
       
       Input: Sudoku in dictionary form.
       Output: Resulting Sudoku in dictionary form after eliminating, filling
       in only choices and removing naked twin box values from peers.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Use the Only Choice Strategy
        values = only_choice(values)

        # Use the Naked Twins Strategy
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    '''search recursively creates a search tree using the depth first search algorithm
       for potential solutions to the puzzle.
       
       Input: Sudoku in dictionary form.
       Output: Returns a sudoku solution in dictionary form or False if it is unable to
       solve the puzzle.
    '''
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    # Choose one of the unfilled squares with the fewest possibilities
    nextCandidate = None
    leastPossibilities = 10
    solved = True
    for box in boxes:
        candidatesLength = len(values[box])
        if candidatesLength <= leastPossibilities and candidatesLength > 1:
            leastPossibilities = candidatesLength
            nextCandidate = box
            solved = False

    if solved:
        return values
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for potential in values[nextCandidate]:
        newValues = values.copy()
        newValues = assign_values(newValues, nextCandidate, potential)
        ret = search(newValues)
        if ret:
            return ret

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

# List of all boxes on the grid
boxes = cross(rows, cols)

# List of row units on the grid
row_units = [cross(r, cols) for r in rows]

# List of column units on the grid
column_units = [cross(rows, c) for c in cols]

# List of square units on the grid
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

# List of diagonal units on the grid
#diag_units = [cross(rows, cols)[0::10], cross(rows, cols[::-1])[0::10]]
diag_units = [[r+c for r,c in zip(rows, cols)], [r+c for r,c in zip(rows, cols[::-1])]]

# List of all units (row, column & square) on the grid
unitlist = row_units + column_units + square_units + diag_units

# Dictionary of boxes and lists of units they belong to
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

# Dictionary of boxes and set of peers
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
