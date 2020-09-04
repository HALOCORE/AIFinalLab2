#pragma once
#include "include_all.hpp"
#include<queue>
using namespace std;

typedef int T_FVAL;
typedef tuple<T_FVAL, int, int> T_PSTATUS;

class Astar{
public:
    Astar(vector<vector<int>> & m_map);
    void find_path(int start_i, int start_j, int end_i, int end_j, vector<char>& path_dir);

private:
    int pmap_i_max, pmap_j_max;
    int tmp_target_i, tmp_target_j;
    vector<vector<char>> tmp_dirmap;
    vector<vector<int>> gval_map;
    vector<vector<int>> pmap;
    priority_queue<T_PSTATUS> search_queue;
    
    int heuristic_f(int current_i, int current_j, int target_i, int target_j);
    bool span_pos(int posi, int posj);
};