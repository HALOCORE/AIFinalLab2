#pragma once
#include "include_all.hpp"
#include<queue>
using namespace std;


class IDAstar{
public:
    IDAstar(vector<vector<int>> & m_map);
    void find_path(int start_i, int start_j, int end_i, int end_j, vector<char>& path_dir);

private:
    int pmap_i_max, pmap_j_max;
    int tmp_target_i, tmp_target_j;
    vector<vector<char>> tmp_dirmap;
    vector<vector<int>> pmap;
    vector<char> dir_stack;
    int heuristic_f(int current_i, int current_j, int target_i, int target_j);
    bool path_dfs(int cur_i, int cur_j, int gval, int limit_f);
    
    vector<vector<int>> gval_map;//性能优化用

    vector<int> dfs_depth_count; //性能统计用
    int dfs_count;//性能统计用
};