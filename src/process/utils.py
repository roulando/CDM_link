
def generate_index_lists(total_length, n_l):
    index_list = []
    per_process = total_length//n_l
    for i in range(0, total_length//per_process ):
        end_index = total_length if i == total_length//per_process-1 else (i+1)*per_process
        index_list.append(list(range(i*per_process, end_index)))
    return index_list