#include "Astar.hpp"
#include "Viz.hpp"
#include <algorithm>

#define BIG_INT 1000000

Astar::Astar(vector<vector<int>> & m_map)
    :tmp_dirmap(m_map.size(), vector<char>(m_map[0].size(), 0)),
    gval_map(m_map.size(), vector<int>(m_map[0].size(), 1000000))
{
    this->pmap = m_map; //is this a copy or ref? 应该是复制
    this->pmap_i_max = m_map.size() - 1;
    this->pmap_j_max = m_map[0].size() - 1;
    // DBG(" i_max:"<<pmap_i_max<<" j_max:"<<pmap_j_max);
}



void Astar::find_path(int start_i, int start_j, int end_i, int end_j, vector<char>& path_dir){
    //初始化
    for(auto & r : tmp_dirmap)
        for(auto & e : r) e = 0;
    for(auto & r : gval_map)
        for(auto & e : r) e = BIG_INT;
    gval_map[start_i][start_j] = 0;
    for(auto & r : pmap)
        for(auto & e : r) if(e == -1) e = 0;
    tmp_target_i = end_i;
    tmp_target_j = end_j;
    //初始化起点
    span_pos(start_i, start_j);
    //如果起点和终点相同，未处理
    assert(!(start_i == end_i && start_j == end_j));
    while(!search_queue.empty()){
        int hval, cur_i, cur_j;
        std::tie(hval, cur_i, cur_j) 
            = this->search_queue.top();
        search_queue.pop();
        // DBG("pop. hval: "<<hval<<" ci:"<<cur_i<<" cj:"<<cur_j);
        // Viz::show_dirmap(this->pmap, this->tmp_dirmap);
        
        span_pos(cur_i, cur_j);
        if(cur_i == tmp_target_i && cur_j == tmp_target_j) break;
    }
    DBGE(Viz::show_dirmap(this->pmap, this->tmp_dirmap););
    
    //写回路径
    int back_i = end_i, back_j = end_j;
    path_dir.clear();
    while(!(back_i == start_i && back_j == start_j)){
        char dir = tmp_dirmap[back_i][back_j];
        path_dir.push_back(dir);
        if(dir == 'U') back_i++;
        else if(dir == 'D') back_i--;
        else if(dir == 'L') back_j++;
        else if(dir == 'R') back_j--;
        else assert(false);
    }
    std::reverse(path_dir.begin(), path_dir.end());
}


bool Astar::span_pos(int posi, int posj){
    // DBG("ENTER_SPAN: " << " pi:"<<posi<<" pj:"<<posj);
    if(pmap[posi][posj] == -1) return false; //防止重复展开
    pmap[posi][posj] = -1;
    bool pos_find = false;
    int i4[] = {-1, +1, 0, 0};
    int j4[] = {0, 0, -1, +1};
    char d4[] = {'U', 'D', 'L', 'R'};
    int i,j;
    for(int k=0; k<4; k++){
        i = min(pmap_i_max, max(0, posi+i4[k])); 
        j = min(pmap_j_max, max(0, posj+j4[k])); 
        if(pmap[i][j] == 0){
            assert(!(i == posi && j == posj));//正常情况下，不会展开pos点
            pos_find = true;
            int hf = heuristic_f(i, j, tmp_target_i, tmp_target_j);
            int gf = gval_map[posi][posj] + 1;
            int ff = gf + hf;
            int old_ff = gval_map[i][j] + hf;
            
            //如果更优，才更新gval值，Push到队列，设置前驱
            if(ff < old_ff){
                gval_map[i][j] = gf;
                this->search_queue.push(make_tuple(-ff, i, j));
                this->tmp_dirmap[i][j] = d4[k];
            }   
            
            // DBG("push: "<<-hf-gf << " i:"<<i<<" j:"<<j);
        }
    }
    return pos_find;
}

int Astar::heuristic_f(int current_i, int current_j, int target_i, int target_j){
    return (target_i - current_i) + (target_j - current_j);
}