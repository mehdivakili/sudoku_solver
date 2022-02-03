import pygame

sudoku_levels = []


def init_board():
    board = []
    print("")
    print("Please enter sudoku numbers:")
    for i in range(9):
        row = []
        row_str = input()
        for c in row_str:
            if c == '?':
                c = 0
            row += [int(c)]
        board += [row]


    return board


def get_row(sudoku_board, i):
    return sudoku_board[i]


def get_column(sudoku_board, j):

    return [sudoku_board[i][j] for i in range(9)]


def get_cell(sudoku_board, cell_index):
    s_i = (cell_index // 3) * 3
    s_j = (cell_index % 3) * 3
    return [sudoku_board[i][j] for i in range(s_i, s_i + 3) for j in range(s_j, s_j + 3)]


def get_any(sudoku_board, i, type_to_get):
    if type_to_get == "row":
        return get_row(sudoku_board, i)
    if type_to_get == "column":
        return get_column(sudoku_board, i)
    if type_to_get == "cell":
        return get_cell(sudoku_board, i)


def set_row(sudoku_board, i, row, greens=()):
    global sudoku_levels
    sudoku_board[i] = row
    if sudoku_board != sudoku_levels[-1]["sudoku"]:
        sudoku_levels += [{"sudoku": get_copy(sudoku_board), "greens": greens, "focus": {"type": "row", "i": i}}]


def set_column(sudoku_board, j, column, greens=()):
    global sudoku_levels
    for i in range(9):
        sudoku_board[i][j] = column[i]
    if sudoku_board != sudoku_levels[-1]["sudoku"]:
        sudoku_levels += [{"sudoku": get_copy(sudoku_board), "greens": greens, "focus": {"type": "column", "j": j}}]


def set_cell(sudoku_board, cell_index, cell, greens=()):
    global sudoku_levels
    s_i = (cell_index // 3) * 3
    s_j = (cell_index % 3) * 3
    for c_i in range(9):
        i = c_i // 3 + s_i
        j = c_i % 3 + s_j
        sudoku_board[i][j] = cell[c_i]
    if sudoku_board != sudoku_levels[-1]["sudoku"]:
        sudoku_levels += [
            {"sudoku": get_copy(sudoku_board), "greens": greens, "focus": {"type": "cell", "cell_index": cell_index}}]


def set_any(sudoku_board, i, arr, type_to_set, greens=()):
    if type_to_set == "row":
        return set_row(sudoku_board, i, arr, greens)
    if type_to_set == "column":
        return set_column(sudoku_board, i, arr, greens)
    if type_to_set == "cell":
        return set_cell(sudoku_board, i, arr, greens)


def get_candidates_sudoku_board(sudoku_board):
    candidates_sudoku_board = [[[] for _ in range(9)] for _ in range(9)]

    for i in range(9):
        for j in range(9):
            if sudoku_board[i][j] != 0:
                candidates_sudoku_board[i][j] = [sudoku_board[i][j]]
                continue

            for num in range(1, 10):
                cell_index = (i // 3) * 3 + j // 3

                if num not in get_row(sudoku_board, i) + get_column(sudoku_board, j) + get_cell(sudoku_board,
                                                                                                cell_index):
                    candidates_sudoku_board[i][j] += [num]

    return candidates_sudoku_board


def is_solved(sudoku_board):
    for row in sudoku_board:
        for candidates in row:
            if len(candidates) != 1:
                return False
    return True


def delete_num(arr, pos, num):
    for i in range(len(arr)):
        if i == pos:
            arr[pos] = [num]
            continue
        first_j = len(arr[i])
        for candidates_index in range(len(arr[i])):
            if arr[i][candidates_index] == num:
                first_j = candidates_index
                break
        arr[i] = arr[i][:first_j] + arr[i][first_j + 1:]

    return arr


def delete_candidates(board, i, j, num):
    greens = [{"nums": [num], "positions": [(i, j)]}]
    set_row(board, i, delete_num(get_row(board, i), j, num), greens)
    set_column(board, j, delete_num(get_column(board, j), i, num), greens)
    cell_index = (i // 3) * 3 + j // 3
    num_pos = (i % 3) * 3 + j % 3
    set_cell(board, cell_index, delete_num(get_cell(board, cell_index), num_pos, num), greens)


def get_num_poses(sudoku_row):
    num_dict = create_num_count_dict()
    for candidates_index in range(len(sudoku_row)):
        for num in sudoku_row[candidates_index]:
            num_dict[num] += [candidates_index]
    return num_dict


def naked_single(candidates_sudoku_board):
    old = get_copy(candidates_sudoku_board)
    for index in range(9):
        for type_ in ["row", "column", "cell"]:
            candidates_row = get_any(candidates_sudoku_board, index, type_)
            for candidates in range(len(candidates_row)):
                if len(candidates_row[candidates]) == 1:
                    if type_ == "row":
                        i = index
                        j = candidates
                    elif type_ == "column":
                        i, j = candidates, index
                    else:
                        i, j = (index // 3) * 3 + candidates // 3, (index % 3) * 3 + candidates % 3
                    delete_candidates(candidates_sudoku_board, i, j, candidates_row[candidates][0])
    return old == candidates_sudoku_board


def hidden_single(candidates_sudoku_board):
    old = get_copy(candidates_sudoku_board)
    for index in range(9):
        for type_ in ["row", "column", "cell"]:
            candidates_row = get_any(candidates_sudoku_board, index, type_)
            nums_poses = get_num_poses(candidates_row)
            for digit in nums_poses:
                if len(nums_poses[digit]) == 1:
                    if type_ == "row":
                        i = index
                        j = nums_poses[digit][0]
                    elif type_ == "column":
                        i, j = nums_poses[digit][0], index
                    else:
                        i, j = (index // 3) * 3 + nums_poses[digit][0] // 3, (index % 3) * 3 + nums_poses[digit][
                            0] % 3
                    if len(candidates_sudoku_board[i][j]) != 1:
                        candidates_row[nums_poses[digit][0]] = [digit]
                        set_any(candidates_sudoku_board, index, candidates_row, type_,
                                [{"nums": [digit], "positions": [(i, j)]}])
                        return False

    return old == candidates_sudoku_board


def solve_simple_cells(candidates_sudoku_board):
    if naked_single(candidates_sudoku_board):
        return hidden_single(candidates_sudoku_board)
    return False


def combination(arr, r):
    out = []
    if len(arr) == r:
        return [arr]
    if r <= 0:
        return [[]]

    for set_ in combination(arr[1:], r - 1):
        out += [[arr[0]] + set_]
    out += combination(arr[1:], r)
    return out


def intersect(sets):
    inter = []
    if len(sets) == 2:
        for el in sets[0] + sets[1]:
            if el not in inter:
                inter += [el]
        return inter
    return intersect([sets[0], intersect(sets[1:])])


def search_naked(arr, n):
    indexes = []
    for i_list in combination(list(range(9)), n):
        candidates = [arr[i] for i in i_list if len(arr[i]) != 1]
        if len(candidates) != n:
            continue
        u = intersect(candidates)
        if len(u) == n:
            indexes += [{"nums": u, "positions": i_list}]
    return indexes


def naked(arr, n):
    indexes = search_naked(arr, n)
    for naked_candidates in indexes:
        for i in range(9):
            candidates = []
            if i in naked_candidates["positions"]:
                continue
            for num in arr[i]:
                if num not in naked_candidates["nums"]:
                    candidates += [num]
            arr[i] = candidates
    return indexes


def naked_cells_row(candidates_sudoku_board, i, n):
    row = get_row(candidates_sudoku_board, i)
    indexes = naked(row, n)
    if indexes:
        for naked_i in range(len(indexes)):
            indexes[naked_i]["positions"] = [(i, j) for j in indexes[naked_i]["positions"]]
    set_row(candidates_sudoku_board, i, row, indexes)
    return indexes


def naked_cells_column(candidates_sudoku_board, j, n):
    column = get_column(candidates_sudoku_board, j)
    indexes = naked(column, n)
    if indexes:
        for naked_i in range(len(indexes)):
            indexes[naked_i]["positions"] = [(i, j) for i in indexes[naked_i]["positions"]]
    set_column(candidates_sudoku_board, j, column, indexes)
    return indexes


def naked_cells_cell(candidates_sudoku_board, cell_index, n):
    cell = get_cell(candidates_sudoku_board, cell_index)
    indexes = naked(cell, n)
    if indexes:
        s_i = cell_index // 3 * 3
        s_j = (cell_index % 3) * 3
        for naked_i in range(len(indexes)):
            indexes[naked_i]["positions"] = [(s_i + c_i // 3, s_j + c_i % 3) for c_i in indexes[naked_i]["positions"]]
    set_cell(candidates_sudoku_board, cell_index, cell, indexes)
    return indexes


def solve_naked_cells(candidates_sudoku_board, n):
    old = get_copy(candidates_sudoku_board)
    for i in range(9):
        naked_cells_row(candidates_sudoku_board, i, n)
        naked_cells_column(candidates_sudoku_board, i, n)
        naked_cells_cell(candidates_sudoku_board, i, n)
    return old == candidates_sudoku_board


def create_num_count_dict():
    nums = {}
    for i in range(1, 10):
        nums[i] = []
    return nums


def search_hidden(nums_dict, n):
    hidden_nums = []
    for i_list in combination(list(range(1, 10)), n):
        candidates = [nums_dict[i] for i in i_list if len(nums_dict[i]) != 1]
        if len(candidates) != n:
            continue
        uni = intersect(candidates)
        if len(uni) == n:
            hidden_nums += [{"nums": i_list, "positions": uni}]
    return hidden_nums


def hidden(arr, n):
    nums_dict = get_num_poses(arr)
    hidden_nums = search_hidden(nums_dict, n)
    for hidden_el in hidden_nums:
        for i in hidden_el["positions"]:
            candidates = []
            for num in arr[i]:
                if num in hidden_el["nums"]:
                    candidates += [num]
            arr[i] = candidates
    return hidden_nums


def hidden_cells_row(candidates_sudoku_board, i, n):
    row = get_row(candidates_sudoku_board, i)
    hidden_nums = hidden(row, n)
    if hidden_nums:
        for hidden_i in range(len(hidden_nums)):
            hidden_nums[hidden_i]["positions"] = [(i, j) for j in hidden_nums[hidden_i]["positions"]]
    set_row(candidates_sudoku_board, i, row, hidden_nums)
    return hidden_nums


def hidden_cells_column(candidates_sudoku_board, j, n):
    column = get_column(candidates_sudoku_board, j)
    hidden_nums = hidden(column, n)
    if hidden_nums:
        for hidden_i in range(len(hidden_nums)):
            hidden_nums[hidden_i]["positions"] = [(i, j) for i in hidden_nums[hidden_i]["positions"]]
    set_column(candidates_sudoku_board, j, column, hidden_nums)
    return hidden_nums


def hidden_cells_cell(candidates_sudoku_board, cell_index, n):
    cell = get_cell(candidates_sudoku_board, cell_index)
    hidden_nums = hidden(cell, n)
    if hidden_nums:
        s_i = cell_index // 3 * 3
        s_j = (cell_index % 3) * 3
        for naked_i in range(len(hidden_nums)):
            hidden_nums[naked_i]["positions"] = [(s_i + c_i // 3, s_j + c_i % 3) for c_i in
                                                 hidden_nums[naked_i]["positions"]]
    set_cell(candidates_sudoku_board, cell_index, cell, hidden_nums)
    return hidden_nums


def get_copy(candidates_sudoku_board):
    return [[candidates_sudoku_board[i][j][:] for j in range(9)] for i in range(9)]


def solve_hidden_cells(candidates_sudoku_board, n):
    old = get_copy(candidates_sudoku_board)
    for i in range(9):
        hidden_cells_row(candidates_sudoku_board, i, n)
        hidden_cells_column(candidates_sudoku_board, i, n)
        hidden_cells_cell(candidates_sudoku_board, i, n)
    return old == candidates_sudoku_board


def solve_naked_and_hidden_cells(candidates_sudoku_board):
    for n in range(2, 5):
        if solve_naked_cells(candidates_sudoku_board, n) and solve_hidden_cells(candidates_sudoku_board, n):
            continue
        return False
    return True


def select_candidates_by_naked_pair(candidates_sudoku_board):
    while not is_solved(candidates_sudoku_board):
        if (
                solve_simple_cells(candidates_sudoku_board) and
                solve_naked_and_hidden_cells(candidates_sudoku_board)):
            break
        continue

    return candidates_sudoku_board


def solve(sudoku_board):
    global sudoku_levels
    candidates_sudoku_board = get_candidates_sudoku_board(sudoku_board)
    sudoku_levels += [{"sudoku": get_copy(candidates_sudoku_board), "greens": [], "focus": {"type": None}}]
    sudoku_levels += [{"sudoku": get_copy(candidates_sudoku_board), "greens": [], "focus": {"type": None}}]
    sudoku_board_solved = select_candidates_by_naked_pair(candidates_sudoku_board)
    sudoku_levels += [{"sudoku": get_copy(candidates_sudoku_board), "greens": [], "focus": {"type": None}}]
    return sudoku_board_solved


def draw_multi_number_lines(screen, size, margin, sudoku):
    max_ = size[0] - margin[0]
    min_ = margin[0]
    len_ = (max_ - min_) / 9
    small_len = len_ / 3
    for i in range(9):
        for j in range(9):
            if len(sudoku[i][j]) == 1:
                continue
            small_min_x = j * len_ + min_
            small_min_y = i * len_ + min_
            small_max_x = small_min_x + len_
            small_max_y = small_min_y + len_

            for c in range(1, 3):
                pos_x = small_min_x + c * small_len
                pos_y = small_min_y + c * small_len
                pygame.draw.line(screen, (0, 0, 0), (pos_x, small_min_y), (pos_x, small_max_y))
                pygame.draw.line(screen, (0, 0, 0), (small_min_x, pos_y), (small_max_x, pos_y))


def draw_sudoku_board(screen, size, margin):
    max_ = size[0] - margin[0]
    min_ = margin[0]
    for i in range(0, 10):
        width = 2
        if i % 3 == 0:
            width = 4

        pos = (max_ - min_) / 9 * i + min_

        pygame.draw.line(screen, (0, 0, 0), (pos, min_), (pos, max_), width)
        pygame.draw.line(screen, (0, 0, 0), (min_, pos), (max_, pos), width)


def draw_number_in_board(screen, size, margin, sudoku, font_size):
    font_name = "Times new Roman"
    font = pygame.font.SysFont(font_name, font_size)
    max_ = size[0] - margin[0]
    min_ = margin[0]
    len_ = (max_ - min_) / 9
    for i in range(9):
        for j in range(9):
            if len(sudoku[i][j]) != 1:
                continue
            num = sudoku[i][j][0]
            text = font.render(str(num), True, (0, 0, 0))
            pos_x = j * len_ + (len_ - text.get_width()) / 2 + min_
            pos_y = i * len_ + (len_ - text.get_height()) / 2 + min_

            screen.blit(text, (pos_x, pos_y))


def draw_multi_number_in_board(screen, size, margin, new_sudoku, old_sudoku, font_size):
    font_name = "Times new Roman"
    font = pygame.font.SysFont(font_name, font_size)
    max_ = size[0] - margin[0]
    min_ = margin[0]
    len_ = (max_ - min_) / 9
    small_len = len_ / 3
    for i in range(9):
        for j in range(9):
            if len(new_sudoku[i][j]) == 1 and new_sudoku[i][j] == old_sudoku[i][j]:
                continue
            candidates = new_sudoku[i][j]
            small_min_x = j * len_ + min_
            small_min_y = i * len_ + min_
            for num in candidates:
                text = font.render(str(num), True, (0, 0, 0))
                small_i = (num - 1) // 3
                small_j = (num - 1) % 3
                pos_x = small_min_x + small_j * small_len + (small_len - text.get_width()) / 2
                pos_y = small_min_y + small_i * small_len + (small_len - text.get_height()) / 2
                screen.blit(text, (pos_x, pos_y))


def check_added_sudoku_number(screen, size, margin, new_sudoku, old_sudoku):
    max_ = size[0] - margin[0]
    min_ = margin[0]
    len_ = (max_ - min_) / 9
    greens = new_sudoku["greens"]
    for green in greens:
        for poses in green["positions"]:
            pos_x = poses[1] * len_ + min_
            pos_y = poses[0] * len_ + min_
            for num in new_sudoku["sudoku"][poses[0]][poses[1]]:
                if num in green["nums"] and len(old_sudoku["sudoku"][poses[0]][poses[1]]) == 1:
                    rect = pygame.Rect(pos_x, pos_y, len_, len_)
                    pygame.draw.rect(screen, (0, 255, 0), rect)


def check_added_multi_sudoku_number(screen, size, margin, new_sudoku, old_sudoku, font_size):
    font_name = "Times new Roman"
    font = pygame.font.SysFont(font_name, font_size)
    max_ = size[0] - margin[0]
    min_ = margin[0]
    len_ = (max_ - min_) / 9
    small_len = len_ / 3
    for i in range(9):
        for j in range(9):
            if (len(new_sudoku["sudoku"][i][j]) == 1 and new_sudoku["sudoku"][i][j] == old_sudoku["sudoku"][i][j]) or \
                    new_sudoku["sudoku"][i][j] == \
                    old_sudoku["sudoku"][i][j]:
                continue
            candidates = [num for num in old_sudoku["sudoku"][i][j] if num not in new_sudoku["sudoku"][i][j]]
            small_min_x = j * len_ + min_
            small_min_y = i * len_ + min_
            for num in candidates:
                text = font.render(str(num), True, (0, 0, 0))
                small_i = (num - 1) // 3
                small_j = (num - 1) % 3
                pos_x = small_min_x + small_j * small_len
                pos_y = small_min_y + small_i * small_len
                rect = pygame.Rect(pos_x + 1, pos_y + 1, small_len, small_len)
                pygame.draw.rect(screen, (255, 80, 80), rect)
                screen.blit(text,
                            (pos_x + (small_len - text.get_width()) / 2, pos_y + (small_len - text.get_height()) / 2))
    greens = new_sudoku["greens"]
    for green in greens:
        for poses in green["positions"]:
            small_min_x = poses[1] * len_ + min_
            small_min_y = poses[0] * len_ + min_
            for num in new_sudoku["sudoku"][poses[0]][poses[1]]:
                if num in green["nums"] and len(old_sudoku["sudoku"][poses[0]][poses[1]]) != 1:
                    text = font.render(str(num), True, (0, 0, 0))
                    small_i = (num - 1) // 3
                    small_j = (num - 1) % 3
                    pos_x = small_min_x + small_j * small_len
                    pos_y = small_min_y + small_i * small_len
                    rect = pygame.Rect(pos_x + 1, pos_y + 1, small_len, small_len)
                    pos_x += (small_len - text.get_width()) / 2
                    pos_y += (small_len - text.get_height()) / 2
                    pygame.draw.rect(screen, (0, 255, 0), rect)
                    screen.blit(text, (pos_x, pos_y))


def draw_first_sudoku(screen, size, margin, sudoku, font_size):
    font_name = "Times new Roman"
    font = pygame.font.SysFont(font_name, font_size)
    max_ = size[0] - margin[0]
    min_ = margin[0]
    len_ = (max_ - min_) / 9
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] == 0:
                continue
            num = sudoku[i][j]
            text = font.render(str(num), True, (0, 0, 0))
            pos_x = j * len_ + (len_ - text.get_width()) / 2 + min_
            pos_y = i * len_ + (len_ - text.get_height()) / 2 + min_

            screen.blit(text, (pos_x, pos_y))


def set_focus(screen, size, margin, sudoku):
    max_ = size[0] - margin[0]
    min_ = margin[0]
    len_ = (max_ - min_) / 9
    color = (100, 255, 255)
    focus = sudoku["focus"]
    if focus["type"] == "row":
        rect = pygame.Rect(min_, min_ + focus["i"] * len_, len_ * 9, len_)
        pygame.draw.rect(screen, color, rect)
    elif focus["type"] == "column":
        rect = pygame.Rect(min_ + focus["j"] * len_, min_, len_, len_ * 9)
        pygame.draw.rect(screen, color, rect)
    elif focus["type"] == "cell":
        rect = pygame.Rect(min_ + focus["cell_index"] % 3 * len_ * 3, min_ + focus["cell_index"] // 3 * len_ * 3,
                           len_ * 3, len_ * 3)
        pygame.draw.rect(screen, color, rect)
    else:
        pass


def draw_text(screen, size):
    font_name = "Times new Roman"
    font = pygame.font.SysFont(font_name, 40)
    text = font.render("sudoku solve", True, (0, 0, 0))
    screen.blit(text, ((size[0] - text.get_width()) / 2, 10))


def show_sudoku(sudoku_board):
    global sudoku_levels
    max_ = len(sudoku_levels)
    pygame.init()
    size = (600, 600)
    margin = (60, 60)

    # Set up the drawing window
    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))
    draw_sudoku_board(screen, size, margin)
    draw_first_sudoku(screen, size, margin, sudoku_board, 40)
    i = 1

    # Run until the user asks to quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                exit(0)
                break
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN) or (
                    event.type == pygame.KEYUP and event.key == pygame.K_UP):
                if i == 0:
                    i = 1
                elif i == max_:
                    i = max_ - 1
                screen.fill((255, 255, 255))
                set_focus(screen, size, margin, sudoku_levels[i])
                check_added_sudoku_number(screen, size, margin, sudoku_levels[i], sudoku_levels[i - 1])
                check_added_multi_sudoku_number(screen, size, margin, sudoku_levels[i], sudoku_levels[i - 1], 15)
                draw_sudoku_board(screen, size, margin)
                draw_multi_number_lines(screen, size, margin, sudoku_levels[i - 1]["sudoku"])
                draw_number_in_board(screen, size, margin, sudoku_levels[i - 1]["sudoku"], 40)
                draw_multi_number_in_board(screen, size, margin, sudoku_levels[i]["sudoku"],
                                           sudoku_levels[i - 1]["sudoku"], 15)
                draw_text(screen, size)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    i += 1
                else:
                    i -= 1

        pygame.display.flip()


def show_sudoku_console(sudoku):
    for i in range(9):
        for j in range(9):
            if len(sudoku[i][j]) != 1:
                print('?', end='')
                continue
            print(sudoku[i][j][0], end='')
        print()


def main():
    sudoku_board = init_board()
    sudoku = solve(sudoku_board)
    show_sudoku(sudoku_board)
    #show_sudoku_console(sudoku)


main()
